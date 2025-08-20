# Fire IoT MSA

IoT 화재 모니터링 시스템으로 실시간 데이터 처리 및 알림 기능을 제공합니다.

## 서비스 링크

### 핵심 서비스

- **[DataLake](./services/datalake/README.md)** - 센서 데이터 수집, 문제 탐지, 대시보드 제공
- **[ControlTower](./services/controltower/README.md)** - 다른 서비스에 데이터를 제공하는 메인 서비스
- **[FacilityManagement](./services/facilitymanagement/README.md)** - 장비 및 유지보수 정보 관리
- **[Alert](./services/alert/README.md)** - 문제 발견 시 알림 발송
- **[MockServer](./services/mock-server/README.md)** - 테스트용 가짜 데이터 생성

## 아키텍처 다이어그램

![아키텍처](./architecture.jpg)

## ADR (아키텍처 결정 기록)

### ADR-001: 서비스 간 통신에 Kafka 사용

- **문제**: 서비스들이 서로 통신해야 함
- **결정**: 서비스 간 메시지 전달에 Kafka 사용
- **이유**: Kafka는 Azure Event Hub와 원활한 통합을 제공합니다.

### ADR-002: 서비스별 데이터베이스 분리

- **문제**: 각 서비스의 데이터를 어디에 저장할지
- **결정**: 각 서비스가 필요시 자체 PostgreSQL 데이터베이스 보유
- **이유**: 서비스가 다른 서비스에 영향을 주지 않고 데이터를 변경할 수 있음

## 데이터 아키텍처

![ERD](./erd.png)

### 데이터베이스 테이블 (PostgreSQL)

**DataLake 데이터베이스:**

```
realtime
- id (PK)
- equipment_id
- facility_id
- temperature, humidity, smoke_density, co_level, gas_level
- measured_at
- created_at

alert
- id (PK)
- equipment_id
- alert_type (WARNING, EMERGENCY)
- message
- created_at
```

**FacilityManagement 데이터베이스:**

```
equipment
- id (PK)
- name, type, location
- status (ACTIVE, INACTIVE, MAINTENANCE)
- created_at

maintenance
- id (PK)
- equipment_id (FK)
- type, description
- scheduled_date, completed_date
- status (SCHEDULED, IN_PROGRESS, COMPLETED)
```

### Kafka 토픽

```
dataLake.sensorDataAnomalyDetected
- equipment_id, facility_id, alert_type, message, timestamp

dataLake.sensorDataSaved
- equipment_id, facility_id, data, timestamp

alert.alertSendFail
- alert_id, message, severity, timestamp

```

## 에러 처리

### 전략 1: 단순 재시도

- 서비스 호출이 실패하면 3번까지 재시도
- 재시도 간 1초 대기
- 여전히 실패하면 에러 로그 기록 후 중단

### 전략 2: 서킷 브레이커

- 1분 내에 서비스가 5번 실패하면 30초간 시도 중단
- 서비스가 복구될 때까지 기다린 후 다시 시도
- 시스템 과부하 방지

### 헬스 체크

각 서비스는 `/healthz` 엔드포인트를 가짐:

```
GET /healthz
Response: {"status": "healthy", "timestamp": "2024-01-01T12:00:00Z"}
```

### 에러 로깅

- 모든 에러는 타임스탬프와 서비스명과 함께 로그 기록
- 중요한 에러는 모니터링 시스템으로 전송
- 데이터베이스 연결 에러는 재시도 트리거

## MSA 보드

### 서비스 의존성

```
DataLake가 필요로 하는 것:
- PostgreSQL (데이터 저장)
- Redis (캐시)
- Kafka (메시지 전송)
- Mock Server (데이터 수집)

ControlTower가 필요로 하는 것:
- Kafka (메시지 수신)
- 데이터베이스 없음 (읽기 전용)

FacilityManagement가 필요로 하는 것:
- PostgreSQL (장비 데이터 저장)

Alert가 필요로 하는 것:
- Kafka (메시지 수신)
- Redis (중복 제거)
- Slack (알림 발송)

Mock Server가 필요로 하는 것:
- 없음 (독립 실행)
```

### 통신 패턴

```
DataLake → Kafka → ControlTower (센서 데이터)
DataLake → Kafka → Alert (이상치 알림)
ControlTower → Kafka → Alert (경고 알림)
FacilityManagement → Kafka → Alert (유지보수 알림)
```

## 빠른 시작

### 모든 서비스 시작

```bash
docker-compose up -d
```

### 상태 확인

```bash
docker-compose ps
```

### 접속 지점

- **DataLake Dashboard**: http://localhost:8501
- **ControlTower API**: http://localhost:8082
- **FacilityManagement API**: http://localhost:8083
- **Mock Server**: http://localhost:8001
- **Kafka UI**: http://localhost:8090

### 모든 서비스 중지

```bash
docker-compose down
```

## 개발

### 서비스 빌드

```bash
# 모든 서비스 빌드
docker-compose build

# 특정 서비스 빌드
docker-compose build datalake
```

### 로컬 개발

```bash
# DataLake
cd services/datalake
python -m uvicorn app.main:app --reload

# ControlTower
cd services/controltower
./mvnw spring-boot:run

# FacilityManagement
cd services/facilitymanagement
./mvnw spring-boot:run
```

## 배포

### 로컬

```bash
docker-compose up -d
```

### Azure

```bash
cd infra/aca
./deploy.sh
```
