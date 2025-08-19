package com.fireiot.mockserver.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "facility")
public class Facility {

    @Id
    @Column(name = "facility_id", length = 10, nullable = false)
    private String facilityId;

    @Column(name = "address", length = 30)
    private String address;

    @Column(name = "internal_address", length = 10)
    private String internalAddress;

    @Column(name = "facility_type", length = 10)
    private String facilityType;

    @Column(name = "manager_name", length = 20)
    private String managerName;

    @Column(name = "manager_phone", length = 20)
    private String managerPhone;

    @Column(name = "risk_level", length = 20)
    private String riskLevel;

    @Column(name = "active_alerts_count")
    private Integer activeAlertsCount;

    @Column(name = "online_sensors_count")
    private Integer onlineSensorsCount;

    @Column(name = "total_sensors_count")
    private Integer totalSensorsCount;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "version")
    private Integer version;

    // Default constructor
    public Facility() {}

    // Constructor with required fields
    public Facility(String facilityId) {
        this.facilityId = facilityId;
    }

    // Getters and Setters
    public String getFacilityId() {
        return facilityId;
    }

    public void setFacilityId(String facilityId) {
        this.facilityId = facilityId;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getInternalAddress() {
        return internalAddress;
    }

    public void setInternalAddress(String internalAddress) {
        this.internalAddress = internalAddress;
    }

    public String getFacilityType() {
        return facilityType;
    }

    public void setFacilityType(String facilityType) {
        this.facilityType = facilityType;
    }

    public String getManagerName() {
        return managerName;
    }

    public void setManagerName(String managerName) {
        this.managerName = managerName;
    }

    public String getManagerPhone() {
        return managerPhone;
    }

    public void setManagerPhone(String managerPhone) {
        this.managerPhone = managerPhone;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel) {
        this.riskLevel = riskLevel;
    }

    public Integer getActiveAlertsCount() {
        return activeAlertsCount;
    }

    public void setActiveAlertsCount(Integer activeAlertsCount) {
        this.activeAlertsCount = activeAlertsCount;
    }

    public Integer getOnlineSensorsCount() {
        return onlineSensorsCount;
    }

    public void setOnlineSensorsCount(Integer onlineSensorsCount) {
        this.onlineSensorsCount = onlineSensorsCount;
    }

    public Integer getTotalSensorsCount() {
        return totalSensorsCount;
    }

    public void setTotalSensorsCount(Integer totalSensorsCount) {
        this.totalSensorsCount = totalSensorsCount;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public Integer getVersion() {
        return version;
    }

    public void setVersion(Integer version) {
        this.version = version;
    }
}
