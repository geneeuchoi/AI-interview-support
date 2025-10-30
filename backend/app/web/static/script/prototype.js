const fullStartBtn = document.getElementById("fullStartBtn");
const fullStopBtn = document.getElementById("fullStopBtn");
const partStartBtn = document.getElementById("partStartBtn");
const partStopBtn = document.getElementById("partStopBtn");

const sttResultBox = document.getElementById("sttResult");
const llmAnswerResultBox = document.getElementById("llmAnswerResult");
const llmSummaryResultBox = document.getElementById("llmSummaryResult");
const emailSendResultBox = document.getElementById("emailSendResult");

const audioPlayer = document.getElementById("audioPlayer");

const fmt = pickAudioFormat();
// TODO: 배포시 도메인 수정
const baseUrl = "http://localhost:8000";
let masterStream = null;

const full = {
  recorder: null,
  chunks: [],
  running: false
};

const part = {
  recorder: null,
  chunks: [],
  running: false,
  stream: null // clone stream
};

// ---------- 이벤트 바인딩 ----------
fullStartBtn.addEventListener("click", startFullRecording);
fullStopBtn.addEventListener("click", stopFullRecording);
partStartBtn.addEventListener("click", startPartRecording);
partStopBtn.addEventListener("click", stopPartRecording);

// ---------- 녹음 권한 및 오디오 포맷 설정 ----------
// 마이크 권한 확인
async function ensureMasterStream() {
  if (!masterStream) {
    masterStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  }
}

// 브라우저 지원 오디오 포맷 설정
function pickAudioFormat() {
  // mime: Multipurpose Internet Mail Extensions
  // e.g 'audio/webm;codecs=opus'
  // 오디오(audio) 파일이고, WebM 형식이며, Opus 코덱으로 압축
  const cands = [
    { mime: 'audio/webm;codecs=opus', ext: 'webm' },
    { mime: 'audio/mp4;codecs=mp4a.40.2', ext: 'm4a' },
    { mime: 'audio/ogg;codecs=opus', ext: 'ogg' },
  ];
  for (const c of cands) {
    if (MediaRecorder.isTypeSupported?.(c.mime)) return c;
  }
  return { mime: '', ext: 'wav' };
}

// ---------- 전체 녹음 ----------
async function startFullRecording() {
  try {
    await ensureMasterStream();
    full.chunks = [];
    full.recorder = new MediaRecorder(masterStream, fmt.mime ? { mimeType: fmt.mime } : {});
    // e.data: 오디오 데이터 조각
    // 옵셔널 체이닝: e.data && e.data.size
    full.recorder.ondataavailable = (e) => { if (e.data?.size) full.chunks.push(e.data); };
    full.recorder.onstop = async () => {
      // Binary Large Object (BLOB): 데이터베이스나 클라우드 스토리지에서 텍스트, 이미지, 비디오 등과 같이 정해진 형식이 없는 대규모의 비정형 데이터를 저장하기 위한 데이터 타입
      const blob = new Blob(full.chunks, { type: fmt.mime || 'audio/wav' });
      const file = new File([blob], `full.${fmt.ext || 'wav'}`, { type: blob.type });
      audioPlayer.src = URL.createObjectURL(blob);

      // STT -> LLM 전송
      try {
        const text = await sendAudioToServer(file);
        await llmSummary(text);
      } catch (e) {
        console.error(e);
      } finally {
        full.running = false; // 녹음 중지
        if (!part.running) {
          // 부분 녹음이 진행 중이지 않다면 마스터 녹음 객체 초기화
          masterStream.getTracks().forEach(t => t.stop());
          masterStream = null;
        }
      }
    };
    full.recorder.start();
    full.running = true;

    fullStartBtn.disabled = true;
    fullStopBtn.disabled = false;
  } catch (err) {
    alert("마이크 접근 실패: " + err.message);
  }
}

function stopFullRecording() {
  if (full.recorder && full.recorder.state === "recording") {
    full.recorder.stop();
  }
  fullStartBtn.disabled = false;
  fullStopBtn.disabled = true;
}

// ---------- 부분 녹음 ----------
async function startPartRecording() {
  try {
    // 마이크 권한 확인
    await ensureMasterStream();
    part.chunks = [];

    // master의 트랙을 clone해서 별도 스트림 생성
    // 스트림 안에 트랙이 있음. 트랙을 꺼내서 클론한 후 새로운 스트림 생성
    // 즉 마스터 트랙 1 -> 마스터 스트림
    // 클론된 마스터 트랙 1 -> 부분 스트림
    part.stream = new MediaStream(masterStream.getAudioTracks().map(t => t.clone()));
    part.recorder = new MediaRecorder(part.stream, fmt.mime ? { mimeType: fmt.mime } : {});
    part.recorder.ondataavailable = (e) => { if (e.data?.size) part.chunks.push(e.data); };
    part.recorder.onstop = async () => {
      const blob = new Blob(part.chunks, { type: fmt.mime || 'audio/wav' });
      const file = new File([blob], `part.${fmt.ext || 'wav'}`, { type: blob.type });
      audioPlayer.src = URL.createObjectURL(blob);

      try {
        const text = await sendAudioToServer(file);
        sttResultBox.value = text || "";
        await llmAnswer(text);
      } catch (e) {
        console.error(e);
      } finally {
        // part 전용 트랙 정리
        part.stream.getTracks().forEach(t => t.stop());
        part.stream = null;
        part.running = false;

        // 만약 전체도 안 돌고 있으면 master 정리
        if (!full.running && masterStream) {
          masterStream.getTracks().forEach(t => t.stop());
          masterStream = null;
        }
      }
    };

    part.recorder.start();
    part.running = true;

    partStartBtn.disabled = true;
    partStopBtn.disabled = false;
    sttResultBox.value = "녹음 중...";
  } catch (err) {
    alert("마이크 접근 실패: " + err.message);
  }
}

function stopPartRecording() {
  if (part.recorder && part.recorder.state === "recording") {
    part.recorder.stop();
  }
  partStartBtn.disabled = false;
  partStopBtn.disabled = true;
}

// ---------- STT ----------
// 녹음본 STT 서버 전송
async function sendAudioToServer(file) {
  const url = `${baseUrl}/api/stt`;
  const formData = new FormData();
  formData.append("audio", file);

  try {
    const res = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const errDetail = await res.json().catch(() => ({}));
      throw new Error(`HTTP ${res.status} ${JSON.stringify(errDetail)}`);
    }

    const data = await res.json();
    return data.text || "";
  } catch (err) {
    console.error("STT Error:", err);
    throw err;
  }
}

// ---------- LLM ----------
// 부분 녹음(실시간 대응) 답변
async function llmAnswer(text) {
  const url = `${baseUrl}/api/llm/answer`;
  const startTime = performance.now();

  const body = {
    text,
    model: "gpt-4o-mini",
    language: "ja"
  };

  llmAnswerResultBox.value = "서버로 전송 중...";

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      let errDetail = {};
      try {
        errDetail = await res.json();
      } catch {
        try {
          const t = await res.text();
          errDetail = { message: t.slice(0, 200) };
        } catch {}
      }
      throw new Error(`HTTP ${res.status} ${JSON.stringify(errDetail)}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let done = false;
    llmAnswerResultBox.value = "";
    while (!done) {
      const { value, done: streamDone } = await reader.read();
      done = streamDone;
      if (value) {
        const chunkText = decoder.decode(value, { stream: true });
        llmAnswerResultBox.value += chunkText;
      }
    }
    llmAnswerResultBox.value += decoder.decode();
  } catch (err) {
    llmAnswerResultBox.value = err.message;
  }
}

// 전체 녹음(면접 요약) 답변
async function llmSummary(text) {
  const url = `${baseUrl}/api/llm/summary`;

  const body = {
    text,
    model: "gpt-4o-mini",
    language: "ja"
  };

  llmSummaryResultBox.value = "서버로 전송 중...";

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {"Content-Type": "application/json; charset=utf-8"},
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const errDetail = await res.json().catch(() => ({}));
      throw new Error(`HTTP ${res.status} ${JSON.stringify(errDetail)}`);
    }

    const data = await res.json();
    llmSummaryResultBox.value = `${data.text}`;
    await sendSummary(data.text)
  } catch (err) {
    llmSummaryResultBox.value = err.message;
  }
}

// ---------- 이메일 전송 ----------
async function sendSummary(summary) {
  const url = `${baseUrl}/api/email`;

  const body = {
    summary
  };

  emailSendResultBox.value = "서버로 전송 중...";

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {"Content-Type": "application/json; charset=utf-8"},
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const errDetail = await res.json().catch(() => ({}));
      throw new Error(`HTTP ${res.status} ${JSON.stringify(errDetail)}`);
    }

    emailSendResultBox.value = "전송이 완료되었습니다!";
  } catch (err) {
    emailSendResultBox.value = err.message;
  }
}