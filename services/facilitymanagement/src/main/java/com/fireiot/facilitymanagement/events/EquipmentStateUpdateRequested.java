package com.fireiot.facilitymanagement.events;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.OffsetDateTime;

public class EquipmentStateUpdateRequested {

  @JsonProperty("version")
  private Integer version;

  @JsonProperty("request_id")
  private String requestId;

  @JsonProperty("equipment_id")
  private String equipmentId;

  @JsonProperty("facility_id")
  private String facilityId;

  @JsonProperty("changes")
  private EquipmentChanges changes;

  @JsonProperty("reason")
  private String reason;

  @JsonProperty("requested_by")
  private String requestedBy;

  @JsonProperty("requested_at")
  private OffsetDateTime requestedAt;

  // Inner class for equipment changes
  public static class EquipmentChanges {
    @JsonProperty("equipment_location")
    private String equipmentLocation;

    @JsonProperty("status_code")
    private String statusCode;

    @JsonProperty("expired_at")
    private OffsetDateTime expiredAt;

    // Default constructor
    public EquipmentChanges() {}

    // Getters and Setters
    public String getEquipmentLocation() {
      return equipmentLocation;
    }

    public void setEquipmentLocation(String equipmentLocation) {
      this.equipmentLocation = equipmentLocation;
    }

    public String getStatusCode() {
      return statusCode;
    }

    public void setStatusCode(String statusCode) {
      this.statusCode = statusCode;
    }

    public OffsetDateTime getExpiredAt() {
      return expiredAt;
    }

    public void setExpiredAt(OffsetDateTime expiredAt) {
      this.expiredAt = expiredAt;
    }
  }

  // Default constructor
  public EquipmentStateUpdateRequested() {}

  // Constructor with required fields
  public EquipmentStateUpdateRequested(Integer version, String requestId, String equipmentId,
      EquipmentChanges changes, OffsetDateTime requestedAt) {
    this.version = version;
    this.requestId = requestId;
    this.equipmentId = equipmentId;
    this.changes = changes;
    this.requestedAt = requestedAt;
  }

  // Getters and Setters
  public Integer getVersion() {
    return version;
  }

  public void setVersion(Integer version) {
    this.version = version;
  }

  public String getRequestId() {
    return requestId;
  }

  public void setRequestId(String requestId) {
    this.requestId = requestId;
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

  public EquipmentChanges getChanges() {
    return changes;
  }

  public void setChanges(EquipmentChanges changes) {
    this.changes = changes;
  }

  public String getReason() {
    return reason;
  }

  public void setReason(String reason) {
    this.reason = reason;
  }

  public String getRequestedBy() {
    return requestedBy;
  }

  public void setRequestedBy(String requestedBy) {
    this.requestedBy = requestedBy;
  }

  public OffsetDateTime getRequestedAt() {
    return requestedAt;
  }

  public void setRequestedAt(OffsetDateTime requestedAt) {
    this.requestedAt = requestedAt;
  }
}
