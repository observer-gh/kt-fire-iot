# FacilityManagement

관리자에 의한 소방시설 데이터 업데이트 이벤트 발생 시 equipment, equipment_maintenance 데이터 수정하기.
배치 기능(매일 오전 8시에 1개월 이하로 만료되는 장비 조회)을 통해 유지보수가 필요한 장비에 대해 위험 스코어링을 계산하고 `maintenanceRequested` 토픽 발행.

## Kafka Topics

### Producer Topics (발행하는 토픽)

#### `facilitymanagement.maintenanceRequested`
- **목적**: 유지보수 요청 이벤트 발행. Alert 서비스가 구독하는 토픽이다.
- **발행 시점**: 
  - 배치 프로세스에서 만료 예정 장비 발견 시
- **이벤트 구조**:
  ```json
  {
    "version": 1,
    "maintenance_log_id": "MAINT_ABC12345",
    "equipment_id": "EQ001",
    "facility_id": "FAC001",
    "maintenance_type": "INSPECTION",
    "scheduled_date": "2025-08-21T10:00:00Z",
    "note": "정기 점검 필요",
    "requested_at": "2025-08-21T08:00:00Z"
  }
  ```

### Consumer Topics (구독하는 토픽)

#### `facilitymanagement.equipmentStateUpdateRequested`
- **목적**: ControlTower 가 발행한 토픽. 장비 상태 업데이트 요청 이벤트 발행
- **발행 시점**: 장비 정보 변경 요청 시
- **이벤트 구조**:
  ```json
  {
    "version": 1,
    "request_id": "REQ_XYZ789",
    "equipment_id": "EQ001",
    "facility_id": "FAC001",
    "changes": {
      "status_code": "MAINTENANCE",
      "equipment_location": "1층 소화기실"
    },
    "requested_at": "2025-08-21T09:00:00Z",
    "requested_by": "admin"
  }
  ```
