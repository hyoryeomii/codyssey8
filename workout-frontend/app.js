const API_BASE_URL = 'http://127.0.0.1:8000'; // 배포 후 Render URL로 교체 예정

document.addEventListener('DOMContentLoaded', () => {
  loadSummary();
  loadDataList();
  loadConversations();

  document.getElementById('chat-form').addEventListener('submit', handleChatSubmit);
  document.getElementById('data-form').addEventListener('submit', handleDataSubmit);
  document.getElementById('form-cancel-btn').addEventListener('click', resetDataForm);
});

// 1. 데이터 요약 불러오기
async function loadSummary() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data/summary`);
    const data = await res.json();
    const container = document.getElementById('summary-content');

    if (res.status === 404 || !data.count) {
      container.innerHTML = '<p>등록된 데이터가 없습니다.</p>';
      return;
    }

    container.innerHTML = `
      <p><strong>기간:</strong> ${data.period}</p>
      <p><strong>기록 일수:</strong> ${data.count}일</p>
      <p><strong>총 시간:</strong> ${data.metrics.total_minutes}분</p>
      <p><strong>일평균:</strong> ${data.metrics.average_minutes}분</p>
      <p><strong>최고:</strong> ${data.metrics.max_minutes}분 | <strong>최저:</strong> ${data.metrics.min_minutes}분</p>
      <p><strong>트렌드:</strong> ${data.trend}</p>
    `;
  } catch (err) {
    console.error('요약 조회 실패:', err);
  }
}

// 2. 운동 데이터 CRUD 목록 불러오기
async function loadDataList() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/data`);
    const list = await res.json();
    const tbody = document.getElementById('data-list');
    tbody.innerHTML = '';

    list.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.date}</td>
        <td>${item.value}</td>
        <td>${item.memo}</td>
        <td>
          <button class="btn-sm btn-edit" onclick="setEditForm('${item.id}', '${item.date}', ${item.value}, '${item.memo}')">수정</button>
          <button class="btn-sm btn-delete" onclick="deleteData('${item.id}')">삭제</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('데이터 조회 실패:', err);
  }
}

// 데이터 추가/수정 제출
async function handleDataSubmit(e) {
  e.preventDefault();
  const id = document.getElementById('data-id').value;
  const date = document.getElementById('data-date').value;
  const value = parseInt(document.getElementById('data-value').value);
  const memo = document.getElementById('data-memo').value;

  const payload = { date, value, memo };
  const method = id ? 'PUT' : 'POST';
  const url = id ? `${API_BASE_URL}/api/data/${id}` : `${API_BASE_URL}/api/data`;

  await fetch(url, {
    method: method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  resetDataForm();
  loadDataList();
  loadSummary();
}

function setEditForm(id, date, value, memo) {
  document.getElementById('data-id').value = id;
  document.getElementById('data-date').value = date;
  document.getElementById('data-value').value = value;
  document.getElementById('data-memo').value = memo;
  document.getElementById('form-submit-btn').innerText = '데이터 수정';
  document.getElementById('form-cancel-btn').classList.remove('hidden');
}

function resetDataForm() {
  document.getElementById('data-id').value = '';
  document.getElementById('data-date').value = '';
  document.getElementById('data-value').value = '';
  document.getElementById('data-memo').value = '';
  document.getElementById('form-submit-btn').innerText = '데이터 추가';
  document.getElementById('form-cancel-btn').classList.add('hidden');
}

async function deleteData(id) {
  if (!confirm('삭제하시겠습니까?')) return;
  await fetch(`${API_BASE_URL}/api/data/${id}`, { method: 'DELETE' });
  loadDataList();
  loadSummary();
}

// 3. AI 챗봇 연동
async function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  if (!message) return;

  appendMessage('user', message);
  input.value = '';
  document.getElementById('loading').classList.remove('hidden');

  try {
    const res = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    appendMessage('ai', data.response);
    loadConversations(); // 신규 대화 기록 업데이트
  } catch (err) {
    appendMessage('ai', '오류가 발생했습니다. 다시 시도해주세요.');
  } finally {
    document.getElementById('loading').classList.add('hidden');
  }
}

function appendMessage(sender, text) {
  const chatBox = document.getElementById('chat-box');
  const div = document.createElement('div');
  div.className = `message ${sender === 'user' ? 'user-message' : 'ai-message'}`;
  div.innerText = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// 4. 대화 기록 연동
async function loadConversations() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations`);
    const list = await res.json();
    const ul = document.getElementById('history-list');
    ul.innerHTML = '';

    list.forEach(item => {
      const li = document.createElement('li');
      li.innerHTML = `
        <span>${item.user_message.substring(0, 18)}...</span>
        <button class="btn-sm btn-delete" onclick="event.stopPropagation(); deleteConv('${item.id}')">삭제</button>
      `;
      li.onclick = () => loadConvDetail(item.id);
      ul.appendChild(li);
    });
  } catch (err) {
    console.error('대화 기록 조회 실패:', err);
  }
}

async function loadConvDetail(id) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/conversations/${id}`);
    const data = await res.json();
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = '';

    data.messages.forEach(msg => {
      appendMessage(msg.role === 'user' ? 'user' : 'ai', msg.content);
    });
  } catch (err) {
    console.error('대화 상세 불러오기 실패:', err);
  }
}

async function deleteConv(id) {
  if (!confirm('대화 기록을 삭제하시겠습니까?')) return;
  await fetch(`${API_BASE_URL}/api/conversations/${id}`, { method: 'DELETE' });
  loadConversations();
}