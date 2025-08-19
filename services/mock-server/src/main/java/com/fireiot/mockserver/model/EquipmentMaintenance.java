package com.fireiot.mockserver.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "equipment_maintanence")
public class EquipmentMaintenance {

    @Id
    @Column(name = "maintenance_log_id", length = 255, nullable = false)
    private String maintenanceLogId;

    @Column(name = "equiment_id", length = 10, nullable = false)
    private String equipmentId;

    @Column(name = "facility_id", length = 10)
    private String facilityId;

    @Column(name = "equipment_location", length = 40)
    private String equipmentLocation;

    @Enumerated(EnumType.STRING)
    @Column(name = "maintenance_type", columnDefinition = "ENUM('INSPECTION', 'REPAIR', 'REPLACE', 'CLEAN', 'CALIBRATE', 'OTHER')")
    private MaintenanceType maintenanceType;

    @Column(name = "scheduled_date")
    private LocalDateTime scheduledDate;

    @Column(name = "performed_date")
    private LocalDateTime performedDate;

    @Column(name = "manager", length = 10)
    private String manager;

    @Column(name = "status_code", length = 10)
    private String statusCode;

    @Column(name = "next_scheduled_date")
    private LocalDateTime nextScheduledDate;

    @Column(name = "note", columnDefinition = "TEXT")
    private String note;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "version")
    private Integer version;

    // Default constructor
    public EquipmentMaintenance() {}

    // Constructor with required fields
    public EquipmentMaintenance(String maintenanceLogId, String equipmentId) {
        this.maintenanceLogId = maintenanceLogId;
        this.equipmentId = equipmentId;
    }

    // Getters and Setters
    public String getMaintenanceLogId() {
        return maintenanceLogId;
    }

    public void setMaintenanceLogId(String maintenanceLogId) {
        this.maintenanceLogId = maintenanceLogId;
    }

    public String getEquipmentId() {
        return equipmentId;
    }

    public void setEquipmentId(String equipmentId) {
        this.equipmentId = equipmentId;
    }

    public String getFacilityId() {
        return facilityId;
    }

    public void setFacilityId(String facilityId) {
        this.facilityId = facilityId;
    }

    public String getEquipmentLocation() {
        return equipmentLocation;
    }

    public void setEquipmentLocation(String equipmentLocation) {
        this.equipmentLocation = equipmentLocation;
    }

    public MaintenanceType getMaintenanceType() {
        return maintenanceType;
    }

    public void setMaintenanceType(MaintenanceType maintenanceType) {
        this.maintenanceType = maintenanceType;
    }

    public LocalDateTime getScheduledDate() {
        return scheduledDate;
    }

    public void setScheduledDate(LocalDateTime scheduledDate) {
        this.scheduledDate = scheduledDate;
    }

    public LocalDateTime getPerformedDate() {
        return performedDate;
    }

    public void setPerformedDate(LocalDateTime performedDate) {
        this.performedDate = performedDate;
    }

    public String getManager() {
        return manager;
    }

    public void setManager(String manager) {
        this.manager = manager;
    }

    public String getStatusCode() {
        return statusCode;
    }

    public void setStatusCode(String statusCode) {
        this.statusCode = statusCode;
    }

    public LocalDateTime getNextScheduledDate() {
        return nextScheduledDate;
    }

    public void setNextScheduledDate(LocalDateTime nextScheduledDate) {
        this.nextScheduledDate = nextScheduledDate;
    }

    public String getNote() {
        return note;
    }

    public void setNote(String note) {
        this.note = note;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
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

    // Enum for maintenance type
    public enum MaintenanceType {
        INSPECTION, REPAIR, REPLACE, CLEAN, CALIBRATE, OTHER
    }
}
