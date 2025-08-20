package com.fireiot.mockserver.controller;

import com.fireiot.mockserver.model.Incident;
import com.fireiot.mockserver.service.IncidentService;
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
@RequestMapping("/mock/incident")
@Tag(name = "Incident", description = "사고 관리 API")
public class IncidentController {

    @Autowired
    private IncidentService incidentService;

    @GetMapping
    @Operation(summary = "모든 사고 조회", description = "시스템의 모든 사고를 조회합니다.")
    public ResponseEntity<List<Incident>> getAllIncidents() {
        List<Incident> incidents = incidentService.getAllIncidents();
        return ResponseEntity.ok(incidents);
    }

    @GetMapping("/{incidentId}")
    @Operation(summary = "사고 ID로 조회", description = "특정 사고 ID의 사고를 조회합니다.")
    public ResponseEntity<Incident> getIncidentById(
            @Parameter(description = "사고 ID") @PathVariable String incidentId) {
        
        Optional<Incident> incident = incidentService.getIncidentById(incidentId);
        return incident.map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/facility/{facilityId}")
    @Operation(summary = "시설별 사고 조회", description = "특정 시설의 모든 사고를 조회합니다.")
    public ResponseEntity<List<Incident>> getIncidentsByFacilityId(
            @Parameter(description = "시설 ID") @PathVariable String facilityId) {
        
        List<Incident> incidents = incidentService.getIncidentsByFacilityId(facilityId);
        return ResponseEntity.ok(incidents);
    }

    @GetMapping("/type/{incidentType}")
    @Operation(summary = "타입별 사고 조회", description = "특정 타입의 모든 사고를 조회합니다.")
    public ResponseEntity<List<Incident>> getIncidentsByType(
            @Parameter(description = "사고 타입") @PathVariable String incidentType) {
        
        List<Incident> incidents = incidentService.getIncidentsByType(incidentType);
        return ResponseEntity.ok(incidents);
    }

    @GetMapping("/severity/{severity}")
    @Operation(summary = "심각도별 사고 조회", description = "특정 심각도의 모든 사고를 조회합니다.")
    public ResponseEntity<List<Incident>> getIncidentsBySeverity(
            @Parameter(description = "심각도") @PathVariable Incident.IncidentSeverity severity) {
        
        List<Incident> incidents = incidentService.getIncidentsBySeverity(severity);
        return ResponseEntity.ok(incidents);
    }

    @GetMapping("/date-range")
    @Operation(summary = "날짜 범위별 사고 조회", description = "특정 날짜 범위의 사고를 조회합니다.")
    public ResponseEntity<List<Incident>> getIncidentsByDateRange(
            @Parameter(description = "시작 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @Parameter(description = "종료 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        
        List<Incident> incidents = incidentService.getIncidentsByDateRange(startDate, endDate);
        return ResponseEntity.ok(incidents);
    }

    @GetMapping("/unresolved")
    @Operation(summary = "미해결 사고 조회", description = "해결되지 않은 모든 사고를 조회합니다.")
    public ResponseEntity<List<Incident>> getUnresolvedIncidents() {
        List<Incident> incidents = incidentService.getUnresolvedIncidents();
        return ResponseEntity.ok(incidents);
    }

    @GetMapping("/count")
    @Operation(summary = "총 사고 수 조회", description = "시스템의 총 사고 수를 조회합니다.")
    public ResponseEntity<Long> getTotalIncidentCount() {
        long count = incidentService.getTotalIncidentCount();
        return ResponseEntity.ok(count);
    }

    @PostMapping
    @Operation(summary = "사고 생성", description = "새로운 사고를 생성합니다.")
    public ResponseEntity<Incident> createIncident(@RequestBody Incident incident) {
        Incident savedIncident = incidentService.saveIncident(incident);
        return ResponseEntity.ok(savedIncident);
    }

    @DeleteMapping("/{incidentId}")
    @Operation(summary = "사고 삭제", description = "특정 사고를 삭제합니다.")
    public ResponseEntity<Void> deleteIncident(
            @Parameter(description = "사고 ID") @PathVariable String incidentId) {
        
        boolean deleted = incidentService.deleteIncident(incidentId);
        if (deleted) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
