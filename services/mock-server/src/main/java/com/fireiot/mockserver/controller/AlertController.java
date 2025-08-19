package com.fireiot.mockserver.controller;

import com.fireiot.mockserver.model.Alert;
import com.fireiot.mockserver.service.AlertService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/mock/alert")
@Tag(name = "Alert", description = "알림 관리 API")
public class AlertController {

    @Autowired
    private AlertService alertService;

    @GetMapping
    @Operation(summary = "모든 알림 조회", description = "시스템의 모든 알림을 조회합니다.")
    public ResponseEntity<List<Alert>> getAllAlerts() {
        List<Alert> alerts = alertService.getAllAlerts();
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/{alertId}")
    @Operation(summary = "알림 ID로 조회", description = "특정 알림 ID의 알림을 조회합니다.")
    public ResponseEntity<Alert> getAlertById(
            @Parameter(description = "알림 ID") @PathVariable String alertId) {
        
        Optional<Alert> alert = alertService.getAlertById(alertId);
        return alert.map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/equipment/{equipmentId}")
    @Operation(summary = "장비별 알림 조회", description = "특정 장비의 모든 알림을 조회합니다.")
    public ResponseEntity<List<Alert>> getAlertsByEquipmentId(
            @Parameter(description = "장비 ID") @PathVariable String equipmentId) {
        
        List<Alert> alerts = alertService.getAlertsByEquipmentId(equipmentId);
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/facility/{facilityId}")
    @Operation(summary = "시설별 알림 조회", description = "특정 시설의 모든 알림을 조회합니다.")
    public ResponseEntity<List<Alert>> getAlertsByFacilityId(
            @Parameter(description = "시설 ID") @PathVariable String facilityId) {
        
        List<Alert> alerts = alertService.getAlertsByFacilityId(facilityId);
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/location/{equipmentLocation}")
    @Operation(summary = "위치별 알림 조회", description = "특정 위치의 모든 알림을 조회합니다.")
    public ResponseEntity<List<Alert>> getAlertsByLocation(
            @Parameter(description = "장비 위치") @PathVariable String equipmentLocation) {
        
        List<Alert> alerts = alertService.getAlertsByLocation(equipmentLocation);
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/type/{alertType}")
    @Operation(summary = "타입별 알림 조회", description = "특정 타입의 모든 알림을 조회합니다.")
    public ResponseEntity<List<Alert>> getAlertsByType(
            @Parameter(description = "알림 타입") @PathVariable Alert.AlertType alertType) {
        
        List<Alert> alerts = alertService.getAlertsByType(alertType);
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/severity/{severity}")
    @Operation(summary = "심각도별 알림 조회", description = "특정 심각도의 모든 알림을 조회합니다.")
    public ResponseEntity<List<Alert>> getAlertsBySeverity(
            @Parameter(description = "심각도") @PathVariable Alert.AlertSeverity severity) {
        
        List<Alert> alerts = alertService.getAlertsBySeverity(severity);
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/status/{status}")
    @Operation(summary = "상태별 알림 조회", description = "특정 상태의 모든 알림을 조회합니다.")
    public ResponseEntity<List<Alert>> getAlertsByStatus(
            @Parameter(description = "알림 상태") @PathVariable String status) {
        
        List<Alert> alerts = alertService.getAlertsByStatus(status);
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/date-range")
    @Operation(summary = "날짜 범위별 알림 조회", description = "특정 날짜 범위의 알림을 조회합니다.")
    public ResponseEntity<List<Alert>> getAlertsByDateRange(
            @Parameter(description = "시작 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @Parameter(description = "종료 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        
        List<Alert> alerts = alertService.getAlertsByDateRange(startDate, endDate);
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/active")
    @Operation(summary = "활성 알림 조회", description = "활성 상태의 모든 알림을 조회합니다.")
    public ResponseEntity<List<Alert>> getActiveAlerts() {
        List<Alert> alerts = alertService.getActiveAlerts();
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/resolved")
    @Operation(summary = "해결된 알림 조회", description = "해결된 모든 알림을 조회합니다.")
    public ResponseEntity<List<Alert>> getResolvedAlerts() {
        List<Alert> alerts = alertService.getResolvedAlerts();
        return ResponseEntity.ok(alerts);
    }

    @GetMapping("/count")
    @Operation(summary = "총 알림 수 조회", description = "시스템의 총 알림 수를 조회합니다.")
    public ResponseEntity<Long> getTotalAlertCount() {
        long count = alertService.getTotalAlertCount();
        return ResponseEntity.ok(count);
    }

    @PostMapping
    @Operation(summary = "알림 생성", description = "새로운 알림을 생성합니다.")
    public ResponseEntity<Alert> createAlert(@RequestBody Alert alert) {
        Alert savedAlert = alertService.saveAlert(alert);
        return ResponseEntity.ok(savedAlert);
    }

    @DeleteMapping("/{alertId}")
    @Operation(summary = "알림 삭제", description = "특정 알림을 삭제합니다.")
    public ResponseEntity<Void> deleteAlert(
            @Parameter(description = "알림 ID") @PathVariable String alertId) {
        
        boolean deleted = alertService.deleteAlert(alertId);
        if (deleted) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
