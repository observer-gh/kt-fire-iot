package com.fireiot.mockserver.controller;

import com.fireiot.mockserver.model.Equipment;
import com.fireiot.mockserver.service.EquipmentService;
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
@RequestMapping("/mock/equipment")
@Tag(name = "Equipment", description = "장비 관리 API")
public class EquipmentController {

    @Autowired
    private EquipmentService equipmentService;

    @GetMapping
    @Operation(summary = "모든 장비 조회", description = "시스템의 모든 장비를 조회합니다.")
    public ResponseEntity<List<Equipment>> getAllEquipment() {
        List<Equipment> equipment = equipmentService.getAllEquipment();
        return ResponseEntity.ok(equipment);
    }

    @GetMapping("/{equipmentId}")
    @Operation(summary = "장비 ID로 조회", description = "특정 장비 ID의 장비를 조회합니다.")
    public ResponseEntity<Equipment> getEquipmentById(
            @Parameter(description = "장비 ID") @PathVariable String equipmentId) {
        
        Optional<Equipment> equipment = equipmentService.getEquipmentById(equipmentId);
        return equipment.map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/facility/{facilityId}")
    @Operation(summary = "시설별 장비 조회", description = "특정 시설의 모든 장비를 조회합니다.")
    public ResponseEntity<List<Equipment>> getEquipmentByFacilityId(
            @Parameter(description = "시설 ID") @PathVariable String facilityId) {
        
        List<Equipment> equipment = equipmentService.getEquipmentByFacilityId(facilityId);
        return ResponseEntity.ok(equipment);
    }

    @GetMapping("/type/{equipmentType}")
    @Operation(summary = "타입별 장비 조회", description = "특정 타입의 모든 장비를 조회합니다.")
    public ResponseEntity<List<Equipment>> getEquipmentByType(
            @Parameter(description = "장비 타입") @PathVariable String equipmentType) {
        
        List<Equipment> equipment = equipmentService.getEquipmentByType(equipmentType);
        return ResponseEntity.ok(equipment);
    }

    @GetMapping("/status/{statusCode}")
    @Operation(summary = "상태별 장비 조회", description = "특정 상태의 모든 장비를 조회합니다.")
    public ResponseEntity<List<Equipment>> getEquipmentByStatusCode(
            @Parameter(description = "상태 코드") @PathVariable String statusCode) {
        
        List<Equipment> equipment = equipmentService.getEquipmentByStatusCode(statusCode);
        return ResponseEntity.ok(equipment);
    }

    @GetMapping("/location/{equipmentLocation}")
    @Operation(summary = "위치별 장비 조회", description = "특정 위치의 모든 장비를 조회합니다.")
    public ResponseEntity<List<Equipment>> getEquipmentByLocation(
            @Parameter(description = "장비 위치") @PathVariable String equipmentLocation) {
        
        List<Equipment> equipment = equipmentService.getEquipmentByLocation(equipmentLocation);
        return ResponseEntity.ok(equipment);
    }

    @GetMapping("/installation-period")
    @Operation(summary = "설치 기간별 장비 조회", description = "특정 설치 기간의 장비를 조회합니다.")
    public ResponseEntity<List<Equipment>> getEquipmentByInstallationPeriod(
            @Parameter(description = "시작 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @Parameter(description = "종료 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        
        List<Equipment> equipment = equipmentService.getEquipmentByInstallationPeriod(startDate, endDate);
        return ResponseEntity.ok(equipment);
    }

    @GetMapping("/expiring")
    @Operation(summary = "만료 예정 장비 조회", description = "특정 날짜 이전에 만료되는 장비를 조회합니다.")
    public ResponseEntity<List<Equipment>> getExpiringEquipment(
            @Parameter(description = "만료 기준 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime expiryDate) {
        
        List<Equipment> equipment = equipmentService.getExpiringEquipment(expiryDate);
        return ResponseEntity.ok(equipment);
    }

    @GetMapping("/facility-type")
    @Operation(summary = "시설 및 타입별 장비 조회", description = "특정 시설과 타입의 장비를 조회합니다.")
    public ResponseEntity<List<Equipment>> getEquipmentByFacilityAndType(
            @Parameter(description = "시설 ID") @RequestParam String facilityId,
            @Parameter(description = "장비 타입") @RequestParam String equipmentType) {
        
        List<Equipment> equipment = equipmentService.getEquipmentByFacilityAndType(facilityId, equipmentType);
        return ResponseEntity.ok(equipment);
    }

    @GetMapping("/installed-in-period")
    @Operation(summary = "기간 내 설치된 장비 조회", description = "특정 기간 내에 설치된 장비를 조회합니다.")
    public ResponseEntity<List<Equipment>> getEquipmentInstalledInPeriod(
            @Parameter(description = "시작 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @Parameter(description = "종료 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        
        List<Equipment> equipment = equipmentService.getEquipmentInstalledInPeriod(startDate, endDate);
        return ResponseEntity.ok(equipment);
    }

    @GetMapping("/count")
    @Operation(summary = "총 장비 수 조회", description = "시스템의 총 장비 수를 조회합니다.")
    public ResponseEntity<Long> getTotalEquipmentCount() {
        long count = equipmentService.getTotalEquipmentCount();
        return ResponseEntity.ok(count);
    }

    @PostMapping
    @Operation(summary = "장비 생성", description = "새로운 장비를 생성합니다.")
    public ResponseEntity<Equipment> createEquipment(@RequestBody Equipment equipment) {
        Equipment savedEquipment = equipmentService.saveEquipment(equipment);
        return ResponseEntity.ok(savedEquipment);
    }

    @DeleteMapping("/{equipmentId}")
    @Operation(summary = "장비 삭제", description = "특정 장비를 삭제합니다.")
    public ResponseEntity<Void> deleteEquipment(
            @Parameter(description = "장비 ID") @PathVariable String equipmentId) {
        
        boolean deleted = equipmentService.deleteEquipment(equipmentId);
        if (deleted) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
