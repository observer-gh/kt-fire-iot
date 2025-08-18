-- ControlTower Database Schema
-- V1: Initial schema for read-only access to IoT fire monitoring data

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id VARCHAR(100) NOT NULL,
    rule_id VARCHAR(100) NOT NULL,
    rule_name VARCHAR(255) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    dispatched_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'DISPATCHED', 'ACKNOWLEDGED')),
    metadata JSONB,
    version INTEGER NOT NULL DEFAULT 1,
    created_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Station data table
CREATE TABLE station_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    smoke_level DECIMAL(8,4),
    co_level DECIMAL(8,4),
    battery_level DECIMAL(5,2),
    signal_strength DECIMAL(5,2),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    address TEXT,
    building_name VARCHAR(255),
    floor VARCHAR(50),
    room VARCHAR(50),
    version INTEGER NOT NULL DEFAULT 1,
    created_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Equipment status table
CREATE TABLE equipment_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id VARCHAR(100) NOT NULL,
    equipment_type VARCHAR(50) NOT NULL CHECK (equipment_type IN ('SENSOR', 'ALARM', 'SPRINKLER', 'CAMERA', 'COMMUNICATION')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('OPERATIONAL', 'WARNING', 'ERROR', 'OFFLINE', 'MAINTENANCE')),
    last_maintenance TIMESTAMP WITH TIME ZONE,
    next_maintenance TIMESTAMP WITH TIME ZONE,
    version_info VARCHAR(100),
    version INTEGER NOT NULL DEFAULT 1,
    created_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_alerts_station_id ON alerts(station_id);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_station_created ON alerts(station_id, created_at);

CREATE INDEX idx_station_data_station_id ON station_data(station_id);
CREATE INDEX idx_station_data_timestamp ON station_data(timestamp);
CREATE INDEX idx_station_data_station_timestamp ON station_data(station_id, timestamp);

CREATE INDEX idx_equipment_status_equipment_id ON equipment_status(equipment_id);
CREATE INDEX idx_equipment_status_type ON equipment_status(equipment_type);
CREATE INDEX idx_equipment_status_status ON equipment_status(status);

-- Latest station data view (for efficient latest data retrieval)
CREATE VIEW latest_station_data AS
SELECT DISTINCT ON (station_id)
    station_id,
    timestamp,
    temperature,
    humidity,
    smoke_level,
    co_level,
    battery_level,
    signal_strength,
    latitude,
    longitude,
    address,
    building_name,
    floor,
    room
FROM station_data
ORDER BY station_id, timestamp DESC;

-- Alert statistics view
CREATE VIEW alert_statistics AS
SELECT 
    station_id,
    COUNT(*) as total_alerts,
    COUNT(CASE WHEN severity = 'CRITICAL' THEN 1 END) as critical_alerts,
    COUNT(CASE WHEN severity = 'HIGH' THEN 1 END) as high_alerts,
    COUNT(CASE WHEN severity = 'MEDIUM' THEN 1 END) as medium_alerts,
    COUNT(CASE WHEN severity = 'LOW' THEN 1 END) as low_alerts,
    COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending_alerts,
    MAX(created_at) as last_alert_time
FROM alerts
GROUP BY station_id;

-- Update trigger for updated_date
CREATE OR REPLACE FUNCTION update_updated_date_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_date = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_alerts_updated_date BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_date_column();

CREATE TRIGGER update_station_data_updated_date BEFORE UPDATE ON station_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_date_column();

CREATE TRIGGER update_equipment_status_updated_date BEFORE UPDATE ON equipment_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_date_column();
