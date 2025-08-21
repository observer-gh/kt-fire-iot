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
  private EquipmentStateChanges changes;

  @JsonProperty("requested_at")
  private OffsetDateTime requestedAt;

  @JsonProperty("requested_by")
  private String requestedBy;

  // Default constructor
  public EquipmentStateUpdateRequested() {}

  // Constructor with required fields
  public EquipmentStateUpdateRequested(Integer version, String requestId, String equipmentId,
      String facilityId, EquipmentStateChanges changes, OffsetDateTime requestedAt,
      String requestedBy) {
    this.version = version;
    this.requestId = requestId;
    this.equipmentId = equipmentId;
    this.facilityId = facilityId;
    this.changes = changes;
    this.requestedAt = requestedAt;
    this.requestedBy = requestedBy;
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

  public EquipmentStateChanges getChanges() {
    return changes;
  }

  public void setChanges(EquipmentStateChanges changes) {
    this.changes = changes;
  }

  public OffsetDateTime getRequestedAt() {
    return requestedAt;
  }

  public void setRequestedAt(OffsetDateTime requestedAt) {
    this.requestedAt = requestedAt;
  }

  public String getRequestedBy() {
    return requestedBy;
  }

  public void setRequestedBy(String requestedBy) {
    this.requestedBy = requestedBy;
  }

  // Inner class for equipment state changes
  public static class EquipmentStateChanges {
    @JsonProperty("status_code")
    private String statusCode;

    @JsonProperty("equipment_location")
    private String equipmentLocation;

    @JsonProperty("expired_at")
    private OffsetDateTime expiredAt;

    @JsonProperty("last_maintenance_date")
    private OffsetDateTime lastMaintenanceDate;

    @JsonProperty("next_maintenance_date")
    private OffsetDateTime nextMaintenanceDate;

    // Default constructor
    public EquipmentStateChanges() {}

    // Constructor with fields
    public EquipmentStateChanges(String statusCode, String equipmentLocation,
        OffsetDateTime expiredAt, OffsetDateTime lastMaintenanceDate,
        OffsetDateTime nextMaintenanceDate) {
      this.statusCode = statusCode;
      this.equipmentLocation = equipmentLocation;
      this.expiredAt = expiredAt;
      this.lastMaintenanceDate = lastMaintenanceDate;
      this.nextMaintenanceDate = nextMaintenanceDate;
    }

    // Getters and Setters
    public String getStatusCode() {
      return statusCode;
    }

    public void setStatusCode(String statusCode) {
      this.statusCode = statusCode;
    }

    public String getEquipmentLocation() {
      return equipmentLocation;
    }

    public void setEquipmentLocation(String equipmentLocation) {
      this.equipmentLocation = equipmentLocation;
    }

    public OffsetDateTime getExpiredAt() {
      return expiredAt;
    }

    public void setExpiredAt(OffsetDateTime expiredAt) {
      this.expiredAt = expiredAt;
    }

    public OffsetDateTime getLastMaintenanceDate() {
      return lastMaintenanceDate;
    }

    public void setLastMaintenanceDate(OffsetDateTime lastMaintenanceDate) {
      this.lastMaintenanceDate = lastMaintenanceDate;
    }

    public OffsetDateTime getNextMaintenanceDate() {
      return nextMaintenanceDate;
    }

    public void setNextMaintenanceDate(OffsetDateTime nextMaintenanceDate) {
      this.nextMaintenanceDate = nextMaintenanceDate;
    }
  }
}
