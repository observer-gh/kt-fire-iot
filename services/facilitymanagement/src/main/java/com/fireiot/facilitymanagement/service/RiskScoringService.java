package com.fireiot.facilitymanagement.service;

import com.fireiot.facilitymanagement.events.MaintenanceRequested;
import com.fireiot.facilitymanagement.enums.MaintenanceType;
import com.fireiot.facilitymanagement.events.EquipmentStateUpdateRequested;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;

@Service
public class RiskScoringService {

  private static final Logger logger = LoggerFactory.getLogger(RiskScoringService.class);

  // 위험도 점수 범위: 0.0 (매우 낮음) ~ 1.0 (매우 높음)
  private static final double MIN_RISK_SCORE = 0.0;
  private static final double MAX_RISK_SCORE = 1.0;

  // 위험도 등급
  public enum RiskLevel {
    VERY_LOW(0.0, 0.2, "매우 낮음"), LOW(0.2, 0.4, "낮음"), MEDIUM(0.4, 0.6, "보통"), HIGH(0.6, 0.8,
        "높음"), VERY_HIGH(0.8, 1.0, "매우 높음");

    private final double minScore;
    private final double maxScore;
    private final String description;

    RiskLevel(double minScore, double maxScore, String description) {
      this.minScore = minScore;
      this.maxScore = maxScore;
      this.description = description;
    }

    public static RiskLevel fromScore(double score) {
      for (RiskLevel level : values()) {
        if (score >= level.minScore && score < level.maxScore) {
          return level;
        }
      }
      return VERY_HIGH; // 1.0인 경우
    }

    public String getDescription() {
      return description;
    }
  }

  /**
   * 유지보수 요청의 위험도를 스코어링합니다.
   * 
   * @param maintenanceRequest 유지보수 요청 이벤트
   * @return 위험도 점수 (0.0 ~ 1.0)
   */
  public double calculateRiskScore(MaintenanceRequested maintenanceRequest) {
    logger.info("Calculating risk score for maintenance request: {}",
        maintenanceRequest.getMaintenanceLogId());

    double riskScore = 0.0;

    // 1. 유지보수 타입별 위험도 (40% 가중치)
    riskScore += calculateMaintenanceTypeRisk(maintenanceRequest.getMaintenanceType()) * 0.4;

    // 2. 시설 위험도 (30% 가중치)
    riskScore += calculateFacilityRisk(maintenanceRequest.getFacilityId()) * 0.3;

    // 3. 장비 상태 위험도 (20% 가중치) - equipmentStateUpdateRequested 데이터 활용
    riskScore += calculateEquipmentRiskFromState(maintenanceRequest.getEquipmentId()) * 0.2;

    // 4. 긴급성 위험도 (10% 가중치)
    riskScore += calculateUrgencyRisk(maintenanceRequest.getScheduledDate()) * 0.1;

    // 점수 범위 제한
    riskScore = Math.max(MIN_RISK_SCORE, Math.min(MAX_RISK_SCORE, riskScore));

    RiskLevel riskLevel = RiskLevel.fromScore(riskScore);
    logger.info("Risk score calculated: {} ({}) for maintenance request: {}",
        String.format("%.3f", riskScore), riskLevel.getDescription(),
        maintenanceRequest.getMaintenanceLogId());

    return riskScore;
  }

  /**
   * 유지보수 타입별 위험도 계산
   */
  private double calculateMaintenanceTypeRisk(MaintenanceType maintenanceType) {
    return switch (maintenanceType) {
      case INSPECTION -> 0.1; // 점검: 매우 낮음
      case CLEAN -> 0.2; // 청소: 낮음
      case CALIBRATE -> 0.3; // 보정: 낮음
      case REPAIR -> 0.7; // 수리: 높음
      case REPLACE -> 0.8; // 교체: 높음
      case OTHER -> 0.5; // 기타: 보통
    };
  }

  /**
   * 시설별 위험도 계산 TODO: 실제 시설 데이터베이스에서 위험도 정보를 조회하도록 구현
   */
  private double calculateFacilityRisk(String facilityId) {
    if (facilityId == null) {
      return 0.5; // 기본값: 보통
    }

    // 시설 ID 패턴에 따른 위험도 계산 (예시)
    if (facilityId.startsWith("FAC001") || facilityId.startsWith("FAC005")) {
      return 0.8; // 공장: 높음
    } else if (facilityId.startsWith("FAC002")) {
      return 0.6; // 창고: 높음
    } else if (facilityId.startsWith("FAC003")) {
      return 0.3; // 사무실: 낮음
    } else if (facilityId.startsWith("FAC004")) {
      return 0.4; // 연구소: 낮음
    }

    return 0.5; // 기본값: 보통
  }

  /**
   * 장비별 위험도 계산 (기본 방식)
   */
  private double calculateEquipmentRisk(String equipmentId) {
    if (equipmentId == null) {
      return 0.5; // 기본값: 보통
    }

    // 장비 타입에 따른 위험도 계산 (예시)
    if (equipmentId.contains("DETECTOR") || equipmentId.contains("감지기")) {
      return 0.8; // 감지기: 높음 (안전 관련)
    } else if (equipmentId.contains("SENSOR") || equipmentId.contains("센서")) {
      return 0.6; // 센서: 높음 (데이터 수집)
    }

    return 0.5; // 기본값: 보통
  }

  /**
   * equipmentStateUpdateRequested 데이터를 활용한 장비 상태 위험도 계산 TODO: 실제로는 Consumer에서 받은 최신 장비 상태 데이터를 활용
   */
  private double calculateEquipmentRiskFromState(String equipmentId) {
    if (equipmentId == null) {
      return 0.5; // 기본값: 보통
    }

    // TODO: equipmentStateUpdateRequested 토픽에서 받은 최신 장비 상태 정보 활용
    // 예: 장비 위치, 상태 코드, 만료일 등

    // 현재는 기본 로직 사용
    return calculateEquipmentRisk(equipmentId);
  }

  /**
   * 긴급성 위험도 계산
   */
  private double calculateUrgencyRisk(OffsetDateTime scheduledDate) {
    if (scheduledDate == null) {
      return 0.3; // 일정 없음: 낮음
    }

    OffsetDateTime now = OffsetDateTime.now();
    long daysUntilScheduled = ChronoUnit.DAYS.between(now, scheduledDate);

    if (daysUntilScheduled < 0) {
      return 0.9; // 이미 지난 일정: 매우 높음
    } else if (daysUntilScheduled == 0) {
      return 0.8; // 오늘: 높음
    } else if (daysUntilScheduled <= 1) {
      return 0.7; // 내일: 높음
    } else if (daysUntilScheduled <= 3) {
      return 0.6; // 3일 이내: 높음
    } else if (daysUntilScheduled <= 7) {
      return 0.4; // 1주일 이내: 보통
    } else if (daysUntilScheduled <= 30) {
      return 0.2; // 1개월 이내: 낮음
    } else {
      return 0.1; // 1개월 이상: 매우 낮음
    }
  }

  /**
   * 위험도 등급 조회
   */
  public RiskLevel getRiskLevel(double riskScore) {
    return RiskLevel.fromScore(riskScore);
  }

  /**
   * 위험도가 임계값을 초과하는지 확인
   */
  public boolean isHighRisk(double riskScore, double threshold) {
    return riskScore >= threshold;
  }

  /**
   * 위험도 점수에 따른 권장사항 생성
   */
  public String generateRecommendation(double riskScore) {
    RiskLevel riskLevel = getRiskLevel(riskScore);

    return switch (riskLevel) {
      case VERY_LOW -> "정상적인 유지보수 계획으로 진행 가능합니다.";
      case LOW -> "일반적인 안전 수칙을 준수하여 진행하세요.";
      case MEDIUM -> "추가적인 안전 점검이 필요할 수 있습니다.";
      case HIGH -> "전문가의 감독 하에 진행하고, 안전 장비를 착용하세요.";
      case VERY_HIGH -> "즉시 중단하고 전문가와 상담 후 진행하세요. 긴급 상황일 수 있습니다.";
    };
  }

  /**
   * equipmentStateUpdateRequested 이벤트를 활용하여 장비 상태 기반 위험도 계산
   * 
   * @param equipmentStateUpdate 장비 상태 업데이트 이벤트
   * @return 위험도 점수 (0.0 ~ 1.0)
   */
  public double calculateRiskScoreFromEquipmentState(
      EquipmentStateUpdateRequested equipmentStateUpdate) {
    logger.info("Calculating risk score from equipment state update: {}",
        equipmentStateUpdate.getRequestId());

    double riskScore = 0.0;

    // 1. 장비 상태 코드 위험도 (50% 가중치)
    riskScore += calculateStatusCodeRisk(equipmentStateUpdate.getChanges().getStatusCode()) * 0.5;

    // 2. 장비 만료일 위험도 (30% 가중치)
    riskScore += calculateExpirationRisk(equipmentStateUpdate.getChanges().getExpiredAt()) * 0.3;

    // 3. 장비 위치 변경 위험도 (20% 가중치)
    riskScore +=
        calculateLocationChangeRisk(equipmentStateUpdate.getChanges().getEquipmentLocation()) * 0.2;

    // 점수 범위 제한
    riskScore = Math.max(MIN_RISK_SCORE, Math.min(MAX_RISK_SCORE, riskScore));

    RiskLevel riskLevel = RiskLevel.fromScore(riskScore);
    logger.info("Equipment state risk score calculated: {} ({}) for request: {}",
        String.format("%.3f", riskScore), riskLevel.getDescription(),
        equipmentStateUpdate.getRequestId());

    return riskScore;
  }

  /**
   * 장비 상태 코드별 위험도 계산
   */
  private double calculateStatusCodeRisk(String statusCode) {
    if (statusCode == null) {
      return 0.5; // 기본값: 보통
    }

    return switch (statusCode.toUpperCase()) {
      case "ACTIVE", "정상" -> 0.2; // 정상: 낮음
      case "WARNING", "경고" -> 0.6; // 경고: 높음
      case "ERROR", "오류" -> 0.8; // 오류: 높음
      case "MAINTENANCE", "유지보수" -> 0.7; // 유지보수: 높음
      case "OFFLINE", "오프라인" -> 0.9; // 오프라인: 매우 높음
      default -> 0.5; // 기본값: 보통
    };
  }

  /**
   * 장비 만료일 위험도 계산
   */
  private double calculateExpirationRisk(OffsetDateTime expiredAt) {
    if (expiredAt == null) {
      return 0.3; // 만료일 없음: 낮음
    }

    OffsetDateTime now = OffsetDateTime.now();
    long daysUntilExpiration = ChronoUnit.DAYS.between(now, expiredAt);

    if (daysUntilExpiration < 0) {
      return 0.9; // 이미 만료: 매우 높음
    } else if (daysUntilExpiration <= 7) {
      return 0.8; // 1주일 이내 만료: 높음
    } else if (daysUntilExpiration <= 30) {
      return 0.6; // 1개월 이내 만료: 높음
    } else if (daysUntilExpiration <= 90) {
      return 0.4; // 3개월 이내 만료: 보통
    } else {
      return 0.2; // 3개월 이상: 낮음
    }
  }

  /**
   * 장비 위치 변경 위험도 계산
   */
  private double calculateLocationChangeRisk(String newLocation) {
    if (newLocation == null) {
      return 0.3; // 위치 변경 없음: 낮음
    }

    // TODO: 이전 위치와 비교하여 위험도 계산
    // 예: 위험 구역으로 이동, 접근 제한 구역 등

    return 0.4; // 기본값: 보통
  }
}
