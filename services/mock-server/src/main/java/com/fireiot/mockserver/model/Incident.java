package com.fireiot.mockserver.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "incident")
public class Incident {

    @Id
    @Column(name = "incident_id", length = 10, nullable = false)
    private String incidentId;

    @Column(name = "facility_id", length = 10, nullable = false)
    private String facilityId;

    @Column(name = "incident_type", length = 10)
    private String incidentType;

    @Enumerated(EnumType.STRING)
    @Column(name = "severity", columnDefinition = "ENUM('INFO', 'WARN', 'EMERGENCY')")
    private IncidentSeverity severity;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "resolved_at")
    private LocalDateTime resolvedAt;

    @Column(name = "report_file_name", length = 20)
    private String reportFileName;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "version")
    private Integer version;

    // Default constructor
    public Incident() {}

    // Constructor with required fields
    public Incident(String incidentId, String facilityId) {
        this.incidentId = incidentId;
        this.facilityId = facilityId;
    }

    // Getters and Setters
    public String getIncidentId() {
        return incidentId;
    }

    public void setIncidentId(String incidentId) {
        this.incidentId = incidentId;
    }

    public String getFacilityId() {
        return facilityId;
    }

    public void setFacilityId(String facilityId) {
        this.facilityId = facilityId;
    }

    public String getIncidentType() {
        return incidentType;
    }

    public void setIncidentType(String incidentType) {
        this.incidentType = incidentType;
    }

    public IncidentSeverity getSeverity() {
        return severity;
    }

    public void setSeverity(IncidentSeverity severity) {
        this.severity = severity;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getResolvedAt() {
        return resolvedAt;
    }

    public void setResolvedAt(LocalDateTime resolvedAt) {
        this.resolvedAt = resolvedAt;
    }

    public String getReportFileName() {
        return reportFileName;
    }

    public void setReportFileName(String reportFileName) {
        this.reportFileName = reportFileName;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Integer getVersion() {
        return version;
    }

    public void setVersion(Integer version) {
        this.version = version;
    }

    // Enum for severity
    public enum IncidentSeverity {
        INFO, WARN, EMERGENCY
    }
}
