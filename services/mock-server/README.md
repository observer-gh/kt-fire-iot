# Mock Server

Fire IoT 시스템을 위한 Mock Server입니다.

## 📋 프로젝트 개요

이 프로젝트는 Fire IoT 시스템의 다양한 모듈을 시뮬레이션하는 Mock Server입니다. 기존의 시설 관리, 장비 관리, 실시간 데이터 생성 기능에 더해, **CCTV 실시간 스트리밍 기능**이 새롭게 추가되었습니다.

### 🆕 새로 추가된 기능
- **WebSocket 기반 CCTV 스트리밍**: 실시간 비디오 프레임 전송
- **JavaCV 비디오 처리**: MP4, AVI, MOV 등 다양한 형식 지원
- **실시간 스트리밍 제어**: REST API와 WebSocket을 통한 양방향 통신
- **테스트 클라이언트**: HTML 기반 스트리밍 테스트 페이지

## 🚀 기능

- **시설 관리**: 시설 정보 CRUD
- **장비 관리**: 장비 정보 및 상태 관리
- **사고 관리**: 사고 발생 및 해결 추적
- **유지보수 관리**: 장비 유지보수 일정 및 이력
- **실시간 데이터**: 센서 데이터 실시간 수집
- **실시간 데이터 생성**: Datalake 연동을 위한 가짜 실시간 데이터 생성 (90% 정상, 10% 이상)
- **분석 결과**: AI 분석 결과 관리
- **알림 시스템**: 다양한 알림 타입 및 심각도 관리
- **CCTV 스트리밍**: WebSocket 기반 실시간 비디오 스트리밍 (새로 추가됨)

## 🛠️ 기술 스택

- **Java 17**
- **Spring Boot 3.2.0**
- **Spring Data JPA**
- **Spring WebSocket**
- **JavaCV** (비디오 처리)
- **H2 Database** (로컬 개발)
- **PostgreSQL** (프로덕션)
- **OpenAPI/Swagger UI**

## 📋 요구사항

- Java 17 이상
- Maven 3.6 이상

## 🏃‍♂️ 실행 방법

### 로컬 개발 환경

```bash
# 프로젝트 디렉토리로 이동
cd services/mock-server

# 프로젝트 빌드
mvn clean compile

# 애플리케이션 실행
mvn spring-boot:run
```

**주의사항**: 
- 애플리케이션은 `services/mock-server` 디렉토리에서 실행해야 합니다
- CCTV 폴더 경로가 올바르게 설정되어야 합니다

### Docker 실행

#### 단일 컨테이너 실행

```bash
# Docker 이미지 빌드 및 실행
docker build -t mock-server .
docker run -p 8001:8001 mock-server
```

#### Docker Compose 사용 (권장)

```bash
# 애플리케이션만 실행 (H2 데이터베이스 사용)
docker-compose up -d

# PostgreSQL과 함께 실행
docker-compose --profile postgres up -d

# 로그 확인
docker-compose logs -f mock-server

# 컨테이너 중지
docker-compose down
```

## 🌐 API 엔드포인트

### 기본 URL

- **애플리케이션**: http://localhost:8001
- **Swagger UI**: http://localhost:8001/swagger-ui.html
- **H2 Console**: http://localhost:8001/h2-console

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

### WebSocket 엔드포인트
- **WebSocket 연결**: `/cctv-websocket`
- **스트림 구독**: `/topic/cctv-stream`
- **제어 메시지**: `/app/cctv/control`

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

### REST API 엔드포인트
- **사용 가능한 비디오 목록**: `GET /api/cctv/videos`
- **스트리밍 시작**: `POST /api/cctv/stream/start?videoFileName={파일명}`
- **스트리밍 중지**: `POST /api/cctv/stream/stop`
- **스트리밍 상태 확인**: `GET /api/cctv/stream/status`

### 테스트 클라이언트
- **HTML 테스트 페이지**: `http://localhost:8001/cctv-streaming.html`

### 사용 방법
1. **서버 실행**: `mvn spring-boot:run`
2. **브라우저 접속**: `http://localhost:8001/cctv-streaming.html`
3. **비디오 선택**: 드롭다운에서 sample1.mp4 또는 sample2.mp4 선택
4. **스트리밍 시작**: "스트리밍 시작" 버튼 클릭
5. **실시간 확인**: WebSocket을 통한 실시간 프레임 수신 확인
6. **스트리밍 중지**: "스트리밍 중지" 버튼으로 중지

### 테스트 시나리오
- **단일 클라이언트**: 하나의 브라우저에서 스트리밍 확인
- **다중 클라이언트**: 여러 브라우저에서 동시 스트리밍 확인
- **연결 해제/재연결**: WebSocket 연결 상태 변화 테스트

### 지원 형식
- MP4, AVI, MOV 등 JavaCV가 지원하는 비디오 형식
- 30 FPS로 프레임 단위 스트리밍
- Base64 인코딩된 JPEG 이미지로 전송

### 폴더 경로 설정
- **기본 경로**: `${user.dir}/services/mock-server/cctv` (프로젝트 루트 기준)
- **설정 파일**: `application.yml`의 `cctv.folder.path` 속성으로 변경 가능
- **절대 경로 예시**: `/d:/kt_alp-b/project/kt-fire-iot/services/mock-server/cctv`

## 🗄️ 데이터베이스

### 로컬 개발 (H2)

- **URL**: `jdbc:h2:mem:testdb`
- **사용자**: `sa`
- **비밀번호**: (없음)

### 프로덕션 (PostgreSQL)

- **URL**: 환경변수 `POSTGRES_URL`로 설정
- **사용자**: 환경변수 `POSTGRES_USER`로 설정
- **비밀번호**: 환경변수 `POSTGRES_PASSWORD`로 설정

## 📊 샘플 데이터

애플리케이션 시작 시 다음 샘플 데이터가 자동으로 생성됩니다:

- **시설**: 5개 (공장, 창고, 사무실, 연구소)
- **장비**: 10개 (센서, 감지기 등)
- **사고**: 5개 (화재, 가스누출, 장비고장 등)
- **유지보수**: 5개 (점검, 수리, 교체 등)
- **실시간 데이터**: 5개 (온도, 습도, 연기밀도 등)
- **분석**: 5개 (화재위험, 가스누출 등)
- **알림**: 5개 (연기, 가스, 열 등)

### 실시간 데이터 생성 API

새로 추가된 실시간 데이터 생성 API는 Datalake 연동을 위해 다음과 같은 기능을 제공합니다:

#### 일반용 API (Realtime 모델)

- **기본 생성**: `/mock/realtime-generator/generate` - 10개 데이터 생성
- **스트리밍용**: `/mock/realtime-generator/generate/stream` - 5개씩 데이터 생성 (1-5분 간격 권장)
- **배치용**: `/mock/realtime-generator/generate/batch` - 100개씩 데이터 생성 (10-30분 간격 권장)
- **성능테스트용**: `/mock/realtime-generator/generate/performance-test` - 500개씩 데이터 생성
- **헬스체크용**: `/mock/realtime-generator/generate/health-check` - 1개 데이터 생성 (1분 간격 권장)

#### Datalake 전용 API (RawSensorData 모델)

- **기본 생성**: `/mock/realtime-generator/datalake/generate` - 10개 데이터 생성
- **스트리밍용**: `/mock/realtime-generator/datalake/generate/stream` - 5개씩 데이터 생성 (1-5분 간격 권장)
- **배치용**: `/mock/realtime-generator/datalake/generate/batch` - 100개씩 데이터 생성 (10-30분 간격 권장)

**데이터 특성**:

- **90% 정상 데이터**: 온도(15-35°C), 습도(30-70%), 연기밀도(0.001-0.050), CO(0.001-0.030), 가스(0.001-0.040)
- **10% 이상 데이터**: 고온(80-120°C), 고습도(95-100%), 연기밀도(0.200-1.000), CO(0.100-0.500), 가스(0.150-0.800), 복합 이상 등

**Datalake 연동 시 주의사항**:

- Datalake 연동에는 `/datalake/*` 엔드포인트를 사용하세요
- 이 엔드포인트는 Datalake의 `RawSensorData` 모델과 정확히 일치하는 JSON 형태로 데이터를 반환합니다
- 필드명: `equipment_id`, `facility_id`, `equipment_location`, `measured_at`, `temperature`, `humidity`, `smoke_density`, `co_level`, `gas_level`, `metadata`

## 🔧 설정

### 프로파일

- **local**: H2 데이터베이스, 개발용 설정
- **cloud**: PostgreSQL, 프로덕션용 설정

### CCTV 스트리밍 설정

```yaml
# application.yml
cctv:
  folder:
    path: ${user.dir}/services/mock-server/cctv
```

**경로 설정 옵션**:
- **기본값**: `${user.dir}/services/mock-server/cctv` (프로젝트 루트 기준)
- **절대 경로**: `/d:/kt_alp-b/project/kt-fire-iot/services/mock-server/cctv`
- **상대 경로**: `./cctv` (현재 디렉토리 기준)

### 환경변수

- `SPRING_PROFILES_ACTIVE`: 활성 프로파일 설정
- `POSTGRES_URL`: PostgreSQL 연결 URL
- `POSTGRES_USER`: PostgreSQL 사용자명
- `POSTGRES_PASSWORD`: PostgreSQL 비밀번호

## 📝 API 문서

Swagger UI를 통해 모든 API 엔드포인트를 확인하고 테스트할 수 있습니다:
http://localhost:8001/swagger-ui.html

### CCTV 스트리밍 API 테스트

#### REST API 테스트
```bash
# 사용 가능한 비디오 목록 확인
curl http://localhost:8001/api/cctv/videos

# 스트리밍 시작
curl -X POST "http://localhost:8001/api/cctv/stream/start?videoFileName=sample1.mp4"

# 스트리밍 상태 확인
curl http://localhost:8001/api/cctv/stream/status

# 스트리밍 중지
curl -X POST http://localhost:8001/api/cctv/stream/stop
```

#### WebSocket 테스트
- **HTML 테스트 페이지**: `http://localhost:8001/cctv-streaming.html`
- **WebSocket 연결**: `ws://localhost:8001/cctv-websocket`

## 🧪 테스트

```bash
# 단위 테스트 실행
mvn test

# 통합 테스트 실행
mvn verify
```

### CCTV 스트리밍 테스트

#### Windows PowerShell
```powershell
# PowerShell 스크립트 실행
.\test-cctv-streaming.ps1
```

#### Linux/Mac
```bash
# Bash 스크립트 실행
chmod +x test-cctv-streaming.sh
./test-cctv-streaming.sh
```

#### 수동 테스트
1. **서버 실행**: `mvn spring-boot:run`
2. **브라우저 접속**: `http://localhost:8001/cctv-streaming.html`
3. **비디오 선택**: 드롭다운에서 sample1.mp4 또는 sample2.mp4 선택
4. **스트리밍 시작**: "스트리밍 시작" 버튼 클릭
5. **실시간 확인**: WebSocket을 통한 실시간 프레임 수신 확인

## 📦 빌드

```bash
# JAR 파일 생성
mvn clean package

# Docker 이미지 빌드
docker build -t mock-server .
```

### 프로젝트 구조
```
services/mock-server/
├── cctv/                    # CCTV 비디오 파일 (sample1.mp4, sample2.mp4)
├── src/                     # 소스 코드
│   ├── main/java/
│   │   ├── config/         # WebSocket 설정
│   │   ├── controller/     # REST API 컨트롤러
│   │   ├── handler/        # WebSocket 메시지 핸들러
│   │   └── service/        # CCTV 스트리밍 서비스
│   └── resources/
│       ├── static/         # HTML 테스트 페이지
│       └── application.yml # 설정 파일
├── test-cctv-streaming.ps1 # Windows 테스트 스크립트
├── test-cctv-streaming.sh  # Linux/Mac 테스트 스크립트
└── README.md               # 프로젝트 문서
```

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
