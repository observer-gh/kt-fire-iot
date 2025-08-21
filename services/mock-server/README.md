# Mock Server

Fire IoT 시스템을 위한 Mock Server입니다.

## 🚀 기능

- **실시간 데이터 생성**: Datalake 연동을 위한 가짜 실시간 데이터 생성

## 🌐 API 엔드포인트

### 기본 URL

- **애플리케이션**: http://localhost:8001
- **Swagger UI**: http://localhost:8001/swagger-ui.html

### API 경로

- **시설**: `/mock/facility`
- **장비**: `/mock/equipment`
- **사고**: `/mock/incident`
- **유지보수**: `/mock/equipment-maintenance`
- **실시간 데이터**: `/mock/realtime`
- **실시간 데이터 생성**: `/mock/realtime-generator` (Datalake 연동용)
- **분석**: `/mock/analysis`
- **알림**: `/mock/alert`
- **CCTV 스트리밍**: `/api/cctv/*`

## 📹 CCTV 스트리밍 기능

### 통신 흐름
```
클라이언트 ←→ 서버
    ↓
1. WebSocket 연결: /cctv-websocket
    ↓
2. 클라이언트 → 서버: /app/cctv/control
    ↓
3. 서버 → 클라이언트: /topic/cctv-stream
```

### WebSocket 엔드포인트
- **WebSocket 연결**: `/cctv-websocket`
- **스트림 구독**: `/topic/cctv-stream`
- **제어 메시지**: `/app/cctv/control`

### 스트림 시작/종료 트리거 데이터 형식
- 현재 videoFileName은 `sample1.mp4`, `sample2.mp4`만 존재
- resources > static > cctv-streaming.html 참고
- **스트림 시작**
{ action: 'start', videoFileName: '파일명'}
- **스트림 종료**
{ action: 'stop' }


### REST API 엔드포인트
- **사용 가능한 비디오 목록**: `GET /api/cctv/videos`
- **스트리밍 시작**: `POST /api/cctv/stream/start?videoFileName={파일명}`
- **스트리밍 중지**: `POST /api/cctv/stream/stop`
- **스트리밍 상태 확인**: `GET /api/cctv/stream/status`

### 테스트 클라이언트
- **HTML 테스트 페이지**: `http://localhost:8001/cctv-streaming.html`
