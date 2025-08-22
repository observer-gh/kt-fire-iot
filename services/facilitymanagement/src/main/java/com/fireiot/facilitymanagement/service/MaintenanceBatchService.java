package com.fireiot.facilitymanagement.service;

import com.fireiot.facilitymanagement.entity.Equipment;
import com.fireiot.facilitymanagement.entity.EquipmentMaintenance;
import com.fireiot.facilitymanagement.enums.MaintenanceType;
import com.fireiot.facilitymanagement.events.MaintenanceRequested;
import com.fireiot.facilitymanagement.publisher.MaintenanceEventPublisher;
import com.fireiot.facilitymanagement.repository.EquipmentMaintenanceRepository;
import com.fireiot.facilitymanagement.repository.EquipmentRepository;
import com.fireiot.facilitymanagement.service.RiskScoringService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Random;
import java.util.UUID;

@Service
public class MaintenanceBatchService {

  private static final Logger logger = LoggerFactory.getLogger(MaintenanceBatchService.class);

  @Autowired
  private EquipmentRepository equipmentRepository;

  @Autowired
  private EquipmentMaintenanceRepository equipmentMaintenanceRepository;

  @Autowired
  private MaintenanceEventPublisher maintenanceEventPublisher;

  @Autowired
  private RiskScoringService riskScoringService;

  private final Random random = new Random();

  // 매일 오전 8시에 실행
  @Scheduled(cron = "0 0 8 * * ?")
  @Transactional
  public void processExpiringEquipmentMaintenance() {
    logger.info("Starting daily maintenance batch process for expiring equipment");

    try {
      // 1개월 이하로 만료되는 장비 조회
      LocalDateTime oneMonthFromNow = LocalDateTime.now().plusMonths(1);
      List<Equipment> expiringEquipment =
          equipmentRepository.findByExpiredAtBefore(oneMonthFromNow);

      logger.info("Found {} equipment items expiring within 1 month", expiringEquipment.size());

      for (Equipment equipment : expiringEquipment) {
        try {
          // 위험도 스코어링을 통한 유지보수 요청 생성
          EquipmentMaintenance maintenance = createMaintenanceRequestWithRiskScoring(equipment);

          // 데이터베이스에 저장
          equipmentMaintenanceRepository.save(maintenance);

          // MaintenanceRequested 이벤트 발행
          publishMaintenanceRequestedEvent(maintenance, equipment);

          logger.info(
              "Successfully processed maintenance request with risk scoring for equipment: {}",
              equipment.getEquipmentId());

        } catch (Exception e) {
          logger.error("Failed to process maintenance request for equipment: {}",
              equipment.getEquipmentId(), e);
        }
      }

      logger.info("Completed daily maintenance batch process. Processed {} equipment items",
          expiringEquipment.size());

    } catch (Exception e) {
      logger.error("Failed to execute daily maintenance batch process", e);
    }
  }

  /**
   * 위험도 스코어링을 통한 유지보수 요청 생성
   */
  private EquipmentMaintenance createMaintenanceRequestWithRiskScoring(Equipment equipment) {
    EquipmentMaintenance maintenance =
        new EquipmentMaintenance(generateMaintenanceLogId(), equipment.getEquipmentId());

    // 기본 정보 설정
    maintenance.setFacilityId(equipment.getFacilityId());
    maintenance.setEquipmentLocation(equipment.getEquipmentLocation());

    // 위험도 스코어링을 통한 유지보수 타입 결정
    maintenance.setMaintenanceType(determineMaintenanceTypeByRisk(equipment));

    // 예정 날짜 설정 (만료일을 초과하지 않는 랜덤한 날짜)
    maintenance.setScheduledDate(generateRandomScheduledDate(equipment.getExpiredAt()));

    // 담당자 랜덤 선택
    maintenance.setManager(getRandomManager());

    // 상태 코드 초기화
    maintenance.setStatusCode("업무할당");

    // 다음 예정 날짜 설정 (위험도에 따라 조정)
    maintenance.setNextScheduledDate(determineNextScheduledDateByRisk(equipment, maintenance));

    // 위험도 기반 노트 생성
    maintenance.setNote(generateMaintenanceNoteWithRisk(equipment, maintenance));

    return maintenance;
  }

  /**
   * 위험도에 따른 유지보수 타입 결정
   */
  private MaintenanceType determineMaintenanceTypeByRisk(Equipment equipment) {
    try {
      // 위험도 계산을 위한 가상의 MaintenanceRequested 이벤트 생성
      MaintenanceRequested virtualEvent = createVirtualMaintenanceRequest(equipment);

      // 위험도 스코어링 수행
      double riskScore = riskScoringService.calculateRiskScore(virtualEvent);

      // 위험도에 따른 유지보수 타입 결정
      if (riskScore >= 0.8) {
        return MaintenanceType.REPLACE; // 매우 높은 위험도: 교체
      } else if (riskScore >= 0.6) {
        return MaintenanceType.REPAIR; // 높은 위험도: 수리
      } else if (riskScore >= 0.4) {
        return MaintenanceType.INSPECTION; // 보통 위험도: 점검
      } else if (riskScore >= 0.2) {
        return MaintenanceType.CALIBRATE; // 낮은 위험도: 보정
      } else {
        return MaintenanceType.CLEAN; // 매우 낮은 위험도: 청소
      }

    } catch (Exception e) {
      logger.warn("Failed to calculate risk score for equipment: {}, using random type",
          equipment.getEquipmentId());
      return getRandomMaintenanceType();
    }
  }

  /**
   * 위험도에 따른 다음 예정 날짜 결정
   */
  private LocalDateTime determineNextScheduledDateByRisk(Equipment equipment,
      EquipmentMaintenance maintenance) {
    try {
      // 위험도 계산을 위한 가상의 MaintenanceRequested 이벤트 생성
      MaintenanceRequested virtualEvent = createVirtualMaintenanceRequest(equipment);

      // 위험도 스코어링 수행
      double riskScore = riskScoringService.calculateRiskScore(virtualEvent);

      // 위험도에 따른 다음 예정 날짜 조정
      if (riskScore >= 0.8) {
        return maintenance.getScheduledDate().plusMonths(3); // 매우 높은 위험도: 3개월 후
      } else if (riskScore >= 0.6) {
        return maintenance.getScheduledDate().plusMonths(4); // 높은 위험도: 4개월 후
      } else if (riskScore >= 0.4) {
        return maintenance.getScheduledDate().plusMonths(6); // 보통 위험도: 6개월 후
      } else if (riskScore >= 0.2) {
        return maintenance.getScheduledDate().plusMonths(8); // 낮은 위험도: 8개월 후
      } else {
        return maintenance.getScheduledDate().plusMonths(12); // 매우 낮은 위험도: 12개월 후
      }

    } catch (Exception e) {
      logger.warn("Failed to calculate risk score for equipment: {}, using default 6 months",
          equipment.getEquipmentId());
      return maintenance.getScheduledDate().plusMonths(6);
    }
  }

  /**
   * 위험도 기반 유지보수 노트 생성
   */
  private String generateMaintenanceNoteWithRisk(Equipment equipment,
      EquipmentMaintenance maintenance) {
    try {
      // 위험도 계산을 위한 가상의 MaintenanceRequested 이벤트 생성
      MaintenanceRequested virtualEvent = createVirtualMaintenanceRequest(equipment);

      // 위험도 스코어링 수행
      double riskScore = riskScoringService.calculateRiskScore(virtualEvent);
      String riskLevel = riskScoringService.getRiskLevel(riskScore).getDescription();
      String riskRecommendation = riskScoringService.generateRecommendation(riskScore);

      StringBuilder note = new StringBuilder();

      note.append("장비 유지보수 요청 (위험도 기반) - ");
      note.append("장비ID: ").append(equipment.getEquipmentId()).append(", ");
      note.append("위치: ")
          .append(
              equipment.getEquipmentLocation() != null ? equipment.getEquipmentLocation() : "미지정")
          .append(", ");
      note.append("유지보수타입: ").append(maintenance.getMaintenanceType()).append(", ");
      note.append("위험도점수: ").append(String.format("%.3f", riskScore)).append(" (").append(riskLevel)
          .append("), ");

      if (equipment.getExpiredAt() != null) {
        long daysUntilExpiry =
            ChronoUnit.DAYS.between(LocalDateTime.now(), equipment.getExpiredAt());
        if (daysUntilExpiry > 0) {
          note.append("만료일까지 ").append(daysUntilExpiry).append("일 남음. ");
        } else {
          note.append("만료일이 지남. ");
        }
      }

      note.append("권장사항: ").append(riskRecommendation);

      return note.toString();

    } catch (Exception e) {
      logger.warn("Failed to generate risk-based note for equipment: {}, using basic note",
          equipment.getEquipmentId());
      return generateMaintenanceNote(equipment, maintenance);
    }
  }

  /**
   * 위험도 계산을 위한 가상의 MaintenanceRequested 이벤트 생성
   */
  private MaintenanceRequested createVirtualMaintenanceRequest(Equipment equipment) {
    MaintenanceRequested virtualEvent = new MaintenanceRequested();
    virtualEvent.setVersion(1);
    virtualEvent.setMaintenanceLogId("VIRTUAL_" + equipment.getEquipmentId());
    virtualEvent.setEquipmentId(equipment.getEquipmentId());
    virtualEvent.setFacilityId(equipment.getFacilityId());
    virtualEvent.setMaintenanceType(MaintenanceType.INSPECTION); // 기본값
    virtualEvent.setScheduledDate(LocalDateTime.now().plusDays(7)
        .atZone(java.time.ZoneId.systemDefault()).toOffsetDateTime());
    virtualEvent.setNote("가상 유지보수 요청 - 위험도 계산용");
    virtualEvent.setRequestedAt(
        LocalDateTime.now().atZone(java.time.ZoneId.systemDefault()).toOffsetDateTime());

    return virtualEvent;
  }

  /**
   * 장비 정보를 기반으로 유지보수 요청 생성 (기본 방식)
   */
  private EquipmentMaintenance createMaintenanceRequest(Equipment equipment) {
    EquipmentMaintenance maintenance =
        new EquipmentMaintenance(generateMaintenanceLogId(), equipment.getEquipmentId());

    // 기본 정보 설정
    maintenance.setFacilityId(equipment.getFacilityId());
    maintenance.setEquipmentLocation(equipment.getEquipmentLocation());

    // 랜덤 유지보수 타입 선택
    maintenance.setMaintenanceType(getRandomMaintenanceType());

    // 예정 날짜 설정 (만료일을 초과하지 않는 랜덤한 날짜)
    maintenance.setScheduledDate(generateRandomScheduledDate(equipment.getExpiredAt()));

    // 담당자 랜덤 선택
    maintenance.setManager(getRandomManager());

    // 상태 코드 초기화
    maintenance.setStatusCode("업무할당");

    // 다음 예정 날짜 설정 (기본 6개월 후)
    maintenance.setNextScheduledDate(maintenance.getScheduledDate().plusMonths(6));

    // 기본 노트 생성
    maintenance.setNote(generateMaintenanceNote(equipment, maintenance));

    return maintenance;
  }

  /**
   * 유지보수 로그 ID 생성
   */
  private String generateMaintenanceLogId() {
    return "MAINT_" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
  }

  /**
   * 랜덤 유지보수 타입 선택
   */
  private MaintenanceType getRandomMaintenanceType() {
    MaintenanceType[] types = MaintenanceType.values();
    return types[random.nextInt(types.length)];
  }

  /**
   * 만료일을 초과하지 않는 랜덤한 예정 날짜 생성
   */
  private LocalDateTime generateRandomScheduledDate(LocalDateTime expiredAt) {
    LocalDateTime now = LocalDateTime.now();
    LocalDateTime maxDate = expiredAt != null ? expiredAt.minusDays(7) : now.plusMonths(1);

    if (maxDate.isBefore(now)) {
      maxDate = now.plusDays(7); // 최소 1주일 후
    }

    long daysBetween = ChronoUnit.DAYS.between(now, maxDate);
    long randomDays = random.nextInt((int) daysBetween + 1);

    return now.plusDays(randomDays);
  }

  /**
   * 랜덤 담당자 선택
   */
  private String getRandomManager() {
    String[] managers = {"박희원", "길현준", "하태균"};
    return managers[random.nextInt(managers.length)];
  }

  /**
   * 유지보수 노트 생성
   */
  private String generateMaintenanceNote(Equipment equipment, EquipmentMaintenance maintenance) {
    StringBuilder note = new StringBuilder();

    note.append("장비 유지보수 요청 - ");
    note.append("장비ID: ").append(equipment.getEquipmentId()).append(", ");
    note.append("위치: ")
        .append(equipment.getEquipmentLocation() != null ? equipment.getEquipmentLocation() : "미지정")
        .append(", ");
    note.append("유지보수타입: ").append(maintenance.getMaintenanceType()).append(", ");

    if (equipment.getExpiredAt() != null) {
      long daysUntilExpiry = ChronoUnit.DAYS.between(LocalDateTime.now(), equipment.getExpiredAt());
      if (daysUntilExpiry > 0) {
        note.append("만료일까지 ").append(daysUntilExpiry).append("일 남음. ");
      } else {
        note.append("만료일이 지남. ");
      }
    }

    note.append("정기 점검 및 유지보수가 필요합니다.");

    return note.toString();
  }

  /**
   * MaintenanceRequested 이벤트 발행
   */
  private void publishMaintenanceRequestedEvent(EquipmentMaintenance maintenance,
      Equipment equipment) {
    try {
      MaintenanceRequested event = new MaintenanceRequested();
      event.setVersion(1);
      event.setMaintenanceLogId(maintenance.getMaintenanceLogId());
      event.setEquipmentId(maintenance.getEquipmentId());
      event.setFacilityId(maintenance.getFacilityId());
      event.setMaintenanceType(maintenance.getMaintenanceType());
      event.setScheduledDate(maintenance.getScheduledDate().atZone(java.time.ZoneId.systemDefault())
          .toOffsetDateTime());
      event.setNote(maintenance.getNote());
      event.setRequestedAt(
          maintenance.getCreatedAt().atZone(java.time.ZoneId.systemDefault()).toOffsetDateTime());

      maintenanceEventPublisher.publishMaintenanceRequested(event);

      logger.info("Published MaintenanceRequested event for maintenance: {}",
          maintenance.getMaintenanceLogId());

    } catch (Exception e) {
      logger.error("Failed to publish MaintenanceRequested event for maintenance: {}",
          maintenance.getMaintenanceLogId(), e);
    }
  }

}
