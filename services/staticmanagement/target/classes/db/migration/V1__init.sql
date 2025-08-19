-- StaticManagement Database Schema
-- V1: Initial schema for equipment and maintenance management

CREATE TABLE equipment (
    equipment_id VARCHAR(100) PRIMARY KEY,
    equipment_type VARCHAR(50) NOT NULL CHECK (equipment_type IN ('SENSOR', 'ALARM', 'SPRINKLER', 'CAMERA', 'COMMUNICATION', 'VEHICLE', 'TOOL')),
    name VARCHAR(255) NOT NULL,
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    serial_number VARCHAR(255),
    location_id VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE', 'RETIRED')),
    installation_date TIMESTAMP WITH TIME ZONE,
    warranty_expiry TIMESTAMP WITH TIME ZONE,
    specifications JSONB,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE maintenance (
    maintenance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id VARCHAR(100) NOT NULL REFERENCES equipment(equipment_id),
    maintenance_type VARCHAR(50) NOT NULL CHECK (maintenance_type IN ('PREVENTIVE', 'CORRECTIVE', 'EMERGENCY', 'INSPECTION')),
    status VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    scheduled_date TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_date TIMESTAMP WITH TIME ZONE,
    technician_id VARCHAR(100) NOT NULL,
    description TEXT,
    findings TEXT,
    actions_taken TEXT,
    parts_replaced TEXT[],
    cost DECIMAL(10,2),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_status ON equipment(status);
CREATE INDEX idx_maintenance_equipment_id ON maintenance(equipment_id);
CREATE INDEX idx_maintenance_status ON maintenance(status);
