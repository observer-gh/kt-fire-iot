# Mock Server

Fire IoT 시스템을 위한 Mock Server입니다.

## 주요 기능

### 1. CCTV 스트리밍 서비스
- **무한 루프 스트리밍**: CCTV 폴더의 4개 샘플 영상을 순차적으로 재생
- **웹소켓 브로드캐스트**: 연결된 모든 클라이언트에게 실시간 영상 전송
- **자동 재시작**: 마지막 영상 종료 시 첫 번째 영상으로 자동 전환

### 2. 스트리밍 특징
- **프레임 레이트**: 15 FPS로 제한하여 네트워크 부하 최소화
- **Base64 인코딩**: JPEG 이미지로 변환하여 웹소켓으로 전송
- **실시간 동기화**: 모든 클라이언트가 동일한 시점의 영상 시청

## API 엔드포인트

### CCTV 스트리밍 API
- `POST /api/cctv/start` - 스트리밍 시작
- `POST /api/cctv/stop` - 스트리밍 중지
- `GET /api/cctv/status` - 스트리밍 상태 조회
- `GET /api/cctv/videos` - 비디오 파일 목록 조회

### WebSocket 엔드포인트
- `/cctv-websocket` - CCTV 스트리밍용 WebSocket 연결
- `/topic/cctv-stream` - 비디오 프레임 스트림

## 사용 방법

### 1. 서버 실행
```bash
mvn spring-boot:run
```

### 2. 웹 플레이어 접속
```
http://localhost:8001/cctv-player.html
```

### 3. 스트리밍 시작
- 웹 플레이어에서 "스트리밍 시작" 버튼 클릭
- 자동으로 CCTV 폴더의 영상들이 순차적으로 재생됨

## 기술 스택

- **Spring Boot 3.2.0**: 백엔드 프레임워크
- **WebSocket**: 실시간 양방향 통신
- **JavaCV**: 비디오 프레임 추출 및 처리
- **STOMP**: WebSocket 메시징 프로토콜

## 파일 구조

```
services/mock-server/
├── cctv/                    # CCTV 샘플 영상 파일들
│   ├── sample1.mp4
│   ├── sample2.mp4
│   ├── sample3.mp4
│   └── sample4.mp4
├── src/main/java/
│   └── com/fireiot/mockserver/
│       ├── config/
│       │   └── WebSocketConfig.java      # WebSocket 설정
│       ├── controller/
│       │   └── CCTVController.java       # CCTV API 컨트롤러
│       ├── service/
│       │   └── CCTVStreamingService.java # CCTV 스트리밍 서비스
│       └── MockServerApplication.java    # 메인 애플리케이션
└── src/main/resources/
    └── static/
        └── cctv-player.html              # 웹 플레이어
```

## 설정

### WebSocket 설정
- **엔드포인트**: `/cctv-websocket`
- **메시지 브로커**: `/topic`
- **애플리케이션 프리픽스**: `/app`

### 스트리밍 설정
- **프레임 레이트**: 15 FPS
- **이미지 포맷**: JPEG
- **인코딩**: Base64

## 모니터링

### 로그 확인
- 스트리밍 시작/중지 로그
- 비디오 전환 알림
- 에러 발생 시 상세 로그

### 상태 모니터링
- 현재 재생 중인 비디오
- 연결된 클라이언트 수
- 프레임 전송 통계
