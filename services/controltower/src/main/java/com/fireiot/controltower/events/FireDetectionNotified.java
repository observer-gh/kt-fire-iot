package com.fireiot.controltower.events;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.OffsetDateTime;

public class FireDetectionNotified {
  @JsonProperty("version")
  private Integer version;

  @JsonProperty("alert_id")
  private String alertId;

  @JsonProperty("incident_id")
  private String incidentId;

  @JsonProperty("facility_id")
  private String facilityId;

  @JsonProperty("equipment_location")
  private String equipmentLocation;

  @JsonProperty("alert_type")
  private String alertType;

  @JsonProperty("severity")
  private String severity;

  @JsonProperty("status")
  private String status;

  @JsonProperty("created_at")
  private OffsetDateTime createdAt;

  @JsonProperty("description")
  private String description;

  @JsonProperty("cctv_id")
  private String cctvId;

  @JsonProperty("detection_confidence")
  private Integer detectionConfidence;

  // Getters and Setters
  public Integer getVersion() {
    return version;
  }

  public void setVersion(Integer version) {
    this.version = version;
  }

  public String getAlertId() {
    return alertId;
  }

  public void setAlertId(String alertId) {
    this.alertId = alertId;
  }

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

  public String getEquipmentLocation() {
    return equipmentLocation;
  }

  public void setEquipmentLocation(String equipmentLocation) {
    this.equipmentLocation = equipmentLocation;
  }

  public String getAlertType() {
    return alertType;
  }

  public void setAlertType(String alertType) {
    this.alertType = alertType;
  }

  public String getSeverity() {
    return severity;
  }

  public void setSeverity(String severity) {
    this.severity = severity;
  }

  public String getStatus() {
    return status;
  }

  public void setStatus(String status) {
    this.status = status;
  }

  public OffsetDateTime getCreatedAt() {
    return createdAt;
  }

  public void setCreatedAt(OffsetDateTime createdAt) {
    this.createdAt = createdAt;
  }

  public String getDescription() {
    return description;
  }

  public void setDescription(String description) {
    this.description = description;
  }

  public String getCctvId() {
    return cctvId;
  }

  public void setCctvId(String cctvId) {
    this.cctvId = cctvId;
  }

  public Integer getDetectionConfidence() {
    return detectionConfidence;
  }

  public void setDetectionConfidence(Integer detectionConfidence) {
    this.detectionConfidence = detectionConfidence;
  }
}
