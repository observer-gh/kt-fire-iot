package com.fireiot.facilitymanagement.service;

import com.fireiot.facilitymanagement.entity.Equipment;
import com.fireiot.facilitymanagement.repository.EquipmentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class EquipmentService {

  @Autowired
  private EquipmentRepository equipmentRepository;

  // 장비 생성
  public Equipment createEquipment(Equipment equipment) {
    equipment.setCreatedAt(LocalDateTime.now());
    equipment.setVersion(1);
    return equipmentRepository.save(equipment);
  }

  // 장비 조회 (ID로)
  @Transactional(readOnly = true)
  public Optional<Equipment> getEquipmentById(String equipmentId) {
    return equipmentRepository.findById(equipmentId);
  }

  // 모든 장비 조회
  @Transactional(readOnly = true)
  public List<Equipment> getAllEquipment() {
    return equipmentRepository.findAll();
  }

  // 시설별 장비 조회
  @Transactional(readOnly = true)
  public List<Equipment> getEquipmentByFacility(String facilityId) {
    return equipmentRepository.findByFacilityId(facilityId);
  }

  // 장비 타입별 조회
  @Transactional(readOnly = true)
  public List<Equipment> getEquipmentByType(String equipmentType) {
    return equipmentRepository.findByEquipmentType(equipmentType);
  }

  // 상태별 장비 조회
  @Transactional(readOnly = true)
  public List<Equipment> getEquipmentByStatus(String statusCode) {
    return equipmentRepository.findByStatusCode(statusCode);
  }

  // 만료 예정 장비 조회
  @Transactional(readOnly = true)
  public List<Equipment> getExpiringEquipment(LocalDateTime expiryDate) {
    return equipmentRepository.findByExpiredAtBefore(expiryDate);
  }

  // 위치별 장비 조회
  @Transactional(readOnly = true)
  public List<Equipment> getEquipmentByLocation(String location) {
    return equipmentRepository.findByEquipmentLocation(location);
  }

  // 복합 검색
  @Transactional(readOnly = true)
  public List<Equipment> searchEquipment(String facilityId, String equipmentType, String statusCode,
      String location) {
    return equipmentRepository.findEquipmentByCriteria(facilityId, equipmentType, statusCode,
        location);
  }

  // 장비 업데이트
  public Equipment updateEquipment(String equipmentId, Equipment equipmentDetails) {
    Optional<Equipment> existingEquipment = equipmentRepository.findById(equipmentId);
    if (existingEquipment.isPresent()) {
      Equipment equipment = existingEquipment.get();

      if (equipmentDetails.getEquipmentLocation() != null) {
        equipment.setEquipmentLocation(equipmentDetails.getEquipmentLocation());
      }
      if (equipmentDetails.getEquipmentType() != null) {
        equipment.setEquipmentType(equipmentDetails.getEquipmentType());
      }
      if (equipmentDetails.getStatusCode() != null) {
        equipment.setStatusCode(equipmentDetails.getStatusCode());
      }
      if (equipmentDetails.getInstalledAt() != null) {
        equipment.setInstalledAt(equipmentDetails.getInstalledAt());
      }
      if (equipmentDetails.getExpiredAt() != null) {
        equipment.setExpiredAt(equipmentDetails.getExpiredAt());
      }

      equipment.setVersion(equipment.getVersion() + 1);
      return equipmentRepository.save(equipment);
    }
    throw new RuntimeException("Equipment not found with id: " + equipmentId);
  }

  // 장비 상태 업데이트
  public Equipment updateEquipmentStatus(String equipmentId, String statusCode) {
    Optional<Equipment> existingEquipment = equipmentRepository.findById(equipmentId);
    if (existingEquipment.isPresent()) {
      Equipment equipment = existingEquipment.get();
      equipment.setStatusCode(statusCode);
      equipment.setVersion(equipment.getVersion() + 1);
      return equipmentRepository.save(equipment);
    }
    throw new RuntimeException("Equipment not found with id: " + equipmentId);
  }

  // 장비 위치 업데이트
  public Equipment updateEquipmentLocation(String equipmentId, String location) {
    Optional<Equipment> existingEquipment = equipmentRepository.findById(equipmentId);
    if (existingEquipment.isPresent()) {
      Equipment equipment = existingEquipment.get();
      equipment.setEquipmentLocation(location);
      equipment.setVersion(equipment.getVersion() + 1);
      return equipmentRepository.save(equipment);
    }
    throw new RuntimeException("Equipment not found with id: " + equipmentId);
  }

  // 장비 삭제
  public void deleteEquipment(String equipmentId) {
    if (equipmentRepository.existsById(equipmentId)) {
      equipmentRepository.deleteById(equipmentId);
    } else {
      throw new RuntimeException("Equipment not found with id: " + equipmentId);
    }
  }

  // 시설별 장비 수 조회
  @Transactional(readOnly = true)
  public long getEquipmentCountByFacility(String facilityId) {
    return equipmentRepository.countByFacilityId(facilityId);
  }

  // 상태별 장비 통계
  @Transactional(readOnly = true)
  public List<Object[]> getEquipmentStatusStatistics() {
    return equipmentRepository.countByStatusCode();
  }

  // 장비 존재 여부 확인
  @Transactional(readOnly = true)
  public boolean equipmentExists(String equipmentId) {
    return equipmentRepository.existsById(equipmentId);
  }

  // 장비 상태 업데이트 이벤트 처리
  public boolean updateEquipmentState(
      com.fireiot.facilitymanagement.events.EquipmentStateUpdateRequested event) {
    try {
      // 입력 검증
      if (event == null || event.getEquipmentId() == null) {
        return false;
      }

      // 기존 장비 조회
      Optional<Equipment> existingEquipment = equipmentRepository.findById(event.getEquipmentId());

      if (existingEquipment.isPresent()) {
        // 기존 장비 정보 업데이트
        return updateExistingEquipment(existingEquipment.get(), event);
      } else {
        // 새 장비 생성 (facilityId가 있는 경우에만)
        if (event.getFacilityId() != null) {
          return createNewEquipment(event);
        } else {
          return false;
        }
      }

    } catch (Exception e) {
      return false;
    }
  }

  /**
   * 기존 장비 정보 업데이트
   */
  private boolean updateExistingEquipment(Equipment equipment,
      com.fireiot.facilitymanagement.events.EquipmentStateUpdateRequested event) {
    try {
      boolean hasChanges = false;

      // 상태 코드 업데이트
      if (event.getChanges() != null && event.getChanges().getStatusCode() != null) {
        equipment.setStatusCode(event.getChanges().getStatusCode());
        hasChanges = true;
      }

      // 위치 업데이트
      if (event.getChanges() != null && event.getChanges().getEquipmentLocation() != null) {
        equipment.setEquipmentLocation(event.getChanges().getEquipmentLocation());
        hasChanges = true;
      }

      // 만료일 업데이트
      if (event.getChanges() != null && event.getChanges().getExpiredAt() != null) {
        equipment.setExpiredAt(convertToLocalDateTime(event.getChanges().getExpiredAt()));
        hasChanges = true;
      }

      if (hasChanges) {
        equipment.setVersion(equipment.getVersion() + 1);
        equipmentRepository.save(equipment);
        return true;
      } else {
        return true; // 변경사항이 없어도 성공으로 처리
      }

    } catch (Exception e) {
      return false;
    }
  }

  /**
   * 새 장비 생성
   */
  private boolean createNewEquipment(
      com.fireiot.facilitymanagement.events.EquipmentStateUpdateRequested event) {
    try {
      Equipment newEquipment = new Equipment(event.getEquipmentId(), event.getFacilityId());

      // 기본 정보 설정
      if (event.getChanges() != null) {
        newEquipment.setEquipmentLocation(event.getChanges().getEquipmentLocation());
        newEquipment.setStatusCode(event.getChanges().getStatusCode());
        newEquipment.setExpiredAt(convertToLocalDateTime(event.getChanges().getExpiredAt()));
      }

      newEquipment.setCreatedAt(java.time.LocalDateTime.now());
      newEquipment.setInstalledAt(java.time.LocalDateTime.now());

      equipmentRepository.save(newEquipment);
      return true;

    } catch (Exception e) {
      return false;
    }
  }

  /**
   * OffsetDateTime을 LocalDateTime으로 변환
   */
  private java.time.LocalDateTime convertToLocalDateTime(java.time.OffsetDateTime offsetDateTime) {
    if (offsetDateTime == null) {
      return null;
    }
    return offsetDateTime.toLocalDateTime();
  }
}
