package com.fireiot.controltower.processor;

import com.fireiot.controltower.events.SensorDataSaved;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.OffsetDateTime;

import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class SensorDataProcessorTest {

  private SensorDataProcessor processor;

  @BeforeEach
  void setUp() {
    processor = new SensorDataProcessor();
  }

  @Test
  void shouldProcessNormalSensorDataWithoutAlerts() {
    // Given
    SensorDataSaved event = createSensorDataEvent("sensor-001", 25.0, // normal temperature
        0.1, // low smoke
        0.05 // low CO
    );

    // When
    processor.processSensorData(event);

    // Then - verify no alerts are generated for normal readings
    // (we'll add alert generation logic based on this test)
  }

  @Test
  void shouldDetectHighSmokeLevelAndGenerateAlert() {
    // Given
    SensorDataSaved event = createSensorDataEvent("sensor-001", 25.0, // normal temperature
        0.8, // high smoke - should trigger alert
        0.05 // low CO
    );

    // When
    processor.processSensorData(event);

    // Then - verify warning alert is generated
    // (we'll implement alert generation based on this test)
  }

  @Test
  void shouldDetectCriticalCOLevelAndGenerateEmergencyAlert() {
    // Given
    SensorDataSaved event = createSensorDataEvent("sensor-001", 25.0, // normal temperature
        0.1, // low smoke
        0.15 // critical CO - should trigger emergency
    );

    // When
    processor.processSensorData(event);

    // Then - verify emergency alert is generated
    // (we'll implement emergency alert generation based on this test)
  }

  @Test
  void shouldHandleMultipleCriticalReadingsAndEscalate() {
    // Given
    SensorDataSaved event = createSensorDataEvent("sensor-001", 85.0, // high temperature
        0.9, // very high smoke
        0.2 // very high CO
    );

    // When
    processor.processSensorData(event);

    // Then - verify emergency alert is generated for multiple critical readings
    // (we'll implement escalation logic based on this test)
  }

  private SensorDataSaved createSensorDataEvent(String equipmentId, Double temperature,
      Double smoke, Double co) {
    SensorDataSaved event = new SensorDataSaved();
    event.setVersion(1);
    event.setEventId("event-" + System.currentTimeMillis());
    event.setEquipmentId(equipmentId);
    event.setFacilityId("facility-001");
    event.setEquipmentLocation("Building A, Floor 2, Room 205");
    event.setMeasuredAt(OffsetDateTime.now());
    event.setTemperature(temperature);
    event.setHumidity(45.0);
    event.setSmokeDensity(smoke);
    event.setCoLevel(co);
    event.setGasLevel(0.02);
    event.setIngestedAt(OffsetDateTime.now());
    return event;
  }
}
