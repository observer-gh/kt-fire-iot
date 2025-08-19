package com.fireiot.controltower.events;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.OffsetDateTime;

public class SensorAnomalyDetected {
  @JsonProperty("version")
  private Integer version;

  @JsonProperty("event_id")
  private String eventId;

  @JsonProperty("equipment_id")
  private String equipmentId;

  @JsonProperty("facility_id")
  private String facilityId;

  @JsonProperty("metric")
  private String metric;

  @JsonProperty("value")
  private Double value;

  @JsonProperty("threshold")
  private Double threshold;

  @JsonProperty("rule_id")
  private String ruleId;

  @JsonProperty("measured_at")
  private OffsetDateTime measuredAt;

  @JsonProperty("detected_at")
  private OffsetDateTime detectedAt;

  @JsonProperty("severity")
  private String severity;

  // Getters and Setters
  public Integer getVersion() {
    return version;
  }

  public void setVersion(Integer version) {
    this.version = version;
  }

  public String getEventId() {
    return eventId;
  }

  public void setEventId(String eventId) {
    this.eventId = eventId;
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

  public String getMetric() {
    return metric;
  }

  public void setMetric(String metric) {
    this.metric = metric;
  }

  public Double getValue() {
    return value;
  }

  public void setValue(Double value) {
    this.value = value;
  }

  public Double getThreshold() {
    return threshold;
  }

  public void setThreshold(Double threshold) {
    this.threshold = threshold;
  }

  public String getRuleId() {
    return ruleId;
  }

  public void setRuleId(String ruleId) {
    this.ruleId = ruleId;
  }

  public OffsetDateTime getMeasuredAt() {
    return measuredAt;
  }

  public void setMeasuredAt(OffsetDateTime measuredAt) {
    this.measuredAt = measuredAt;
  }

  public OffsetDateTime getDetectedAt() {
    return detectedAt;
  }

  public void setDetectedAt(OffsetDateTime detectedAt) {
    this.detectedAt = detectedAt;
  }

  public String getSeverity() {
    return severity;
  }

  public void setSeverity(String severity) {
    this.severity = severity;
  }
}
