package com.fireiot.controltower.consumer;

import com.fireiot.controltower.events.VideoFireDetected;
import com.fireiot.controltower.processor.FireDetectionProcessor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class FireDetectionConsumer {

  private static final Logger logger = LoggerFactory.getLogger(FireDetectionConsumer.class);

  private final FireDetectionProcessor fireDetectionProcessor;

  public FireDetectionConsumer(FireDetectionProcessor fireDetectionProcessor) {
    this.fireDetectionProcessor = fireDetectionProcessor;
  }

  @KafkaListener(topics = "${kafka.topics.video-fire-detected:videoAnalysis.fireDetected}",
      groupId = "${kafka.consumer.group-id:controltower-group}",
      containerFactory = "videoFireDetectedKafkaListenerContainerFactory")
  public void consumeVideoFireDetected(VideoFireDetected event) {
    logger.info("Received VideoFireDetected event: {} from CCTV: {}", event.getEventId(),
        event.getCctvId());

    try {
      fireDetectionProcessor.processVideoFireDetection(event);
      logger.info("Successfully processed VideoFireDetected event: {}", event.getEventId());
    } catch (Exception e) {
      logger.error("Error processing VideoFireDetected event: {}", event.getEventId(), e);
      // TODO: Implement dead letter queue or retry mechanism
    }
  }
}
