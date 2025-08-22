-- FacilityManagement Database Schema
-- V2: Drop existing tables and recreate with new schema

-- 기존 테이블 삭제 (CASCADE로 외래키 제약조건도 함께 삭제)
DROP TABLE IF EXISTS equipment_maintenance CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;

-- equipment 테이블 생성
CREATE TABLE equipment (
	equipment_id VARCHAR(10) NOT NULL,
	equipment_location VARCHAR(40) NULL,
	facility_id VARCHAR(10) NOT NULL,
	equipment_type VARCHAR(10) NULL,
	status_code VARCHAR(10) NULL,
	created_at TIMESTAMP NULL,
	installed_at TIMESTAMP NULL,
	expired_at TIMESTAMP NULL,
	version INTEGER NULL
);

-- equipment_maintenance 테이블 생성
CREATE TABLE equipment_maintenance (
	maintenance_log_id VARCHAR(255) NOT NULL,
	equipment_id VARCHAR(10) NOT NULL,
	facility_id VARCHAR(10) NULL,
	equipment_location VARCHAR(40) NULL,
	maintenance_type VARCHAR(20) NULL,
	scheduled_date TIMESTAMP NULL,
	performed_date TIMESTAMP NULL,
	manager VARCHAR(10) NULL,
	status_code VARCHAR(10) NULL,
	next_scheduled_date TIMESTAMP NULL,
	note TEXT NULL,
	created_at TIMESTAMP NULL,
	updated_at TIMESTAMP NULL,
	version INTEGER NULL
);

-- Primary Key 제약조건 추가
ALTER TABLE equipment ADD CONSTRAINT PK_EQUIPMENT PRIMARY KEY (
	equipment_id
);

ALTER TABLE equipment_maintenance ADD CONSTRAINT PK_EQUIPMENT_MAINTENANCE PRIMARY KEY (
	maintenance_log_id
);

-- Foreign Key 제약조건 추가
ALTER TABLE equipment_maintenance ADD CONSTRAINT FK_EQUIPMENT_MAINTENANCE_EQUIPMENT 
FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id);