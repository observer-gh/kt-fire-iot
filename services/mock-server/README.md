# Mock Server

Fire IoT 시스템을 위한 Mock Server입니다.

## 🚀 기능

- **시설 관리**: 시설 정보 CRUD
- **장비 관리**: 장비 정보 및 상태 관리
- **사고 관리**: 사고 발생 및 해결 추적
- **유지보수 관리**: 장비 유지보수 일정 및 이력
- **실시간 데이터**: 센서 데이터 실시간 수집
- **분석 결과**: AI 분석 결과 관리
- **알림 시스템**: 다양한 알림 타입 및 심각도 관리

## 🛠️ 기술 스택

- **Java 17**
- **Spring Boot 3.2.0**
- **Spring Data JPA**
- **H2 Database** (로컬 개발)
- **PostgreSQL** (프로덕션)
- **OpenAPI/Swagger UI**

## 📋 요구사항

- Java 17 이상
- Maven 3.6 이상

## 🏃‍♂️ 실행 방법

### 로컬 개발 환경

```bash
# 프로젝트 빌드
mvn clean compile

# 애플리케이션 실행
mvn spring-boot:run
```

### Docker 실행

#### 단일 컨테이너 실행
```bash
# Docker 이미지 빌드 및 실행
docker build -t mock-server .
docker run -p 8080:8080 mock-server
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
- **애플리케이션**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **H2 Console**: http://localhost:8080/h2-console

### API 경로
- **시설**: `/mock/facility`
- **장비**: `/mock/equipment`
- **사고**: `/mock/incident`
- **유지보수**: `/mock/equipment-maintenance`
- **실시간 데이터**: `/mock/realtime`
- **분석**: `/mock/analysis`
- **알림**: `/mock/alert`

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

## 🔧 설정

### 프로파일
- **local**: H2 데이터베이스, 개발용 설정
- **cloud**: PostgreSQL, 프로덕션용 설정

### 환경변수
- `SPRING_PROFILES_ACTIVE`: 활성 프로파일 설정
- `POSTGRES_URL`: PostgreSQL 연결 URL
- `POSTGRES_USER`: PostgreSQL 사용자명
- `POSTGRES_PASSWORD`: PostgreSQL 비밀번호

## 📝 API 문서

Swagger UI를 통해 모든 API 엔드포인트를 확인하고 테스트할 수 있습니다:
http://localhost:8080/swagger-ui.html

## 🧪 테스트

```bash
# 단위 테스트 실행
mvn test

# 통합 테스트 실행
mvn verify
```

## 📦 빌드

```bash
# JAR 파일 생성
mvn clean package

# Docker 이미지 빌드
docker build -t mock-server .
```

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
