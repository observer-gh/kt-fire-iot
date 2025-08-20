package com.fireiot.mockserver.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "alert")
public class Alert {

    @Id
    @Column(name = "alert_id", length = 10, nullable = false)
    private String alertId;

    @Column(name = "equipment_id", length = 10)
    private String equipmentId;

    @Column(name = "facility_id", length = 10)
    private String facilityId;

    @Column(name = "equipment_location", length = 40)
    private String equipmentLocation;

    @Enumerated(EnumType.STRING)
    @Column(name = "alert_type", columnDefinition = "ENUM('SMOKE', 'GAS', 'CO', 'HEAT', 'POWER', 'COMM', 'CUSTOM')")
    private AlertType alertType;

    @Enumerated(EnumType.STRING)
    @Column(name = "severity", columnDefinition = "ENUM('INFO', 'WARN', 'EMERGENCY')")
    private AlertSeverity severity;

    @Column(name = "status", length = 20)
    private String status;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "resolved_at")
    private LocalDateTime resolvedAt;

    @Column(name = "version")
    private Integer version;

    // Default constructor
    public Alert() {}

    // Constructor with required fields
    public Alert(String alertId) {
        this.alertId = alertId;
    }

    // Getters and Setters
    public String getAlertId() {
        return alertId;
    }

    public void setAlertId(String alertId) {
        this.alertId = alertId;
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

    public AlertType getAlertType() {
        return alertType;
    }

    public void setAlertType(AlertType alertType) {
        this.alertType = alertType;
    }

    public AlertSeverity getSeverity() {
        return severity;
    }

    public void setSeverity(AlertSeverity severity) {
        this.severity = severity;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
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

    public LocalDateTime getResolvedAt() {
        return resolvedAt;
    }

    public void setResolvedAt(LocalDateTime resolvedAt) {
        this.resolvedAt = resolvedAt;
    }

    public Integer getVersion() {
        return version;
    }

    public void setVersion(Integer version) {
        this.version = version;
    }

    // Enum for alert type
    public enum AlertType {
        SMOKE, GAS, CO, HEAT, POWER, COMM, CUSTOM
    }

    // Enum for alert severity
    public enum AlertSeverity {
        INFO, WARN, EMERGENCY
    }
}
