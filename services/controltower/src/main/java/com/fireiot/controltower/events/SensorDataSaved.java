package com.fireiot.controltower.events;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.OffsetDateTime;

public class SensorDataSaved {
  @JsonProperty("version")
  private Integer version;

  @JsonProperty("event_id")
  private String eventId;

  @JsonProperty("equipment_id")
  private String equipmentId;

  @JsonProperty("facility_id")
  private String facilityId;

  @JsonProperty("equipment_location")
  private String equipmentLocation;

  @JsonProperty("measured_at")
  private OffsetDateTime measuredAt;

  @JsonProperty("temperature")
  private Double temperature;

  @JsonProperty("humidity")
  private Double humidity;

  @JsonProperty("smoke_density")
  private Double smokeDensity;

  @JsonProperty("co_level")
  private Double coLevel;

  @JsonProperty("gas_level")
  private Double gasLevel;

  @JsonProperty("ingested_at")
  private OffsetDateTime ingestedAt;

  // Getters and setters
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

  public String getEquipmentLocation() {
    return equipmentLocation;
  }

  public void setEquipmentLocation(String equipmentLocation) {
    this.equipmentLocation = equipmentLocation;
  }

  public OffsetDateTime getMeasuredAt() {
    return measuredAt;
  }

  public void setMeasuredAt(OffsetDateTime measuredAt) {
    this.measuredAt = measuredAt;
  }

  public Double getTemperature() {
    return temperature;
  }

  public void setTemperature(Double temperature) {
    this.temperature = temperature;
  }

  public Double getHumidity() {
    return humidity;
  }

  public void setHumidity(Double humidity) {
    this.humidity = humidity;
  }

  public Double getSmokeDensity() {
    return smokeDensity;
  }

  public void setSmokeDensity(Double smokeDensity) {
    this.smokeDensity = smokeDensity;
  }

  public Double getCoLevel() {
    return coLevel;
  }

  public void setCoLevel(Double coLevel) {
    this.coLevel = coLevel;
  }

  public Double getGasLevel() {
    return gasLevel;
  }

  public void setGasLevel(Double gasLevel) {
    this.gasLevel = gasLevel;
  }

  public OffsetDateTime getIngestedAt() {
    return ingestedAt;
  }

  public void setIngestedAt(OffsetDateTime ingestedAt) {
    this.ingestedAt = ingestedAt;
  }
}
