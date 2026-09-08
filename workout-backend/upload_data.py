import firebase_admin
from firebase_admin import credentials, firestore

# 1. Firebase 인증 키 로드
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. ChatGPT에서 작성한 100개 운동 기록 데이터
workout_data = [
    {"date":"2024-05-01","value":60,"memo":"상체 웨이트"},
    {"date":"2024-05-02","value":45,"memo":"러닝"},
    {"date":"2024-05-03","value":75,"memo":"하체 및 유산소"},
    {"date":"2024-05-04","value":40,"memo":"가벼운 스트레칭"},
    {"date":"2024-05-05","value":90,"memo":"전신 웨이트"},
    {"date":"2024-05-06","value":50,"memo":"러닝"},
    {"date":"2024-05-07","value":30,"memo":"휴식"},
    {"date":"2024-05-08","value":65,"memo":"상체 웨이트"},
    {"date":"2024-05-09","value":80,"memo":"하체 및 유산소"},
    {"date":"2024-05-10","value":45,"memo":"러닝"},
    {"date":"2024-05-11","value":70,"memo":"전신 웨이트"},
    {"date":"2024-05-12","value":35,"memo":"스트레칭 및 코어"},
    {"date":"2024-05-13","value":60,"memo":"상체 웨이트"},
    {"date":"2024-05-14","value":90,"memo":"하체 및 유산소"},
    {"date":"2024-05-15","value":50,"memo":"러닝"},
    {"date":"2024-05-16","value":30,"memo":"휴식"},
    {"date":"2024-05-17","value":75,"memo":"전신 웨이트"},
    {"date":"2024-05-18","value":55,"memo":"러닝"},
    {"date":"2024-05-19","value":65,"memo":"상체 웨이트"},
    {"date":"2024-05-20","value":85,"memo":"하체 및 유산소"},
    {"date":"2024-05-21","value":40,"memo":"가벼운 스트레칭"},
    {"date":"2024-05-22","value":70,"memo":"전신 웨이트"},
    {"date":"2024-05-23","value":45,"memo":"러닝"},
    {"date":"2024-05-24","value":60,"memo":"상체 웨이트"},
    {"date":"2024-05-25","value":100,"memo":"하체 및 유산소"},
    {"date":"2024-05-26","value":35,"memo":"휴식"},
    {"date":"2024-05-27","value":80,"memo":"전신 웨이트"},
    {"date":"2024-05-28","value":50,"memo":"러닝"},
    {"date":"2024-05-29","value":65,"memo":"상체 웨이트"},
    {"date":"2024-05-30","value":75,"memo":"하체 및 유산소"},
    {"date":"2024-05-31","value":45,"memo":"코어 및 스트레칭"},
    {"date":"2024-06-01","value":90,"memo":"전신 웨이트"},
    {"date":"2024-06-02","value":50,"memo":"러닝"},
    {"date":"2024-06-03","value":60,"memo":"상체 웨이트"},
    {"date":"2024-06-04","value":80,"memo":"하체 및 유산소"},
    {"date":"2024-06-05","value":35,"memo":"휴식"},
    {"date":"2024-06-06","value":70,"memo":"전신 웨이트"},
    {"date":"2024-06-07","value":55,"memo":"러닝"},
    {"date":"2024-06-08","value":65,"memo":"상체 웨이트"},
    {"date":"2024-06-09","value":85,"memo":"하체 및 유산소"},
    {"date":"2024-06-10","value":40,"memo":"스트레칭"},
    {"date":"2024-06-11","value":75,"memo":"전신 웨이트"},
    {"date":"2024-06-12","value":45,"memo":"러닝"},
    {"date":"2024-06-13","value":60,"memo":"상체 웨이트"},
    {"date":"2024-06-14","value":95,"memo":"하체 및 유산소"},
    {"date":"2024-06-15","value":30,"memo":"휴식"},
    {"date":"2024-06-16","value":70,"memo":"전신 웨이트"},
    {"date":"2024-06-17","value":50,"memo":"러닝"},
    {"date":"2024-06-18","value":65,"memo":"상체 웨이트"},
    {"date":"2024-06-19","value":80,"memo":"하체 및 유산소"},
    {"date":"2024-06-20","value":40,"memo":"코어 운동"},
    {"date":"2024-06-21","value":85,"memo":"전신 웨이트"},
    {"date":"2024-06-22","value":55,"memo":"러닝"},
    {"date":"2024-06-23","value":60,"memo":"상체 웨이트"},
    {"date":"2024-06-24","value":90,"memo":"하체 및 유산소"},
    {"date":"2024-06-25","value":35,"memo":"휴식"},
    {"date":"2024-06-26","value":75,"memo":"전신 웨이트"},
    {"date":"2024-06-27","value":45,"memo":"러닝"},
    {"date":"2024-06-28","value":70,"memo":"상체 웨이트"},
    {"date":"2024-06-29","value":100,"memo":"하체 및 유산소"},
    {"date":"2024-06-30","value":50,"memo":"가벼운 유산소"},
    {"date":"2024-07-01","value":80,"memo":"전신 웨이트"},
    {"date":"2024-07-02","value":45,"memo":"러닝"},
    {"date":"2024-07-03","value":65,"memo":"상체 웨이트"},
    {"date":"2024-07-04","value":90,"memo":"하체 및 유산소"},
    {"date":"2024-07-05","value":35,"memo":"휴식"},
    {"date":"2024-07-06","value":75,"memo":"전신 웨이트"},
    {"date":"2024-07-07","value":55,"memo":"러닝"},
    {"date":"2024-07-08","value":60,"memo":"상체 웨이트"},
    {"date":"2024-07-09","value":85,"memo":"하체 및 유산소"},
    {"date":"2024-07-10","value":40,"memo":"스트레칭 및 코어"},
    {"date":"2024-07-11","value":90,"memo":"전신 웨이트"},
    {"date":"2024-07-12","value":50,"memo":"러닝"},
    {"date":"2024-07-13","value":70,"memo":"상체 웨이트"},
    {"date":"2024-07-14","value":95,"memo":"하체 및 유산소"},
    {"date":"2024-07-15","value":30,"memo":"휴식"},
    {"date":"2024-07-16","value":80,"memo":"전신 웨이트"},
    {"date":"2024-07-17","value":45,"memo":"러닝"},
    {"date":"2024-07-18","value":65,"memo":"상체 웨이트"},
    {"date":"2024-07-19","value":85,"memo":"하체 및 유산소"},
    {"date":"2024-07-20","value":40,"memo":"가벼운 스트레칭"},
    {"date":"2024-07-21","value":75,"memo":"전신 웨이트"},
    {"date":"2024-07-22","value":55,"memo":"러닝"},
    {"date":"2024-07-23","value":60,"memo":"상체 웨이트"},
    {"date":"2024-07-24","value":100,"memo":"하체 및 유산소"},
    {"date":"2024-07-25","value":35,"memo":"휴식"},
    {"date":"2024-07-26","value":85,"memo":"전신 웨이트"},
    {"date":"2024-07-27","value":50,"memo":"러닝"},
    {"date":"2024-07-28","value":70,"memo":"상체 웨이트"},
    {"date":"2024-07-29","value":90,"memo":"하체 및 유산소"},
    {"date":"2024-07-30","value":45,"memo":"코어 운동"},
    {"date":"2024-07-31","value":80,"memo":"전신 웨이트"},
    {"date":"2024-08-01","value":55,"memo":"러닝"},
    {"date":"2024-08-02","value":65,"memo":"상체 웨이트"},
    {"date":"2024-08-03","value":95,"memo":"하체 및 유산소"},
    {"date":"2024-08-04","value":30,"memo":"휴식"},
    {"date":"2024-08-05","value":75,"memo":"전신 웨이트"},
    {"date":"2024-08-06","value":50,"memo":"러닝"},
    {"date":"2024-08-07","value":70,"memo":"상체 웨이트"},
    {"date":"2024-08-08","value":85,"memo":"하체 및 유산소"}
]

# 3. Firestore 'exercise_data' 컬렉션에 업로드
def upload():
    collection_ref = db.collection("exercise_data")
    count = 0
    for item in workout_data:
        collection_ref.add(item)
        count += 1
        print(f"[{count}/100] {item['date']} 업로드 완료")
    print("🎉 모든 데이터가 Firestore에 성공적으로 입력되었습니다!")

if __name__ == "__main__":
    upload()