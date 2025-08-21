package com.fireiot.facilitymanagement.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "equipment")
public class Equipment {

  @Id
  @Column(name = "equipment_id", length = 10)
  private String equipmentId;

  @Column(name = "equipment_location", length = 40)
  private String equipmentLocation;

  @Column(name = "facility_id", length = 10, nullable = false)
  private String facilityId;

  @Column(name = "equipment_type", length = 10)
  private String equipmentType;

  @Column(name = "status_code", length = 10)
  private String statusCode;

  @Column(name = "created_at")
  private LocalDateTime createdAt;

  @Column(name = "installed_at")
  private LocalDateTime installedAt;

  @Column(name = "expired_at")
  private LocalDateTime expiredAt;

  @Version
  @Column(name = "version")
  private Integer version;

  // Default constructor
  public Equipment() {}

  // Constructor with required fields
  public Equipment(String equipmentId, String facilityId) {
    this.equipmentId = equipmentId;
    this.facilityId = facilityId;
    this.createdAt = LocalDateTime.now();
    this.version = 1;
  }

  // Getters and Setters
  public String getEquipmentId() {
    return equipmentId;
  }

  public void setEquipmentId(String equipmentId) {
    this.equipmentId = equipmentId;
  }

  public String getEquipmentLocation() {
    return equipmentLocation;
  }

  public void setEquipmentLocation(String equipmentLocation) {
    this.equipmentLocation = equipmentLocation;
  }

  public String getFacilityId() {
    return facilityId;
  }

  public void setFacilityId(String facilityId) {
    this.facilityId = facilityId;
  }

  public String getEquipmentType() {
    return equipmentType;
  }

  public void setEquipmentType(String equipmentType) {
    this.equipmentType = equipmentType;
  }

  public String getStatusCode() {
    return statusCode;
  }

  public void setStatusCode(String statusCode) {
    this.statusCode = statusCode;
  }

  public LocalDateTime getCreatedAt() {
    return createdAt;
  }

  public void setCreatedAt(LocalDateTime createdAt) {
    this.createdAt = createdAt;
  }

  public LocalDateTime getInstalledAt() {
    return installedAt;
  }

  public void setInstalledAt(LocalDateTime installedAt) {
    this.installedAt = installedAt;
  }

  public LocalDateTime getExpiredAt() {
    return expiredAt;
  }

  public void setExpiredAt(LocalDateTime expiredAt) {
    this.expiredAt = expiredAt;
  }

  public Integer getVersion() {
    return version;
  }

  public void setVersion(Integer version) {
    this.version = version;
  }

  @PreUpdate
  public void preUpdate() {
    // 업데이트 시 버전 증가 로직은 필요에 따라 구현
  }
}
