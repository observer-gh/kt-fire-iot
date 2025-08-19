package com.fireiot.controltower.processor;

import com.fireiot.controltower.events.SensorDataSaved;
import com.fireiot.controltower.events.SensorAnomalyDetected;
import com.fireiot.controltower.events.WarningAlertIssued;
import com.fireiot.controltower.events.EmergencyAlertIssued;
import com.fireiot.controltower.publisher.AlertEventPublisher;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import java.time.OffsetDateTime;
import java.util.UUID;

@Component
public class SensorDataProcessor {

  private static final Logger logger = LoggerFactory.getLogger(SensorDataProcessor.class);

  private final AlertEventPublisher alertEventPublisher;

  public SensorDataProcessor(AlertEventPublisher alertEventPublisher) {
    this.alertEventPublisher = alertEventPublisher;
  }

  // Thresholds
  private static final double SMOKE_WARNING_THRESHOLD = 0.7;
  private static final double SMOKE_CRITICAL_THRESHOLD = 0.9;
  private static final double CO_WARNING_THRESHOLD = 0.1;
  private static final double CO_CRITICAL_THRESHOLD = 0.15;
  private static final double TEMP_WARNING_THRESHOLD = 80.0;
  private static final double TEMP_CRITICAL_THRESHOLD = 100.0;

  public void processSensorData(SensorDataSaved event) {
    logger.info("Processing sensor data for equipment: {}", event.getEquipmentId());

    // Basic validation
    if (event.getEquipmentId() == null || event.getEquipmentId().isEmpty()) {
      logger.warn("Invalid sensor data: missing equipment ID");
      return;
    }

    // Log the sensor readings
    logger.info("Sensor readings - Equipment: {}, Temperature: {}, Smoke: {}, CO: {}",
        event.getEquipmentId(), event.getTemperature(), event.getSmokeDensity(),
        event.getCoLevel());

    // Check thresholds and generate alerts
    checkSmokeLevel(event);
    checkCOLevel(event);
    checkTemperature(event);
    checkMultipleCriticalReadings(event);
  }

  public void processSensorAnomaly(SensorAnomalyDetected event) {
    logger.info("Processing sensor anomaly for equipment: {}", event.getEquipmentId());

    // Basic validation
    if (event.getEquipmentId() == null || event.getEquipmentId().isEmpty()) {
      logger.warn("Invalid sensor anomaly: missing equipment ID");
      return;
    }

    // Log the anomaly details
    logger.info(
        "Sensor anomaly - Equipment: {}, Metric: {}, Value: {}, Threshold: {}, Severity: {}",
        event.getEquipmentId(), event.getMetric(), event.getValue(), event.getThreshold(),
        event.getSeverity());

    // Process based on severity
    switch (event.getSeverity()) {
      case "WARN":
        logger.warn("WARNING: Sensor anomaly detected. Equipment: {}, Metric: {}, Value: {}",
            event.getEquipmentId(), event.getMetric(), event.getValue());
        generateWarningAlert(event);
        break;
      case "EMERGENCY":
        logger.error(
            "EMERGENCY: Critical sensor anomaly detected! Equipment: {}, Metric: {}, Value: {}",
            event.getEquipmentId(), event.getMetric(), event.getValue());
        generateEmergencyAlert(event);
        break;
      case "INFO":
        logger.info("INFO: Sensor anomaly detected. Equipment: {}, Metric: {}, Value: {}",
            event.getEquipmentId(), event.getMetric(), event.getValue());
        // For INFO level, just log - no alert needed
        break;
      default:
        logger.warn("Unknown severity level: {} for equipment: {}", event.getSeverity(),
            event.getEquipmentId());
    }
  }

  private void checkSmokeLevel(SensorDataSaved event) {
    Double smokeLevel = event.getSmokeDensity();
    if (smokeLevel == null)
      return;

    if (smokeLevel >= SMOKE_CRITICAL_THRESHOLD) {
      logger.error("CRITICAL: High smoke level detected! Equipment: {}, Level: {}",
          event.getEquipmentId(), smokeLevel);
      // TODO: Generate emergency alert
    } else if (smokeLevel >= SMOKE_WARNING_THRESHOLD) {
      logger.warn("WARNING: Elevated smoke level detected. Equipment: {}, Level: {}",
          event.getEquipmentId(), smokeLevel);
      // TODO: Generate warning alert
    }
  }

  private void checkCOLevel(SensorDataSaved event) {
    Double coLevel = event.getCoLevel();
    if (coLevel == null)
      return;

    if (coLevel >= CO_CRITICAL_THRESHOLD) {
      logger.error("CRITICAL: High CO level detected! Equipment: {}, Level: {}",
          event.getEquipmentId(), coLevel);
      // TODO: Generate emergency alert
    } else if (coLevel >= CO_WARNING_THRESHOLD) {
      logger.warn("WARNING: Elevated CO level detected. Equipment: {}, Level: {}",
          event.getEquipmentId(), coLevel);
      // TODO: Generate warning alert
    }
  }

  private void checkTemperature(SensorDataSaved event) {
    Double temperature = event.getTemperature();
    if (temperature == null)
      return;

    if (temperature >= TEMP_CRITICAL_THRESHOLD) {
      logger.error("CRITICAL: High temperature detected! Equipment: {}, Temp: {}",
          event.getEquipmentId(), temperature);
      // TODO: Generate emergency alert
    } else if (temperature >= TEMP_WARNING_THRESHOLD) {
      logger.warn("WARNING: Elevated temperature detected. Equipment: {}, Temp: {}",
          event.getEquipmentId(), temperature);
      // TODO: Generate warning alert
    }
  }

  private void checkMultipleCriticalReadings(SensorDataSaved event) {
    int criticalCount = 0;

    if (event.getSmokeDensity() != null && event.getSmokeDensity() >= SMOKE_CRITICAL_THRESHOLD) {
      criticalCount++;
    }
    if (event.getCoLevel() != null && event.getCoLevel() >= CO_CRITICAL_THRESHOLD) {
      criticalCount++;
    }
    if (event.getTemperature() != null && event.getTemperature() >= TEMP_CRITICAL_THRESHOLD) {
      criticalCount++;
    }

    if (criticalCount >= 2) {
      logger.error(
          "EMERGENCY: Multiple critical readings detected! Equipment: {}, Critical Count: {}",
          event.getEquipmentId(), criticalCount);
      // TODO: Generate emergency escalation alert
    }
  }

  private void generateWarningAlert(SensorAnomalyDetected event) {
    WarningAlertIssued alert = new WarningAlertIssued();
    alert.setVersion(1);
    alert.setAlertId(UUID.randomUUID().toString());
    alert.setEquipmentId(event.getEquipmentId());
    alert.setFacilityId(event.getFacilityId());
    alert.setEquipmentLocation("Unknown"); // Could be enhanced with location data
    alert.setAlertType(mapMetricToAlertType(event.getMetric()));
    alert.setSeverity("WARN");
    alert.setStatus("PENDING");
    alert.setCreatedAt(OffsetDateTime.now());

    alertEventPublisher.publishWarningAlert(alert);
    logger.info("Generated warning alert: {} for equipment: {}", alert.getAlertId(),
        event.getEquipmentId());
  }

  private void generateEmergencyAlert(SensorAnomalyDetected event) {
    EmergencyAlertIssued alert = new EmergencyAlertIssued();
    alert.setVersion(1);
    alert.setAlertId(UUID.randomUUID().toString());
    alert.setEquipmentId(event.getEquipmentId());
    alert.setFacilityId(event.getFacilityId());
    alert.setEquipmentLocation("Unknown"); // Could be enhanced with location data
    alert.setAlertType(mapMetricToAlertType(event.getMetric()));
    alert.setSeverity("EMERGENCY");
    alert.setStatus("PENDING");
    alert.setCreatedAt(OffsetDateTime.now());

    alertEventPublisher.publishEmergencyAlert(alert);
    logger.info("Generated emergency alert: {} for equipment: {}", alert.getAlertId(),
        event.getEquipmentId());
  }

  private String mapMetricToAlertType(String metric) {
    if (metric == null)
      return "CUSTOM";

    switch (metric.toLowerCase()) {
      case "smoke_density":
      case "smoke":
        return "SMOKE";
      case "co_level":
      case "co":
        return "CO";
      case "temperature":
      case "temp":
        return "HEAT";
      case "gas_level":
      case "gas":
        return "GAS";
      case "power":
        return "POWER";
      case "communication":
      case "comm":
        return "COMM";
      default:
        return "CUSTOM";
    }
  }
}
