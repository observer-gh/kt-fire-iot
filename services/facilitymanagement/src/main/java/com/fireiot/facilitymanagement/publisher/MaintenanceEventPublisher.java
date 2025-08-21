package com.fireiot.facilitymanagement.publisher;

import com.fireiot.facilitymanagement.events.MaintenanceRequested;
import com.fireiot.facilitymanagement.events.MaintenanceRequestedWithRisk;
import com.fireiot.facilitymanagement.service.RiskScoringService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class MaintenanceEventPublisher {

  private static final Logger logger = LoggerFactory.getLogger(MaintenanceEventPublisher.class);

  private final KafkaTemplate<String, Object> kafkaTemplate;
  private final RiskScoringService riskScoringService;

  public MaintenanceEventPublisher(KafkaTemplate<String, Object> kafkaTemplate,
      RiskScoringService riskScoringService) {
    this.kafkaTemplate = kafkaTemplate;
    this.riskScoringService = riskScoringService;
  }

  public void publishMaintenanceRequested(MaintenanceRequested event) {
    String topic = "maintenanceRequested";
    logger.info("Publishing maintenance requested event to topic: {}, maintenanceLogId: {}", topic,
        event.getMaintenanceLogId());

    try {
      // 위험도 스코어링 수행
      double riskScore = riskScoringService.calculateRiskScore(event);
      String riskLevel = riskScoringService.getRiskLevel(riskScore).getDescription();
      String riskRecommendation = riskScoringService.generateRecommendation(riskScore);

      // 위험도 정보를 포함한 이벤트 생성
      MaintenanceRequestedWithRisk eventWithRisk =
          new MaintenanceRequestedWithRisk(event, riskScore, riskLevel, riskRecommendation);

      // 위험도 정보와 함께 이벤트 발행
      kafkaTemplate.send(topic, event.getMaintenanceLogId(), eventWithRisk);

      logger.info(
          "Successfully published maintenance requested event with risk score {} ({}) for: {}",
          String.format("%.3f", riskScore), riskLevel, event.getMaintenanceLogId());

      // 높은 위험도인 경우 추가 로깅
      if (riskScoringService.isHighRisk(riskScore, 0.7)) {
        logger.warn(
            "HIGH RISK maintenance request detected! Score: {}, Level: {}, Recommendation: {}",
            String.format("%.3f", riskScore), riskLevel, riskRecommendation);
      }

    } catch (Exception e) {
      logger.error("Failed to publish maintenance requested event: {}", event.getMaintenanceLogId(),
          e);
      // TODO: Implement retry mechanism or dead letter queue
    }
  }
}
