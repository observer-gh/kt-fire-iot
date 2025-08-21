package com.fireiot.facilitymanagement.consumer;

import com.fireiot.facilitymanagement.events.EquipmentStateUpdateRequested;
import com.fireiot.facilitymanagement.service.EquipmentService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class EquipmentStateUpdateConsumer {

  private static final Logger logger = LoggerFactory.getLogger(EquipmentStateUpdateConsumer.class);

  @Autowired
  private EquipmentService equipmentService;

  @KafkaListener(topics = "equipmentStateUpdateRequested", groupId = "facilitymanagement-group")
  public void consumeEquipmentStateUpdateRequested(EquipmentStateUpdateRequested event) {
    logger.info("Received EquipmentStateUpdateRequested event: {}", event.getRequestId());

    try {
      // 장비 상태 업데이트 이벤트를 처리하여 데이터베이스 업데이트
      boolean updateSuccess = equipmentService.updateEquipmentState(event);

      if (updateSuccess) {
        logger.info(
            "Successfully processed EquipmentStateUpdateRequested event: {} for equipment: {}",
            event.getRequestId(), event.getEquipmentId());
      } else {
        logger.error("Failed to process EquipmentStateUpdateRequested event: {} for equipment: {}",
            event.getRequestId(), event.getEquipmentId());
      }

    } catch (Exception e) {
      logger.error("Error processing EquipmentStateUpdateRequested event: {} for equipment: {}",
          event.getRequestId(), event.getEquipmentId(), e);
      // TODO: Implement dead letter queue or retry mechanism
    }
  }
}
