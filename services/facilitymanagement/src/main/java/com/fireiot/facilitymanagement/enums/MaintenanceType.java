package com.fireiot.facilitymanagement.enums;

/**
 * 유지보수 타입을 정의하는 enum
 */
public enum MaintenanceType {
  INSPECTION("점검"),
  REPAIR("수리"),
  REPLACE("교체"),
  CLEAN("청소"),
  CALIBRATE("보정"),
  OTHER("기타");

  private final String description;

  MaintenanceType(String description) {
    this.description = description;
  }

  public String getDescription() {
    return description;
  }
}
