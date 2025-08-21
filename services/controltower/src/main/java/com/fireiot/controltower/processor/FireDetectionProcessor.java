package com.fireiot.controltower.processor;

import com.fireiot.controltower.events.VideoFireDetected;
import com.fireiot.controltower.events.FireDetectionNotified;
import com.fireiot.controltower.publisher.FireDetectionEventPublisher;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import java.time.OffsetDateTime;
import java.util.UUID;

@Component
public class FireDetectionProcessor {

  private static final Logger logger = LoggerFactory.getLogger(FireDetectionProcessor.class);

  private final FireDetectionEventPublisher fireDetectionEventPublisher;

  // Confidence thresholds
  private static final int WARNING_CONFIDENCE_THRESHOLD = 70;
  private static final int EMERGENCY_CONFIDENCE_THRESHOLD = 85;

  public FireDetectionProcessor(FireDetectionEventPublisher fireDetectionEventPublisher) {
    this.fireDetectionEventPublisher = fireDetectionEventPublisher;
  }

  public void processVideoFireDetection(VideoFireDetected event) {
    logger.info("Processing video fire detection for CCTV: {}, Confidence: {}%", event.getCctvId(),
        event.getDetectionConfidence());

    // Basic validation
    if (event.getCctvId() == null || event.getCctvId().isEmpty()) {
      logger.warn("Invalid fire detection: missing CCTV ID");
      return;
    }

    if (event.getDetectionConfidence() == null) {
      logger.warn("Invalid fire detection: missing confidence score");
      return;
    }

    // Log the detection details
    logger.info("Fire detection details - CCTV: {}, Confidence: {}%, Area: {}, Facility: {}",
        event.getCctvId(), event.getDetectionConfidence(), event.getDetectionArea(),
        event.getFacilityId());

    // Process based on confidence level
    String severity = determineSeverity(event.getDetectionConfidence());

    switch (severity) {
      case "WARN":
        logger.warn("WARNING: Fire detected with medium confidence. CCTV: {}, Confidence: {}%",
            event.getCctvId(), event.getDetectionConfidence());
        generateFireDetectionAlert(event, severity);
        break;
      case "EMERGENCY":
        logger.error("EMERGENCY: Fire detected with high confidence! CCTV: {}, Confidence: {}%",
            event.getCctvId(), event.getDetectionConfidence());
        generateFireDetectionAlert(event, severity);
        break;
      case "INFO":
        logger.info("INFO: Possible fire detected with low confidence. CCTV: {}, Confidence: {}%",
            event.getCctvId(), event.getDetectionConfidence());
        generateFireDetectionAlert(event, severity);
        break;
      default:
        logger.warn("Unknown severity level determined for CCTV: {}", event.getCctvId());
    }
  }

  private String determineSeverity(Integer confidence) {
    if (confidence >= EMERGENCY_CONFIDENCE_THRESHOLD) {
      return "EMERGENCY";
    } else if (confidence >= WARNING_CONFIDENCE_THRESHOLD) {
      return "WARN";
    } else {
      return "INFO";
    }
  }

  private void generateFireDetectionAlert(VideoFireDetected event, String severity) {
    FireDetectionNotified alert = new FireDetectionNotified();

    // Generate unique IDs
    String alertId = UUID.randomUUID().toString();
    String incidentId = UUID.randomUUID().toString();

    alert.setVersion(1);
    alert.setAlertId(alertId);
    alert.setIncidentId(incidentId);
    alert.setFacilityId(event.getFacilityId());
    alert.setEquipmentLocation(event.getEquipmentLocation());
    alert.setAlertType("CUSTOM"); // Fire detection from video analysis
    alert.setSeverity(severity);
    alert.setStatus("PENDING");
    alert.setCreatedAt(OffsetDateTime.now());
    alert.setCctvId(event.getCctvId());
    alert.setDetectionConfidence(event.getDetectionConfidence());

    // Create descriptive message
    String description = String.format(
        "Fire detected via video analysis from CCTV %s with %d%% confidence in area: %s",
        event.getCctvId(), event.getDetectionConfidence(),
        event.getDetectionArea() != null ? event.getDetectionArea() : "unknown");
    alert.setDescription(description);

    // Publish the fire detection notification
    fireDetectionEventPublisher.publishFireDetectionNotification(alert);

    logger.info("Generated fire detection alert: {} for CCTV: {} with severity: {}", alertId,
        event.getCctvId(), severity);
  }
}
