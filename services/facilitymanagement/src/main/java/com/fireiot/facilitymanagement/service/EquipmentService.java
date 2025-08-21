package com.fireiot.facilitymanagement.service;

import com.fireiot.facilitymanagement.entity.Equipment;
import com.fireiot.facilitymanagement.events.EquipmentStateUpdateRequested;
import com.fireiot.facilitymanagement.repository.EquipmentRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.util.Objects;
import java.util.Optional;

@Service
public class EquipmentService {

  private static final Logger logger = LoggerFactory.getLogger(EquipmentService.class);

  @Autowired
  private EquipmentRepository equipmentRepository;

  /**
   * 장비 상태 업데이트 이벤트를 처리하여 데이터베이스를 업데이트합니다.
   */
  @Transactional
  public boolean updateEquipmentState(EquipmentStateUpdateRequested event) {
    try {
      // 입력 검증
      if (event == null || event.getEquipmentId() == null) {
        logger.error("Invalid event or equipmentId is null");
        return false;
      }

      logger.info("Processing equipment state update for equipment: {}", event.getEquipmentId());

      // 기존 장비 조회
      Optional<Equipment> existingEquipment =
          equipmentRepository.findByEquipmentId(event.getEquipmentId());

      if (existingEquipment.isPresent()) {
        // 기존 장비 정보 업데이트
        return updateExistingEquipment(existingEquipment.get(), event);
      } else {
        // 새 장비 생성 (facilityId가 있는 경우에만)
        if (event.getFacilityId() != null) {
          return createNewEquipment(event);
        } else {
          logger.warn("Cannot create new equipment without facilityId for equipment: {}",
              event.getEquipmentId());
          return false;
        }
      }

    } catch (Exception e) {
      logger.error("Failed to update equipment state for equipment: {}", event.getEquipmentId(), e);
      return false;
    }
  }

  /**
   * 기존 장비 정보 업데이트
   */
  private boolean updateExistingEquipment(Equipment equipment,
      EquipmentStateUpdateRequested event) {
    try {
      // 입력 검증
      if (event.getChanges() == null) {
        logger.warn("No changes provided for equipment: {}", equipment.getEquipmentId());
        return true;
      }

      // 변경사항이 있는 경우에만 업데이트
      boolean hasChanges = false;

      // 상태 코드 업데이트
      if (event.getChanges().getStatusCode() != null
          && !Objects.equals(event.getChanges().getStatusCode(), equipment.getStatusCode())) {
        equipment.setStatusCode(event.getChanges().getStatusCode());
        hasChanges = true;
      }

      // 위치 업데이트
      if (event.getChanges().getEquipmentLocation() != null && !Objects
          .equals(event.getChanges().getEquipmentLocation(), equipment.getEquipmentLocation())) {
        equipment.setEquipmentLocation(event.getChanges().getEquipmentLocation());
        hasChanges = true;
      }

      // 만료일 업데이트
      if (event.getChanges().getExpiredAt() != null) {
        LocalDateTime expiredAt = convertToLocalDateTime(event.getChanges().getExpiredAt());
        if (!Objects.equals(expiredAt, equipment.getExpiredAt())) {
          equipment.setExpiredAt(expiredAt);
          hasChanges = true;
        }
      }

      if (hasChanges) {
        equipment.setVersion(equipment.getVersion() + 1);
        equipmentRepository.save(equipment);

        logger.info("Successfully updated equipment: {}, Status: {}, Location: {}, ExpiredAt: {}",
            equipment.getEquipmentId(), equipment.getStatusCode(), equipment.getEquipmentLocation(),
            equipment.getExpiredAt());
        return true;
      } else {
        logger.info("No changes detected for equipment: {}", equipment.getEquipmentId());
        return true;
      }

    } catch (Exception e) {
      logger.error("Failed to update existing equipment: {}", equipment.getEquipmentId(), e);
      return false;
    }
  }

  /**
   * 새 장비 생성
   */
  private boolean createNewEquipment(EquipmentStateUpdateRequested event) {
    try {
      // 입력 검증
      if (event.getChanges() == null) {
        logger.error("Cannot create equipment without changes for equipment: {}",
            event.getEquipmentId());
        return false;
      }

      Equipment newEquipment = new Equipment(event.getEquipmentId(), event.getFacilityId());

      // 기본 정보 설정
      newEquipment.setEquipmentLocation(event.getChanges().getEquipmentLocation());
      newEquipment.setStatusCode(event.getChanges().getStatusCode());
      newEquipment.setExpiredAt(convertToLocalDateTime(event.getChanges().getExpiredAt()));
      newEquipment.setCreatedAt(LocalDateTime.now());
      newEquipment.setInstalledAt(LocalDateTime.now());

      equipmentRepository.save(newEquipment);

      logger.info("Successfully created new equipment: {}, Status: {}, Location: {}",
          newEquipment.getEquipmentId(), newEquipment.getStatusCode(),
          newEquipment.getEquipmentLocation());
      return true;

    } catch (Exception e) {
      logger.error("Failed to create new equipment: {}", event.getEquipmentId(), e);
      return false;
    }
  }

  /**
   * OffsetDateTime을 LocalDateTime으로 변환
   */
  private LocalDateTime convertToLocalDateTime(OffsetDateTime offsetDateTime) {
    if (offsetDateTime == null) {
      return null;
    }
    return offsetDateTime.toLocalDateTime();
  }

  /**
   * 장비 상태 조회
   */
  public Optional<Equipment> getEquipmentById(String equipmentId) {
    return equipmentRepository.findByEquipmentId(equipmentId);
  }

  /**
   * 시설별 장비 목록 조회
   */
  public java.util.List<Equipment> getEquipmentByFacility(String facilityId) {
    return equipmentRepository.findByFacilityId(facilityId);
  }

  /**
   * 장비 상태별 목록 조회
   */
  public java.util.List<Equipment> getEquipmentByStatus(String statusCode) {
    return equipmentRepository.findByStatusCode(statusCode);
  }
}
