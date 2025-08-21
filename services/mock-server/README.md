# Mock Server

Fire IoT 시스템을 위한 Mock Server입니다.

## 🚀 기능

- **실시간 데이터 생성**: Datalake 연동을 위한 가짜 실시간 데이터 생성

## 🌐 API 엔드포인트

### 기본 URL

- **애플리케이션**: http://localhost:8001
- **Swagger UI**: http://localhost:8001/swagger-ui.html

### REST API 경로

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
웹소켓을 통해 실시간으로 동영상 스트리밍 데이터를 전송
- 브로드캐스트 가능
- mock-server를 실행하면 웹소켓 열림

### WebSocket 엔드포인트
- **WebSocket 연결**: `/cctv-websocket`
- **스트림 구독**: `/topic/cctv-stream`

### 스트리밍 활용 예시
- resources > static > cctv-player.html 그리고  multi-socket-test.html참고


### REST API 엔드포인트
- **사용 가능한 비디오 목록**: `GET /api/cctv/videos`
- **스트리밍 시작**: `POST /api/cctv/stream/start`
- **스트리밍 중지**: `POST /api/cctv/stream/stop`
- **스트리밍 상태 확인**: `GET /api/cctv/stream/status`
