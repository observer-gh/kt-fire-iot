package com.fireiot.facilitymanagement.controller;

import com.fireiot.facilitymanagement.events.MaintenanceRequested;
import com.fireiot.facilitymanagement.publisher.MaintenanceEventPublisher;
import com.fireiot.facilitymanagement.service.RiskScoringService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.OffsetDateTime;

@RestController
@RequestMapping("/api/v1/maintenance")
@Tag(name = "Maintenance", description = "Maintenance management APIs")
public class MaintenanceController {

  private static final Logger logger = LoggerFactory.getLogger(MaintenanceController.class);

  private final MaintenanceEventPublisher maintenanceEventPublisher;
  private final RiskScoringService riskScoringService;

  public MaintenanceController(MaintenanceEventPublisher maintenanceEventPublisher,
      RiskScoringService riskScoringService) {
    this.maintenanceEventPublisher = maintenanceEventPublisher;
    this.riskScoringService = riskScoringService;
  }

  @PostMapping("/request")
  @Operation(summary = "Request maintenance for equipment",
      description = "Creates a maintenance request with risk scoring and publishes event")
  public ResponseEntity<String> requestMaintenance(@RequestBody MaintenanceRequested request) {
    logger.info("Received maintenance request for equipment: {}", request.getEquipmentId());

    try {
      // Set timestamp if not provided
      if (request.getRequestedAt() == null) {
        request.setRequestedAt(OffsetDateTime.now());
      }

      // Publish the event with risk scoring
      maintenanceEventPublisher.publishMaintenanceRequested(request);

      logger.info("Maintenance request with risk scoring processed successfully: {}",
          request.getMaintenanceLogId());
      return ResponseEntity.ok("Maintenance request created successfully with risk assessment");

    } catch (Exception e) {
      logger.error("Error processing maintenance request: {}", request.getMaintenanceLogId(), e);
      return ResponseEntity.internalServerError().body("Error processing maintenance request");
    }
  }

  @GetMapping("/health")
  @Operation(summary = "Health check", description = "Returns service health status")
  public ResponseEntity<String> health() {
    return ResponseEntity.ok("Facility Management Service is running");
  }

  @PostMapping("/risk-assessment")
  @Operation(summary = "Assess maintenance risk",
      description = "Calculates risk score for maintenance request without publishing")
  public ResponseEntity<RiskAssessmentResponse> assessRisk(
      @RequestBody MaintenanceRequested request) {
    logger.info("Risk assessment requested for equipment: {}", request.getEquipmentId());

    try {
      // 위험도 스코어링 수행
      double riskScore = riskScoringService.calculateRiskScore(request);
      String riskLevel = riskScoringService.getRiskLevel(riskScore).getDescription();
      String riskRecommendation = riskScoringService.generateRecommendation(riskScore);

      RiskAssessmentResponse response = new RiskAssessmentResponse(request.getMaintenanceLogId(),
          riskScore, riskLevel, riskRecommendation, riskScoringService.isHighRisk(riskScore, 0.7));

      logger.info("Risk assessment completed: {} ({}) for maintenance request: {}",
          String.format("%.3f", riskScore), riskLevel, request.getMaintenanceLogId());

      return ResponseEntity.ok(response);

    } catch (Exception e) {
      logger.error("Error during risk assessment for maintenance request: {}",
          request.getMaintenanceLogId(), e);
      return ResponseEntity.internalServerError().body(null);
    }
  }

  // 위험도 평가 응답 DTO
  public static class RiskAssessmentResponse {
    private String maintenanceLogId;
    private double riskScore;
    private String riskLevel;
    private String riskRecommendation;
    private boolean isHighRisk;

    public RiskAssessmentResponse(String maintenanceLogId, double riskScore, String riskLevel,
        String riskRecommendation, boolean isHighRisk) {
      this.maintenanceLogId = maintenanceLogId;
      this.riskScore = riskScore;
      this.riskLevel = riskLevel;
      this.riskRecommendation = riskRecommendation;
      this.isHighRisk = isHighRisk;
    }

    // Getters and Setters
    public String getMaintenanceLogId() {
      return maintenanceLogId;
    }

    public void setMaintenanceLogId(String maintenanceLogId) {
      this.maintenanceLogId = maintenanceLogId;
    }

    public double getRiskScore() {
      return riskScore;
    }

    public void setRiskScore(double riskScore) {
      this.riskScore = riskScore;
    }

    public String getRiskLevel() {
      return riskLevel;
    }

    public void setRiskLevel(String riskLevel) {
      this.riskLevel = riskLevel;
    }

    public String getRiskRecommendation() {
      return riskRecommendation;
    }

    public void setRiskRecommendation(String riskRecommendation) {
      this.riskRecommendation = riskRecommendation;
    }

    public boolean isHighRisk() {
      return isHighRisk;
    }

    public void setHighRisk(boolean highRisk) {
      isHighRisk = highRisk;
    }
  }
}
