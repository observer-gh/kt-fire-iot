package com.fireiot.controltower.processor;

import com.fireiot.controltower.events.SensorDataSaved;
import com.fireiot.controltower.events.SensorAnomalyDetected;
import com.fireiot.controltower.events.WarningAlertIssued;
import com.fireiot.controltower.events.EmergencyAlertIssued;
import com.fireiot.controltower.publisher.AlertEventPublisher;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.ArgumentCaptor;

import java.time.OffsetDateTime;
import java.util.UUID;

import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class SensorDataProcessorTest {

  @Mock
  private AlertEventPublisher alertEventPublisher;

  private SensorDataProcessor sensorDataProcessor;

  @BeforeEach
  void setUp() {
    sensorDataProcessor = new SensorDataProcessor(alertEventPublisher);
  }

  @Test
  void testProcessSensorData_ValidData_ProcessesAllChecks() {
    // Given
    SensorDataSaved event = createValidSensorDataSaved();

    // When
    sensorDataProcessor.processSensorData(event);

    // Then - verify no exceptions and publisher was called if thresholds exceeded
    // (In this case, values are below thresholds, so no alerts should be generated)
    verify(alertEventPublisher, never()).publishWarningAlert(any());
    verify(alertEventPublisher, never()).publishEmergencyAlert(any());
  }

  @Test
  void testProcessSensorData_NullEquipmentId_LogsWarningAndReturns() {
    // Given
    SensorDataSaved event = createValidSensorDataSaved();
    event.setEquipmentId(null);

    // When
    sensorDataProcessor.processSensorData(event);

    // Then
    verify(alertEventPublisher, never()).publishWarningAlert(any());
    verify(alertEventPublisher, never()).publishEmergencyAlert(any());
  }

  @Test
  void testProcessSensorData_EmptyEquipmentId_LogsWarningAndReturns() {
    // Given
    SensorDataSaved event = createValidSensorDataSaved();
    event.setEquipmentId("");

    // When
    sensorDataProcessor.processSensorData(event);

    // Then
    verify(alertEventPublisher, never()).publishWarningAlert(any());
    verify(alertEventPublisher, never()).publishEmergencyAlert(any());
  }

  @Test
  void testProcessSensorAnomaly_WarningSeverity_GeneratesWarningAlert() {
    // Given
    SensorAnomalyDetected event = createSensorAnomalyDetected("WARN", "smoke_density", 0.8);

    // When
    sensorDataProcessor.processSensorAnomaly(event);

    // Then
    ArgumentCaptor<WarningAlertIssued> alertCaptor =
        ArgumentCaptor.forClass(WarningAlertIssued.class);
    verify(alertEventPublisher).publishWarningAlert(alertCaptor.capture());

    WarningAlertIssued alert = alertCaptor.getValue();
    assertEquals("WARN", alert.getSeverity());
    assertEquals("SMOKE", alert.getAlertType());
    assertEquals(event.getEquipmentId(), alert.getEquipmentId());
    assertEquals(event.getFacilityId(), alert.getFacilityId());
    assertNotNull(alert.getAlertId());
    assertEquals("PENDING", alert.getStatus());
  }

  @Test
  void testProcessSensorAnomaly_EmergencySeverity_GeneratesEmergencyAlert() {
    // Given
    SensorAnomalyDetected event = createSensorAnomalyDetected("EMERGENCY", "co_level", 0.2);

    // When
    sensorDataProcessor.processSensorAnomaly(event);

    // Then
    ArgumentCaptor<EmergencyAlertIssued> alertCaptor =
        ArgumentCaptor.forClass(EmergencyAlertIssued.class);
    verify(alertEventPublisher).publishEmergencyAlert(alertCaptor.capture());

    EmergencyAlertIssued alert = alertCaptor.getValue();
    assertEquals("EMERGENCY", alert.getSeverity());
    assertEquals("CO", alert.getAlertType());
    assertEquals(event.getEquipmentId(), alert.getEquipmentId());
    assertEquals(event.getFacilityId(), alert.getFacilityId());
    assertNotNull(alert.getAlertId());
    assertEquals("PENDING", alert.getStatus());
  }

  @Test
  void testProcessSensorAnomaly_InfoSeverity_NoAlertGenerated() {
    // Given
    SensorAnomalyDetected event = createSensorAnomalyDetected("INFO", "temperature", 75.0);

    // When
    sensorDataProcessor.processSensorAnomaly(event);

    // Then
    verify(alertEventPublisher, never()).publishWarningAlert(any());
    verify(alertEventPublisher, never()).publishEmergencyAlert(any());
  }

  @Test
  void testProcessSensorAnomaly_UnknownSeverity_NoAlertGenerated() {
    // Given
    SensorAnomalyDetected event = createSensorAnomalyDetected("UNKNOWN", "temperature", 75.0);

    // When
    sensorDataProcessor.processSensorAnomaly(event);

    // Then
    verify(alertEventPublisher, never()).publishWarningAlert(any());
    verify(alertEventPublisher, never()).publishEmergencyAlert(any());
  }

  @Test
  void testProcessSensorAnomaly_NullEquipmentId_LogsWarningAndReturns() {
    // Given
    SensorAnomalyDetected event = createSensorAnomalyDetected("WARN", "smoke_density", 0.8);
    event.setEquipmentId(null);

    // When
    sensorDataProcessor.processSensorAnomaly(event);

    // Then
    verify(alertEventPublisher, never()).publishWarningAlert(any());
    verify(alertEventPublisher, never()).publishEmergencyAlert(any());
  }

  @Test
  void testProcessSensorAnomaly_EmptyEquipmentId_LogsWarningAndReturns() {
    // Given
    SensorAnomalyDetected event = createSensorAnomalyDetected("WARN", "smoke_density", 0.8);
    event.setEquipmentId("");

    // When
    sensorDataProcessor.processSensorAnomaly(event);

    // Then
    verify(alertEventPublisher, never()).publishWarningAlert(any());
    verify(alertEventPublisher, never()).publishEmergencyAlert(any());
  }

  @Test
  void testMetricMapping_VariousMetrics_ReturnsCorrectAlertTypes() {
    // Test through the anomaly processing
    String[][] testCases = {{"smoke_density", "SMOKE"}, {"smoke", "SMOKE"}, {"co_level", "CO"},
        {"co", "CO"}, {"temperature", "HEAT"}, {"temp", "HEAT"}, {"gas_level", "GAS"},
        {"gas", "GAS"}, {"power", "POWER"}, {"communication", "COMM"}, {"comm", "COMM"},
        {"unknown_metric", "CUSTOM"}, {null, "CUSTOM"}};

    for (String[] testCase : testCases) {
      SensorAnomalyDetected event = createSensorAnomalyDetected("WARN", testCase[0], 0.8);

      sensorDataProcessor.processSensorAnomaly(event);

      ArgumentCaptor<WarningAlertIssued> alertCaptor =
          ArgumentCaptor.forClass(WarningAlertIssued.class);
      verify(alertEventPublisher).publishWarningAlert(alertCaptor.capture());

      assertEquals(testCase[1], alertCaptor.getValue().getAlertType(),
          "Failed for metric: " + testCase[0]);

      // Reset mock for next iteration
      reset(alertEventPublisher);
    }
  }

  // Helper methods to create test data
  private SensorDataSaved createValidSensorDataSaved() {
    SensorDataSaved event = new SensorDataSaved();
    event.setEventId(UUID.randomUUID().toString());
    event.setEquipmentId("equipment-001");
    event.setFacilityId("facility-001");
    event.setTemperature(25.0);
    event.setSmokeDensity(0.1);
    event.setCoLevel(0.05);
    event.setMeasuredAt(OffsetDateTime.now());
    event.setIngestedAt(OffsetDateTime.now());
    return event;
  }

  private SensorAnomalyDetected createSensorAnomalyDetected(String severity, String metric,
      Double value) {
    SensorAnomalyDetected event = new SensorAnomalyDetected();
    event.setEventId(UUID.randomUUID().toString());
    event.setEquipmentId("equipment-001");
    event.setFacilityId("facility-001");
    event.setMetric(metric);
    event.setValue(value);
    event.setThreshold(0.5);
    event.setSeverity(severity);
    event.setMeasuredAt(OffsetDateTime.now());
    event.setDetectedAt(OffsetDateTime.now());
    return event;
  }
}
