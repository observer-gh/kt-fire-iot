package com.fireiot.facilitymanagement.service;

import com.fireiot.facilitymanagement.entity.EquipmentMaintenance;
import com.fireiot.facilitymanagement.enums.MaintenanceType;
import com.fireiot.facilitymanagement.repository.EquipmentMaintenanceRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class EquipmentMaintenanceService {

  @Autowired
  private EquipmentMaintenanceRepository maintenanceRepository;

  // 유지보수 기록 생성
  public EquipmentMaintenance createMaintenanceRecord(EquipmentMaintenance maintenance) {
    maintenance.setCreatedAt(LocalDateTime.now());
    maintenance.setUpdatedAt(LocalDateTime.now());
    maintenance.setVersion(1);
    return maintenanceRepository.save(maintenance);
  }

  // 유지보수 기록 조회 (ID로)
  @Transactional(readOnly = true)
  public Optional<EquipmentMaintenance> getMaintenanceById(String maintenanceLogId) {
    return maintenanceRepository.findById(maintenanceLogId);
  }

  // 모든 유지보수 기록 조회
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> getAllMaintenanceRecords() {
    return maintenanceRepository.findAll();
  }

  // 장비별 유지보수 기록 조회
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> getMaintenanceByEquipment(String equipmentId) {
    return maintenanceRepository.findByEquipmentId(equipmentId);
  }

  // 시설별 유지보수 기록 조회
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> getMaintenanceByFacility(String facilityId) {
    return maintenanceRepository.findByFacilityId(facilityId);
  }

  // 유지보수 타입별 조회
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> getMaintenanceByType(MaintenanceType maintenanceType) {
    return maintenanceRepository.findByMaintenanceType(maintenanceType);
  }

  // 상태별 유지보수 기록 조회
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> getMaintenanceByStatus(String statusCode) {
    return maintenanceRepository.findByStatusCode(statusCode);
  }

  // 예정된 유지보수 조회
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> getScheduledMaintenance(LocalDateTime startDate,
      LocalDateTime endDate) {
    return maintenanceRepository.findByScheduledDateBetween(startDate, endDate);
  }

  // 수행된 유지보수 조회
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> getPerformedMaintenance(LocalDateTime startDate,
      LocalDateTime endDate) {
    return maintenanceRepository.findByPerformedDateBetween(startDate, endDate);
  }

  // 담당자별 유지보수 기록 조회
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> getMaintenanceByManager(String manager) {
    return maintenanceRepository.findByManager(manager);
  }

  // 장비 및 시설별 유지보수 기록 조회
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> getMaintenanceByEquipmentAndFacility(String equipmentId,
      String facilityId) {
    return maintenanceRepository.findByEquipmentIdAndFacilityId(equipmentId, facilityId);
  }

  // 예정일이 지난 미수행 유지보수 조회
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> getOverdueMaintenance() {
    return maintenanceRepository.findOverdueMaintenance(LocalDateTime.now());
  }

  // 다음 예정 유지보수 조회
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> getNextScheduledMaintenance(String equipmentId) {
    return maintenanceRepository.findNextScheduledMaintenance(equipmentId, LocalDateTime.now());
  }

  // 복합 검색
  @Transactional(readOnly = true)
  public List<EquipmentMaintenance> searchMaintenance(String equipmentId, String facilityId,
      MaintenanceType maintenanceType, String statusCode, String manager) {
    return maintenanceRepository.findMaintenanceByCriteria(equipmentId, facilityId, maintenanceType,
        statusCode, manager);
  }

  // 유지보수 기록 업데이트
  public EquipmentMaintenance updateMaintenanceRecord(String maintenanceLogId,
      EquipmentMaintenance maintenanceDetails) {
    Optional<EquipmentMaintenance> existingMaintenance =
        maintenanceRepository.findById(maintenanceLogId);
    if (existingMaintenance.isPresent()) {
      EquipmentMaintenance maintenance = existingMaintenance.get();

      if (maintenanceDetails.getEquipmentLocation() != null) {
        maintenance.setEquipmentLocation(maintenanceDetails.getEquipmentLocation());
      }
      if (maintenanceDetails.getMaintenanceType() != null) {
        maintenance.setMaintenanceType(maintenanceDetails.getMaintenanceType());
      }
      if (maintenanceDetails.getScheduledDate() != null) {
        maintenance.setScheduledDate(maintenanceDetails.getScheduledDate());
      }
      if (maintenanceDetails.getPerformedDate() != null) {
        maintenance.setPerformedDate(maintenanceDetails.getPerformedDate());
      }
      if (maintenanceDetails.getManager() != null) {
        maintenance.setManager(maintenanceDetails.getManager());
      }
      if (maintenanceDetails.getStatusCode() != null) {
        maintenance.setStatusCode(maintenanceDetails.getStatusCode());
      }
      if (maintenanceDetails.getNextScheduledDate() != null) {
        maintenance.setNextScheduledDate(maintenanceDetails.getNextScheduledDate());
      }
      if (maintenanceDetails.getNote() != null) {
        maintenance.setNote(maintenanceDetails.getNote());
      }

      maintenance.setUpdatedAt(LocalDateTime.now());
      maintenance.setVersion(maintenance.getVersion() + 1);
      return maintenanceRepository.save(maintenance);
    }
    throw new RuntimeException("Maintenance record not found with id: " + maintenanceLogId);
  }

  // 유지보수 수행 완료 처리
  public EquipmentMaintenance completeMaintenance(String maintenanceLogId, String note) {
    Optional<EquipmentMaintenance> existingMaintenance =
        maintenanceRepository.findById(maintenanceLogId);
    if (existingMaintenance.isPresent()) {
      EquipmentMaintenance maintenance = existingMaintenance.get();
      maintenance.setPerformedDate(LocalDateTime.now());
      maintenance.setStatusCode("COMPLETED");
      if (note != null) {
        maintenance.setNote(note);
      }
      maintenance.setUpdatedAt(LocalDateTime.now());
      maintenance.setVersion(maintenance.getVersion() + 1);
      return maintenanceRepository.save(maintenance);
    }
    throw new RuntimeException("Maintenance record not found with id: " + maintenanceLogId);
  }

  // 유지보수 기록 삭제
  public void deleteMaintenanceRecord(String maintenanceLogId) {
    if (maintenanceRepository.existsById(maintenanceLogId)) {
      maintenanceRepository.deleteById(maintenanceLogId);
    } else {
      throw new RuntimeException("Maintenance record not found with id: " + maintenanceLogId);
    }
  }

  // 시설별 유지보수 통계
  @Transactional(readOnly = true)
  public List<Object[]> getMaintenanceStatisticsByFacility() {
    return maintenanceRepository.getMaintenanceStatisticsByFacility();
  }

  // 장비별 유지보수 이력 수 조회
  @Transactional(readOnly = true)
  public long getMaintenanceCountByEquipment(String equipmentId) {
    return maintenanceRepository.countByEquipmentId(equipmentId);
  }

  // 유지보수 기록 존재 여부 확인
  @Transactional(readOnly = true)
  public boolean maintenanceRecordExists(String maintenanceLogId) {
    return maintenanceRepository.existsById(maintenanceLogId);
  }
}

