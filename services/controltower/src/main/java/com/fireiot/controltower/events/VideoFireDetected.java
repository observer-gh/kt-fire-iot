package com.fireiot.controltower.events;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.OffsetDateTime;

public class VideoFireDetected {
  @JsonProperty("version")
  private Integer version;

  @JsonProperty("event_id")
  private String eventId;

  @JsonProperty("facility_id")
  private String facilityId;

  @JsonProperty("equipment_location")
  private String equipmentLocation;

  @JsonProperty("detection_confidence")
  private Integer detectionConfidence;

  @JsonProperty("detection_timestamp")
  private OffsetDateTime detectionTimestamp;

  @JsonProperty("cctv_id")
  private String cctvId;

  @JsonProperty("detection_area")
  private String detectionArea;

  @JsonProperty("description")
  private String description;

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

  public Integer getDetectionConfidence() {
    return detectionConfidence;
  }

  public void setDetectionConfidence(Integer detectionConfidence) {
    this.detectionConfidence = detectionConfidence;
  }

  public OffsetDateTime getDetectionTimestamp() {
    return detectionTimestamp;
  }

  public void setDetectionTimestamp(OffsetDateTime detectionTimestamp) {
    this.detectionTimestamp = detectionTimestamp;
  }

  public String getCctvId() {
    return cctvId;
  }

  public void setCctvId(String cctvId) {
    this.cctvId = cctvId;
  }

  public String getDetectionArea() {
    return detectionArea;
  }

  public void setDetectionArea(String detectionArea) {
    this.detectionArea = detectionArea;
  }

  public String getDescription() {
    return description;
  }

  public void setDescription(String description) {
    this.description = description;
  }
}
