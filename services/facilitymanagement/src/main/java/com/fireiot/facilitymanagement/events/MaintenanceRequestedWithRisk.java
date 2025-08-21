package com.fireiot.facilitymanagement.events;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fireiot.facilitymanagement.enums.MaintenanceType;
import java.time.OffsetDateTime;

public class MaintenanceRequestedWithRisk {

  @JsonProperty("version")
  private Integer version;

  @JsonProperty("maintenance_log_id")
  private String maintenanceLogId;

  @JsonProperty("equipment_id")
  private String equipmentId;

  @JsonProperty("facility_id")
  private String facilityId;

  @JsonProperty("maintenance_type")
  private MaintenanceType maintenanceType;

  @JsonProperty("scheduled_date")
  private OffsetDateTime scheduledDate;

  @JsonProperty("note")
  private String note;

  @JsonProperty("requested_at")
  private OffsetDateTime requestedAt;

  // 위험도 관련 필드 추가
  @JsonProperty("risk_score")
  private Double riskScore;

  @JsonProperty("risk_level")
  private String riskLevel;

  @JsonProperty("risk_recommendation")
  private String riskRecommendation;

  @JsonProperty("risk_calculation_time")
  private OffsetDateTime riskCalculationTime;

  // Default constructor
  public MaintenanceRequestedWithRisk() {}

  // Constructor with risk information
  public MaintenanceRequestedWithRisk(MaintenanceRequested original, Double riskScore,
      String riskLevel, String riskRecommendation) {
    this.version = original.getVersion();
    this.maintenanceLogId = original.getMaintenanceLogId();
    this.equipmentId = original.getEquipmentId();
    this.facilityId = original.getFacilityId();
    this.maintenanceType = original.getMaintenanceType();
    this.scheduledDate = original.getScheduledDate();
    this.note = original.getNote();
    this.requestedAt = original.getRequestedAt();
    this.riskScore = riskScore;
    this.riskLevel = riskLevel;
    this.riskRecommendation = riskRecommendation;
    this.riskCalculationTime = OffsetDateTime.now();
  }

  // Getters and Setters
  public Integer getVersion() {
    return version;
  }

  public void setVersion(Integer version) {
    this.version = version;
  }

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

  public MaintenanceType getMaintenanceType() {
    return maintenanceType;
  }

  public void setMaintenanceType(MaintenanceType maintenanceType) {
    this.maintenanceType = maintenanceType;
  }

  public OffsetDateTime getScheduledDate() {
    return scheduledDate;
  }

  public void setScheduledDate(OffsetDateTime scheduledDate) {
    this.scheduledDate = scheduledDate;
  }

  public String getNote() {
    return note;
  }

  public void setNote(String note) {
    this.note = note;
  }

  public OffsetDateTime getRequestedAt() {
    return requestedAt;
  }

  public void setRequestedAt(OffsetDateTime requestedAt) {
    this.requestedAt = requestedAt;
  }

  public Double getRiskScore() {
    return riskScore;
  }

  public void setRiskScore(Double riskScore) {
    this.riskScore = riskScore;
  }

  public String getRiskLevel() {
    return riskLevel;
  }

  public void setRiskLevel(String riskLevel) {
    this.riskLevel = riskLevel;
  }

  public String getRiskRecommendation() {
    return riskRecommendation;
  }

  public void setRiskRecommendation(String riskRecommendation) {
    this.riskRecommendation = riskRecommendation;
  }

  public OffsetDateTime getRiskCalculationTime() {
    return riskCalculationTime;
  }

  public void setRiskCalculationTime(OffsetDateTime riskCalculationTime) {
    this.riskCalculationTime = riskCalculationTime;
  }

}
