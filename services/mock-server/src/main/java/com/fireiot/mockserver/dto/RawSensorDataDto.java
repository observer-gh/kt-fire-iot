package com.fireiot.mockserver.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * Datalake의 RawSensorData 모델과 정확히 맞는 DTO
 */
public class RawSensorDataDto {

  @JsonProperty("equipment_id")
  private String equipmentId;

  @JsonProperty("facility_id")
  private String facilityId;

  @JsonProperty("equipment_location")
  private String equipmentLocation;

  @JsonProperty("measured_at")
  @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
  private LocalDateTime measuredAt;

  private Float temperature;
  private Float humidity;

  @JsonProperty("smoke_density")
  private Float smokeDensity;

  @JsonProperty("co_level")
  private Float coLevel;

  @JsonProperty("gas_level")
  private Float gasLevel;

  private Map<String, Object> metadata;

  // Default constructor
  public RawSensorDataDto() {}

  // Constructor with required fields
  public RawSensorDataDto(String equipmentId, LocalDateTime measuredAt) {
    this.equipmentId = equipmentId;
    this.measuredAt = measuredAt;
  }

  // Getters and Setters
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

  public LocalDateTime getMeasuredAt() {
    return measuredAt;
  }

  public void setMeasuredAt(LocalDateTime measuredAt) {
    this.measuredAt = measuredAt;
  }

  public Float getTemperature() {
    return temperature;
  }

  public void setTemperature(Float temperature) {
    this.temperature = temperature;
  }

  public Float getHumidity() {
    return humidity;
  }

  public void setHumidity(Float humidity) {
    this.humidity = humidity;
  }

  public Float getSmokeDensity() {
    return smokeDensity;
  }

  public void setSmokeDensity(Float smokeDensity) {
    this.smokeDensity = smokeDensity;
  }

  public Float getCoLevel() {
    return coLevel;
  }

  public void setCoLevel(Float coLevel) {
    this.coLevel = coLevel;
  }

  public Float getGasLevel() {
    return gasLevel;
  }

  public void setGasLevel(Float gasLevel) {
    this.gasLevel = gasLevel;
  }

  public Map<String, Object> getMetadata() {
    return metadata;
  }

  public void setMetadata(Map<String, Object> metadata) {
    this.metadata = metadata;
  }
}
