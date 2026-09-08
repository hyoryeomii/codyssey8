import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from openai import OpenAI

load_dotenv()

app = FastAPI(title="Daily Workout AI Assistant")

# 1. CORS 설정 (환경 변수 적용)
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Firebase 및 OpenAI 초기화 (Render 배포 대응)
if not firebase_admin._apps:
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

    if service_account_json:
        # Render 등 클라우드 배포 시 JSON 문자열 환경변수 사용
        cred_dict = json.loads(service_account_json)
        cred = credentials.Certificate(cred_dict)
    elif os.path.exists(service_account_path):
        # 로컬 환경 키 파일 사용
        cred = credentials.Certificate(service_account_path)
    else:
        raise RuntimeError("Firebase 서비스 계정 인증 정보를 찾을 수 없습니다.")
        
    firebase_admin.initialize_app(cred)

db = firestore.client()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pydantic 모델 정의
class DataItem(BaseModel):
    date: str
    value: int
    memo: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ConversationCreate(BaseModel):
    user_message: str
    ai_response: str

# ==========================================
# 1. 데이터 CRUD & Summary API
# ==========================================

@app.get("/api/data")
def get_data():
    docs = db.collection("exercise_data").order_by("date").stream()
    result = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        result.append(d)
    return result

@app.post("/api/data")
def create_data(item: DataItem):
    doc_ref = db.collection("exercise_data").add(item.model_dump())
    return {"id": doc_ref[1].id, **item.model_dump()}

@app.put("/api/data/{id}")
def update_data(id: str, item: DataItem):
    db.collection("exercise_data").document(id).update(item.model_dump())
    return {"id": id, **item.model_dump()}

@app.delete("/api/data/{id}")
def delete_data(id: str):
    db.collection("exercise_data").document(id).delete()
    return {"message": "deleted", "id": id}

@app.get("/api/data/summary")
def get_data_summary():
    docs = list(db.collection("exercise_data").order_by("date").stream())
    if not docs:
        return {
            "period": "데이터 없음",
            "count": 0,
            "metrics": {
                "total_minutes": 0,
                "average_minutes": 0,
                "max_minutes": 0,
                "min_minutes": 0
            },
            "trend": "데이터 없음"
        }
    
    data_list = [d.to_dict() for d in docs]
    values = [d["value"] for d in data_list]
    
    avg_val = round(sum(values) / len(values), 1)
    max_val = max(values)
    min_val = min(values)
    
    recent_avg = sum(values[-10:]) / min(10, len(values))
    trend = "증가 추세" if recent_avg > avg_val else ("유지 추세" if recent_avg == avg_val else "감소 추세")
    
    return {
        "period": f"{data_list[0]['date']} ~ {data_list[-1]['date']}",
        "count": len(values),
        "metrics": {
            "total_minutes": sum(values),
            "average_minutes": avg_val,
            "max_minutes": max_val,
            "min_minutes": min_val
        },
        "trend": trend
    }

# ==========================================
# 2. AI 챗봇 API (컨텍스트 주입)
# ==========================================

@app.post("/api/chat")
def chat(req: ChatRequest):
    summary = get_data_summary()
    
    system_prompt = f"""
    당신은 사용자의 개인 운동 기록을 분석하고 조언해 주는 1:1 맞춤형 AI 피트니스 트레이너입니다.
    아래의 [사용자 운동 데이터 요약]을 바탕으로 사용자의 질문에 맞춰 친절하고 전문적으로 답변해 주세요.

    [사용자 운동 데이터 요약]
    - 조회 기간: {summary['period']}
    - 총 기록 일수: {summary['count']}일
    - 총 운동 시간: {summary['metrics']['total_minutes']}분
    - 일평균 운동 시간: {summary['metrics']['average_minutes']}분
    - 최고 운동 시간: {summary['metrics']['max_minutes']}분
    - 최저 운동 시간: {summary['metrics']['min_minutes']}분
    - 최근 트렌드: {summary['trend']}
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": req.message}
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    ai_reply = response.choices[0].message.content
    
    conv_ref = db.collection("conversations").add({
        "user_message": req.message,
        "ai_response": ai_reply,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    
    return {
        "conversation_id": conv_ref[1].id,
        "response": ai_reply
    }

# ==========================================
# 3. 대화 기록 API (추가 보완 완료)
# ==========================================

@app.post("/api/conversations")
def create_conversation(conv: ConversationCreate):
    conv_ref = db.collection("conversations").add({
        "user_message": conv.user_message,
        "ai_response": conv.ai_response,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    return {"id": conv_ref[1].id, **conv.model_dump()}

@app.get("/api/conversations")
def get_conversations():
    docs = db.collection("conversations").order_by("created_at", direction=firestore.Query.DESCENDING).stream()
    result = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        if "created_at" in d and d["created_at"]:
            d["created_at"] = str(d["created_at"])
        result.append(d)
    return result

@app.get("/api/conversations/{id}")
def get_conversation_detail(id: str):
    doc = db.collection("conversations").document(id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="대화 기록을 찾을 수 없습니다.")
    
    data = doc.to_dict()
    data["id"] = doc.id
    if "created_at" in data and data["created_at"]:
        data["created_at"] = str(data["created_at"])
        
    data["messages"] = [
        {"role": "user", "content": data.get("user_message", "")},
        {"role": "assistant", "content": data.get("ai_response", "")}
    ]
    return data

@app.delete("/api/conversations/{id}")
def delete_conversation(id: str):
    db.collection("conversations").document(id).delete()
    return {"message": "deleted", "id": id}