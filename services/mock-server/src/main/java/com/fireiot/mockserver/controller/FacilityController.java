package com.fireiot.mockserver.controller;

import com.fireiot.mockserver.model.Facility;
import com.fireiot.mockserver.service.FacilityService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/mock/facility")
@Tag(name = "Facility", description = "시설 관리 API")
public class FacilityController {

    @Autowired
    private FacilityService facilityService;

    @GetMapping
    @Operation(summary = "모든 시설 조회", description = "시스템의 모든 시설을 조회합니다.")
    public ResponseEntity<List<Facility>> getAllFacilities() {
        List<Facility> facilities = facilityService.getAllFacilities();
        return ResponseEntity.ok(facilities);
    }

    @GetMapping("/{facilityId}")
    @Operation(summary = "시설 ID로 조회", description = "특정 시설 ID의 시설을 조회합니다.")
    public ResponseEntity<Facility> getFacilityById(
            @Parameter(description = "시설 ID") @PathVariable String facilityId) {
        
        Optional<Facility> facility = facilityService.getFacilityById(facilityId);
        return facility.map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/type/{facilityType}")
    @Operation(summary = "타입별 시설 조회", description = "특정 타입의 모든 시설을 조회합니다.")
    public ResponseEntity<List<Facility>> getFacilitiesByType(
            @Parameter(description = "시설 타입") @PathVariable String facilityType) {
        
        List<Facility> facilities = facilityService.getFacilitiesByType(facilityType);
        return ResponseEntity.ok(facilities);
    }

    @GetMapping("/risk/{riskLevel}")
    @Operation(summary = "위험도별 시설 조회", description = "특정 위험도의 모든 시설을 조회합니다.")
    public ResponseEntity<List<Facility>> getFacilitiesByRiskLevel(
            @Parameter(description = "위험도") @PathVariable String riskLevel) {
        
        List<Facility> facilities = facilityService.getFacilitiesByRiskLevel(riskLevel);
        return ResponseEntity.ok(facilities);
    }

    @GetMapping("/manager/{managerName}")
    @Operation(summary = "관리자별 시설 조회", description = "특정 관리자의 모든 시설을 조회합니다.")
    public ResponseEntity<List<Facility>> getFacilitiesByManager(
            @Parameter(description = "관리자명") @PathVariable String managerName) {
        
        List<Facility> facilities = facilityService.getFacilitiesByManager(managerName);
        return ResponseEntity.ok(facilities);
    }

    @GetMapping("/alerts/{minCount}")
    @Operation(summary = "활성 알림이 있는 시설 조회", description = "특정 개수 이상의 활성 알림이 있는 시설을 조회합니다.")
    public ResponseEntity<List<Facility>> getFacilitiesWithActiveAlerts(
            @Parameter(description = "최소 알림 개수") @PathVariable Integer minCount) {
        
        List<Facility> facilities = facilityService.getFacilitiesWithActiveAlerts(minCount);
        return ResponseEntity.ok(facilities);
    }

    @GetMapping("/online")
    @Operation(summary = "온라인 센서가 있는 시설 조회", description = "특정 개수 이상의 온라인 센서가 있는 시설을 조회합니다.")
    public ResponseEntity<List<Facility>> getFacilitiesWithOnlineSensors(
            @Parameter(description = "최소 온라인 센서 개수") @RequestParam(defaultValue = "1") Integer minCount) {
        
        List<Facility> facilities = facilityService.getFacilitiesWithOnlineSensors(minCount);
        return ResponseEntity.ok(facilities);
    }

    @GetMapping("/address/{address}")
    @Operation(summary = "주소별 시설 조회", description = "특정 주소를 포함하는 시설을 조회합니다.")
    public ResponseEntity<List<Facility>> getFacilitiesByAddress(
            @Parameter(description = "주소") @PathVariable String address) {
        
        List<Facility> facilities = facilityService.getFacilitiesByAddress(address);
        return ResponseEntity.ok(facilities);
    }

    @GetMapping("/count")
    @Operation(summary = "총 시설 수 조회", description = "시스템의 총 시설 수를 조회합니다.")
    public ResponseEntity<Long> getTotalFacilityCount() {
        long count = facilityService.getTotalFacilityCount();
        return ResponseEntity.ok(count);
    }

    @PostMapping
    @Operation(summary = "시설 생성", description = "새로운 시설을 생성합니다.")
    public ResponseEntity<Facility> createFacility(@RequestBody Facility facility) {
        Facility savedFacility = facilityService.saveFacility(facility);
        return ResponseEntity.ok(savedFacility);
    }

    @DeleteMapping("/{facilityId}")
    @Operation(summary = "시설 삭제", description = "특정 시설을 삭제합니다.")
    public ResponseEntity<Void> deleteFacility(
            @Parameter(description = "시설 ID") @PathVariable String facilityId) {
        
        boolean deleted = facilityService.deleteFacility(facilityId);
        if (deleted) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
