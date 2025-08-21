package com.fireiot.facilitymanagement.consumer;

import com.fireiot.facilitymanagement.events.MaintenanceRequested;
import com.fireiot.facilitymanagement.events.EquipmentStateUpdateRequested;
import com.fireiot.facilitymanagement.service.RiskScoringService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

@Component
public class MaintenanceEventConsumer {

  private static final Logger logger = LoggerFactory.getLogger(MaintenanceEventConsumer.class);

  @Autowired
  private RiskScoringService riskScoringService;

  /**
   * 유지보수 요청 이벤트를 수신하여 위험도 분석 수행
   */
  @KafkaListener(
      topics = "${kafka.topics.maintenance-requested:facilitymanagement.maintenanceRequested}",
      groupId = "${spring.kafka.consumer.group-id}")
  public void consumeMaintenanceRequested(@Payload MaintenanceRequested event,
      @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
      @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
      @Header(KafkaHeaders.OFFSET) long offset) {

    logger.info("Received maintenance requested event from topic: {}, partition: {}, offset: {}",
        topic, partition, offset);
    logger.info("Event details: maintenanceLogId={}, equipmentId={}, maintenanceType={}",
        event.getMaintenanceLogId(), event.getEquipmentId(), event.getMaintenanceType());

    try {
      // 위험도 점수 계산
      double riskScore = riskScoringService.calculateRiskScore(event);
      var riskLevel = riskScoringService.getRiskLevel(riskScore);
      String recommendation = riskScoringService.generateRecommendation(riskScore);

      logger.info(
          "Risk assessment completed for maintenance request {}: Score={:.3f}, Level={}, Recommendation={}",
          event.getMaintenanceLogId(), riskScore, riskLevel.getDescription(), recommendation);

      // 높은 위험도인 경우 경고 로그
      if (riskScoringService.isHighRisk(riskScore, 0.7)) {
        logger.warn("HIGH RISK maintenance request detected! ID: {}, Score: {:.3f}, Level: {}",
            event.getMaintenanceLogId(), riskScore, riskLevel.getDescription());
      }

      // TODO: 위험도 분석 결과를 데이터베이스에 저장
      // TODO: 필요시 알림 서비스로 위험도 정보 전송

    } catch (Exception e) {
      logger.error("Error processing maintenance requested event: {}", event.getMaintenanceLogId(),
          e);
      // TODO: Implement error handling (retry, dead letter queue, etc.)
    }
  }

  /**
   * 장비 상태 업데이트 요청 이벤트를 수신하여 위험도 분석 수행
   */
  @KafkaListener(
      topics = "${kafka.topics.equipment-state-update-requested:facilitymanagement.equipmentStateUpdateRequested}",
      groupId = "${spring.kafka.consumer.group-id}")
  public void consumeEquipmentStateUpdateRequested(@Payload EquipmentStateUpdateRequested event,
      @Header(KafkaHeaders.RECEIVED_TOPIC) String topic,
      @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
      @Header(KafkaHeaders.OFFSET) long offset) {

    logger.info(
        "Received equipment state update requested event from topic: {}, partition: {}, offset: {}",
        topic, partition, offset);
    logger.info("Event details: requestId={}, equipmentId={}, facilityId={}", event.getRequestId(),
        event.getEquipmentId(), event.getFacilityId());

    try {
      // 장비 상태 기반 위험도 점수 계산
      double riskScore = riskScoringService.calculateRiskScoreFromEquipmentState(event);
      var riskLevel = riskScoringService.getRiskLevel(riskScore);
      String recommendation = riskScoringService.generateRecommendation(riskScore);

      logger.info(
          "Risk assessment completed for equipment state update {}: Score={:.3f}, Level={}, Recommendation={}",
          event.getRequestId(), riskScore, riskLevel.getDescription(), recommendation);

      // 높은 위험도인 경우 경고 로그
      if (riskScoringService.isHighRisk(riskScore, 0.7)) {
        logger.warn("HIGH RISK equipment state update detected! ID: {}, Score: {:.3f}, Level: {}",
            event.getRequestId(), riskScore, riskLevel.getDescription());
      }

      // TODO: 위험도 분석 결과를 데이터베이스에 저장
      // TODO: 필요시 알림 서비스로 위험도 정보 전송

    } catch (Exception e) {
      logger.error("Error processing equipment state update requested event: {}",
          event.getRequestId(), e);
      // TODO: Implement error handling (retry, dead letter queue, etc.)
    }
  }
}

