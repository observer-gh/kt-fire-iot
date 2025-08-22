package com.fireiot.facilitymanagement.events;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fireiot.facilitymanagement.enums.MaintenanceType;
import java.time.OffsetDateTime;

public class MaintenanceRequested {

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

  // Default constructor
  public MaintenanceRequested() {}

  // Constructor with required fields
  public MaintenanceRequested(Integer version, String maintenanceLogId, String equipmentId,
      MaintenanceType maintenanceType, OffsetDateTime requestedAt) {
    this.version = version;
    this.maintenanceLogId = maintenanceLogId;
    this.equipmentId = equipmentId;
    this.maintenanceType = maintenanceType;
    this.requestedAt = requestedAt;
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
}
