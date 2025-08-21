package com.fireiot.controltower.processor;

import com.fireiot.controltower.events.VideoFireDetected;
import com.fireiot.controltower.events.FireDetectionNotified;
import com.fireiot.controltower.publisher.FireDetectionEventPublisher;
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
class FireDetectionProcessorTest {

  @Mock
  private FireDetectionEventPublisher fireDetectionEventPublisher;

  private FireDetectionProcessor fireDetectionProcessor;

  @BeforeEach
  void setUp() {
    fireDetectionProcessor = new FireDetectionProcessor(fireDetectionEventPublisher);
  }

  @Test
  void testProcessVideoFireDetection_HighConfidence_GeneratesEmergencyAlert() {
    // Given
    VideoFireDetected event = createVideoFireDetected(95); // 95% confidence

    // When
    fireDetectionProcessor.processVideoFireDetection(event);

    // Then
    ArgumentCaptor<FireDetectionNotified> alertCaptor =
        ArgumentCaptor.forClass(FireDetectionNotified.class);
    verify(fireDetectionEventPublisher).publishFireDetectionNotification(alertCaptor.capture());

    FireDetectionNotified alert = alertCaptor.getValue();
    assertEquals("EMERGENCY", alert.getSeverity());
    assertEquals("CUSTOM", alert.getAlertType());
    assertEquals(event.getCctvId(), alert.getCctvId());
    assertEquals(event.getFacilityId(), alert.getFacilityId());
    assertEquals(event.getDetectionConfidence(), alert.getDetectionConfidence());
    assertNotNull(alert.getAlertId());
    assertNotNull(alert.getIncidentId());
    assertEquals("PENDING", alert.getStatus());
    assertTrue(alert.getDescription().contains("95% confidence"));
  }

  @Test
  void testProcessVideoFireDetection_MediumConfidence_GeneratesWarningAlert() {
    // Given
    VideoFireDetected event = createVideoFireDetected(75); // 75% confidence

    // When
    fireDetectionProcessor.processVideoFireDetection(event);

    // Then
    ArgumentCaptor<FireDetectionNotified> alertCaptor =
        ArgumentCaptor.forClass(FireDetectionNotified.class);
    verify(fireDetectionEventPublisher).publishFireDetectionNotification(alertCaptor.capture());

    FireDetectionNotified alert = alertCaptor.getValue();
    assertEquals("WARN", alert.getSeverity());
    assertEquals("CUSTOM", alert.getAlertType());
    assertEquals(event.getCctvId(), alert.getCctvId());
    assertTrue(alert.getDescription().contains("75% confidence"));
  }

  @Test
  void testProcessVideoFireDetection_LowConfidence_GeneratesInfoAlert() {
    // Given
    VideoFireDetected event = createVideoFireDetected(65); // 65% confidence

    // When
    fireDetectionProcessor.processVideoFireDetection(event);

    // Then
    ArgumentCaptor<FireDetectionNotified> alertCaptor =
        ArgumentCaptor.forClass(FireDetectionNotified.class);
    verify(fireDetectionEventPublisher).publishFireDetectionNotification(alertCaptor.capture());

    FireDetectionNotified alert = alertCaptor.getValue();
    assertEquals("INFO", alert.getSeverity());
    assertEquals("CUSTOM", alert.getAlertType());
    assertTrue(alert.getDescription().contains("65% confidence"));
  }

  @Test
  void testProcessVideoFireDetection_BoundaryConfidence70_GeneratesWarningAlert() {
    // Given
    VideoFireDetected event = createVideoFireDetected(70); // Exactly 70% - boundary test

    // When
    fireDetectionProcessor.processVideoFireDetection(event);

    // Then
    ArgumentCaptor<FireDetectionNotified> alertCaptor =
        ArgumentCaptor.forClass(FireDetectionNotified.class);
    verify(fireDetectionEventPublisher).publishFireDetectionNotification(alertCaptor.capture());

    FireDetectionNotified alert = alertCaptor.getValue();
    assertEquals("WARN", alert.getSeverity());
  }

  @Test
  void testProcessVideoFireDetection_BoundaryConfidence85_GeneratesEmergencyAlert() {
    // Given
    VideoFireDetected event = createVideoFireDetected(85); // Exactly 85% - boundary test

    // When
    fireDetectionProcessor.processVideoFireDetection(event);

    // Then
    ArgumentCaptor<FireDetectionNotified> alertCaptor =
        ArgumentCaptor.forClass(FireDetectionNotified.class);
    verify(fireDetectionEventPublisher).publishFireDetectionNotification(alertCaptor.capture());

    FireDetectionNotified alert = alertCaptor.getValue();
    assertEquals("EMERGENCY", alert.getSeverity());
  }

  @Test
  void testProcessVideoFireDetection_NullCctvId_LogsWarningAndReturns() {
    // Given
    VideoFireDetected event = createVideoFireDetected(90);
    event.setCctvId(null);

    // When
    fireDetectionProcessor.processVideoFireDetection(event);

    // Then
    verify(fireDetectionEventPublisher, never()).publishFireDetectionNotification(any());
  }

  @Test
  void testProcessVideoFireDetection_EmptyCctvId_LogsWarningAndReturns() {
    // Given
    VideoFireDetected event = createVideoFireDetected(90);
    event.setCctvId("");

    // When
    fireDetectionProcessor.processVideoFireDetection(event);

    // Then
    verify(fireDetectionEventPublisher, never()).publishFireDetectionNotification(any());
  }

  @Test
  void testProcessVideoFireDetection_NullConfidence_LogsWarningAndReturns() {
    // Given
    VideoFireDetected event = createVideoFireDetected(90);
    event.setDetectionConfidence(null);

    // When
    fireDetectionProcessor.processVideoFireDetection(event);

    // Then
    verify(fireDetectionEventPublisher, never()).publishFireDetectionNotification(any());
  }

  @Test
  void testProcessVideoFireDetection_WithDetectionArea_IncludesAreaInDescription() {
    // Given
    VideoFireDetected event = createVideoFireDetected(80);
    event.setDetectionArea("Kitchen Area B2");

    // When
    fireDetectionProcessor.processVideoFireDetection(event);

    // Then
    ArgumentCaptor<FireDetectionNotified> alertCaptor =
        ArgumentCaptor.forClass(FireDetectionNotified.class);
    verify(fireDetectionEventPublisher).publishFireDetectionNotification(alertCaptor.capture());

    FireDetectionNotified alert = alertCaptor.getValue();
    assertTrue(alert.getDescription().contains("Kitchen Area B2"));
  }

  // Helper method to create test data
  private VideoFireDetected createVideoFireDetected(Integer confidence) {
    VideoFireDetected event = new VideoFireDetected();
    event.setEventId(UUID.randomUUID().toString());
    event.setFacilityId("facility-001");
    event.setEquipmentLocation("Floor 2, Section A");
    event.setDetectionConfidence(confidence);
    event.setDetectionTimestamp(OffsetDateTime.now());
    event.setCctvId("cctv-001");
    event.setDetectionArea("Main Hall");
    event.setDescription("Fire detected via video analysis");
    return event;
  }
}
