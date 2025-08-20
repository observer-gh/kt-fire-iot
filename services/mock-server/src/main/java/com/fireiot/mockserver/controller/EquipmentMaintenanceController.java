package com.fireiot.mockserver.controller;

import com.fireiot.mockserver.model.EquipmentMaintenance;
import com.fireiot.mockserver.service.EquipmentMaintenanceService;
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
@RequestMapping("/mock/equipment-maintenance")
@Tag(name = "Equipment Maintenance", description = "장비 유지보수 관리 API")
public class EquipmentMaintenanceController {

    @Autowired
    private EquipmentMaintenanceService equipmentMaintenanceService;

    @GetMapping
    @Operation(summary = "모든 유지보수 로그 조회", description = "시스템의 모든 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getAllMaintenanceLogs() {
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getAllMaintenanceLogs();
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/{maintenanceLogId}")
    @Operation(summary = "유지보수 로그 ID로 조회", description = "특정 유지보수 로그 ID의 로그를 조회합니다.")
    public ResponseEntity<EquipmentMaintenance> getMaintenanceLogById(
            @Parameter(description = "유지보수 로그 ID") @PathVariable String maintenanceLogId) {
        
        Optional<EquipmentMaintenance> log = equipmentMaintenanceService.getMaintenanceLogById(maintenanceLogId);
        return log.map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/equipment/{equipmentId}")
    @Operation(summary = "장비별 유지보수 로그 조회", description = "특정 장비의 모든 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getMaintenanceLogsByEquipmentId(
            @Parameter(description = "장비 ID") @PathVariable String equipmentId) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getMaintenanceLogsByEquipmentId(equipmentId);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/facility/{facilityId}")
    @Operation(summary = "시설별 유지보수 로그 조회", description = "특정 시설의 모든 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getMaintenanceLogsByFacilityId(
            @Parameter(description = "시설 ID") @PathVariable String facilityId) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getMaintenanceLogsByFacilityId(facilityId);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/location/{equipmentLocation}")
    @Operation(summary = "위치별 유지보수 로그 조회", description = "특정 위치의 모든 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getMaintenanceLogsByLocation(
            @Parameter(description = "장비 위치") @PathVariable String equipmentLocation) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getMaintenanceLogsByLocation(equipmentLocation);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/type/{maintenanceType}")
    @Operation(summary = "타입별 유지보수 로그 조회", description = "특정 타입의 모든 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getMaintenanceLogsByType(
            @Parameter(description = "유지보수 타입") @PathVariable EquipmentMaintenance.MaintenanceType maintenanceType) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getMaintenanceLogsByType(maintenanceType);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/status/{statusCode}")
    @Operation(summary = "상태별 유지보수 로그 조회", description = "특정 상태의 모든 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getMaintenanceLogsByStatus(
            @Parameter(description = "상태 코드") @PathVariable String statusCode) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getMaintenanceLogsByStatus(statusCode);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/manager/{manager}")
    @Operation(summary = "담당자별 유지보수 로그 조회", description = "특정 담당자의 모든 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getMaintenanceLogsByManager(
            @Parameter(description = "담당자") @PathVariable String manager) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getMaintenanceLogsByManager(manager);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/scheduled-date-range")
    @Operation(summary = "예정일 범위별 유지보수 로그 조회", description = "특정 예정일 범위의 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getMaintenanceLogsByScheduledDateRange(
            @Parameter(description = "시작 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @Parameter(description = "종료 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getMaintenanceLogsByScheduledDateRange(startDate, endDate);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/performed-date-range")
    @Operation(summary = "수행일 범위별 유지보수 로그 조회", description = "특정 수행일 범위의 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getMaintenanceLogsByPerformedDateRange(
            @Parameter(description = "시작 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @Parameter(description = "종료 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getMaintenanceLogsByPerformedDateRange(startDate, endDate);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/next-scheduled")
    @Operation(summary = "다음 예정일 기준 유지보수 로그 조회", description = "특정 날짜 이전의 다음 예정일을 가진 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getMaintenanceLogsByNextScheduledDate(
            @Parameter(description = "기준 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime date) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getMaintenanceLogsByNextScheduledDate(date);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/equipment-status")
    @Operation(summary = "장비 및 상태별 유지보수 로그 조회", description = "특정 장비와 상태의 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getMaintenanceLogsByEquipmentAndStatus(
            @Parameter(description = "장비 ID") @RequestParam String equipmentId,
            @Parameter(description = "상태 코드") @RequestParam String statusCode) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getMaintenanceLogsByEquipmentAndStatus(equipmentId, statusCode);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/scheduled-in-period")
    @Operation(summary = "기간 내 예정된 유지보수 로그 조회", description = "특정 기간 내에 예정된 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getScheduledMaintenanceInPeriod(
            @Parameter(description = "시작 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @Parameter(description = "종료 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate,
            @Parameter(description = "상태 코드") @RequestParam String statusCode) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getScheduledMaintenanceInPeriod(startDate, endDate, statusCode);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/overdue")
    @Operation(summary = "지연된 유지보수 로그 조회", description = "현재 날짜 기준으로 지연된 유지보수 로그를 조회합니다.")
    public ResponseEntity<List<EquipmentMaintenance>> getOverdueMaintenance(
            @Parameter(description = "현재 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime currentDate) {
        
        List<EquipmentMaintenance> logs = equipmentMaintenanceService.getOverdueMaintenance(currentDate);
        return ResponseEntity.ok(logs);
    }

    @GetMapping("/count")
    @Operation(summary = "총 유지보수 로그 수 조회", description = "시스템의 총 유지보수 로그 수를 조회합니다.")
    public ResponseEntity<Long> getTotalMaintenanceLogCount() {
        long count = equipmentMaintenanceService.getTotalMaintenanceLogCount();
        return ResponseEntity.ok(count);
    }

    @PostMapping
    @Operation(summary = "유지보수 로그 생성", description = "새로운 유지보수 로그를 생성합니다.")
    public ResponseEntity<EquipmentMaintenance> createMaintenanceLog(@RequestBody EquipmentMaintenance maintenanceLog) {
        EquipmentMaintenance savedLog = equipmentMaintenanceService.saveMaintenanceLog(maintenanceLog);
        return ResponseEntity.ok(savedLog);
    }

    @DeleteMapping("/{maintenanceLogId}")
    @Operation(summary = "유지보수 로그 삭제", description = "특정 유지보수 로그를 삭제합니다.")
    public ResponseEntity<Void> deleteMaintenanceLog(
            @Parameter(description = "유지보수 로그 ID") @PathVariable String maintenanceLogId) {
        
        boolean deleted = equipmentMaintenanceService.deleteMaintenanceLog(maintenanceLogId);
        if (deleted) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
