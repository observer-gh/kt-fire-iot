package com.fireiot.facilitymanagement.publisher;

import com.fireiot.facilitymanagement.events.MaintenanceRequested;
import com.fireiot.facilitymanagement.events.EquipmentStateUpdateRequested;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Component;

import java.util.concurrent.CompletableFuture;

@Component
public class MaintenanceEventPublisher {

  private static final Logger logger = LoggerFactory.getLogger(MaintenanceEventPublisher.class);

  @Autowired
  private KafkaTemplate<String, Object> kafkaTemplate;

  // Kafka 토픽 이름들
  private static final String MAINTENANCE_REQUESTED_TOPIC =
      "facilitymanagement.maintenanceRequested";
  private static final String EQUIPMENT_STATE_UPDATE_REQUESTED_TOPIC =
      "facilitymanagement.equipmentStateUpdateRequested";

  /**
   * 유지보수 요청 이벤트를 Kafka로 발행
   */
  public CompletableFuture<SendResult<String, Object>> publishMaintenanceRequested(
      MaintenanceRequested event) {
    logger.info("Publishing maintenance requested event: {}", event.getMaintenanceLogId());

    return kafkaTemplate.send(MAINTENANCE_REQUESTED_TOPIC, event.getMaintenanceLogId(), event)
        .whenComplete((result, throwable) -> {
          if (throwable != null) {
            logger.error("Failed to publish maintenance requested event: {}",
                event.getMaintenanceLogId(), throwable);
          } else {
            logger.info(
                "Successfully published maintenance requested event: {} to partition {} offset {}",
                event.getMaintenanceLogId(), result.getRecordMetadata().partition(),
                result.getRecordMetadata().offset());
          }
        });
  }

  /**
   * 장비 상태 업데이트 요청 이벤트를 Kafka로 발행
   */
  public CompletableFuture<SendResult<String, Object>> publishEquipmentStateUpdateRequested(
      EquipmentStateUpdateRequested event) {
    logger.info("Publishing equipment state update requested event: {}", event.getRequestId());

    return kafkaTemplate.send(EQUIPMENT_STATE_UPDATE_REQUESTED_TOPIC, event.getRequestId(), event)
        .whenComplete((result, throwable) -> {
          if (throwable != null) {
            logger.error("Failed to publish equipment state update requested event: {}",
                event.getRequestId(), throwable);
          } else {
            logger.info(
                "Successfully published equipment state update requested event: {} to partition {} offset {}",
                event.getRequestId(), result.getRecordMetadata().partition(),
                result.getRecordMetadata().offset());
          }
        });
  }

  /**
   * 동기적으로 이벤트 발행 (테스트용)
   */
  public void publishMaintenanceRequestedSync(MaintenanceRequested event) {
    try {
      kafkaTemplate.send(MAINTENANCE_REQUESTED_TOPIC, event.getMaintenanceLogId(), event).get();
      logger.info("Synchronously published maintenance requested event: {}",
          event.getMaintenanceLogId());
    } catch (Exception e) {
      logger.error("Failed to synchronously publish maintenance requested event: {}",
          event.getMaintenanceLogId(), e);
      throw new RuntimeException("Failed to publish event", e);
    }
  }

  public void publishEquipmentStateUpdateRequestedSync(EquipmentStateUpdateRequested event) {
    try {
      kafkaTemplate.send(EQUIPMENT_STATE_UPDATE_REQUESTED_TOPIC, event.getRequestId(), event).get();
      logger.info("Synchronously published equipment state update requested event: {}",
          event.getRequestId());
    } catch (Exception e) {
      logger.error("Failed to synchronously publish equipment state update requested event: {}",
          event.getRequestId(), e);
      throw new RuntimeException("Failed to publish event", e);
    }
  }
}
