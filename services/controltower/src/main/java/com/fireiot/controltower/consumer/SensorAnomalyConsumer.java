package com.fireiot.controltower.consumer;

import com.fireiot.controltower.events.SensorAnomalyDetected;
import com.fireiot.controltower.processor.SensorDataProcessor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class SensorAnomalyConsumer {

  private static final Logger logger = LoggerFactory.getLogger(SensorAnomalyConsumer.class);

  private final SensorDataProcessor sensorDataProcessor;

  public SensorAnomalyConsumer(SensorDataProcessor sensorDataProcessor) {
    this.sensorDataProcessor = sensorDataProcessor;
  }

  @KafkaListener(
      topics = "${kafka.topics.sensor-anomaly-detected:datalake.sensorDataAnomalyDetected}",
      groupId = "controltower-group")
  public void consumeSensorAnomalyDetected(SensorAnomalyDetected event) {
    logger.info("Received SensorAnomalyDetected event: {}", event.getEventId());

    try {
      sensorDataProcessor.processSensorAnomaly(event);
      logger.info("Successfully processed SensorAnomalyDetected event: {}", event.getEventId());
    } catch (Exception e) {
      logger.error("Error processing SensorAnomalyDetected event: {}", event.getEventId(), e);
      // TODO: Implement dead letter queue or retry mechanism
    }
  }
}
