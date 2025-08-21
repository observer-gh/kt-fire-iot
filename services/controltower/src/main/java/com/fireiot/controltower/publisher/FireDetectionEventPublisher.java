package com.fireiot.controltower.publisher;

import com.fireiot.controltower.events.FireDetectionNotified;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
public class FireDetectionEventPublisher {

  private static final Logger logger = LoggerFactory.getLogger(FireDetectionEventPublisher.class);

  private final KafkaTemplate<String, Object> kafkaTemplate;

  @Value("${kafka.topics.fire-detection-notified:controlTower.fireDetectionNotified}")
  private String fireDetectionTopic;

  public FireDetectionEventPublisher(KafkaTemplate<String, Object> kafkaTemplate) {
    this.kafkaTemplate = kafkaTemplate;
  }

  public void publishFireDetectionNotification(FireDetectionNotified notification) {
    String topic = fireDetectionTopic;
    logger.info("Publishing fire detection notification to topic: {}, alertId: {}, cctvId: {}",
        topic, notification.getAlertId(), notification.getCctvId());

    try {
      kafkaTemplate.send(topic, notification.getAlertId(), notification);
      logger.info("Successfully published fire detection notification: {} for CCTV: {}",
          notification.getAlertId(), notification.getCctvId());
    } catch (Exception e) {
      logger.error("Failed to publish fire detection notification: {} for CCTV: {}",
          notification.getAlertId(), notification.getCctvId(), e);
      // TODO: Implement retry mechanism or dead letter queue
    }
  }
}
