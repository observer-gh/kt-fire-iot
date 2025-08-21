package com.fireiot.controltower.publisher;

import com.fireiot.controltower.events.WarningAlertIssued;
import com.fireiot.controltower.events.EmergencyAlertIssued;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class AlertEventPublisher {

  private static final Logger logger = LoggerFactory.getLogger(AlertEventPublisher.class);

  private final KafkaTemplate<String, Object> kafkaTemplate;

  @Value("${kafka.topics.warning-alert-issued:controltower.warningAlertIssued}")
  private String warningAlertTopic;

  @Value("${kafka.topics.emergency-alert-issued:controltower.emergencyAlertIssued}")
  private String emergencyAlertTopic;

  public AlertEventPublisher(KafkaTemplate<String, Object> kafkaTemplate) {
    this.kafkaTemplate = kafkaTemplate;
  }

  public void publishWarningAlert(WarningAlertIssued alert) {
    String topic = warningAlertTopic;
    logger.info("Publishing warning alert to topic: {}, alertId: {}", topic, alert.getAlertId());

    try {
      kafkaTemplate.send(topic, alert.getAlertId(), alert);
      logger.info("Successfully published warning alert: {}", alert.getAlertId());
    } catch (Exception e) {
      logger.error("Failed to publish warning alert: {}", alert.getAlertId(), e);
      // TODO: Implement retry mechanism or dead letter queue
    }
  }

  public void publishEmergencyAlert(EmergencyAlertIssued alert) {
    String topic = emergencyAlertTopic;
    logger.info("Publishing emergency alert to topic: {}, alertId: {}", topic, alert.getAlertId());

    try {
      kafkaTemplate.send(topic, alert.getAlertId(), alert);
      logger.info("Successfully published emergency alert: {}", alert.getAlertId());
    } catch (Exception e) {
      logger.error("Failed to publish emergency alert: {}", alert.getAlertId(), e);
      // TODO: Implement retry mechanism or dead letter queue
    }
  }
}
