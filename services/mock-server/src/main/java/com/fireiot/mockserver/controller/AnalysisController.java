package com.fireiot.mockserver.controller;

import com.fireiot.mockserver.model.Analysis;
import com.fireiot.mockserver.service.AnalysisService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/mock/analysis")
@Tag(name = "Analysis", description = "분석 결과 관리 API")
public class AnalysisController {

    @Autowired
    private AnalysisService analysisService;

    @GetMapping
    @Operation(summary = "모든 분석 결과 조회", description = "시스템의 모든 분석 결과를 조회합니다.")
    public ResponseEntity<List<Analysis>> getAllAnalyses() {
        List<Analysis> analyses = analysisService.getAllAnalyses();
        return ResponseEntity.ok(analyses);
    }

    @GetMapping("/{analysisId}")
    @Operation(summary = "분석 ID로 조회", description = "특정 분석 ID의 분석 결과를 조회합니다.")
    public ResponseEntity<Analysis> getAnalysisById(
            @Parameter(description = "분석 ID") @PathVariable String analysisId) {
        
        Optional<Analysis> analysis = analysisService.getAnalysisById(analysisId);
        return analysis.map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/facility/{facilityId}")
    @Operation(summary = "시설별 분석 결과 조회", description = "특정 시설의 모든 분석 결과를 조회합니다.")
    public ResponseEntity<List<Analysis>> getAnalysesByFacilityId(
            @Parameter(description = "시설 ID") @PathVariable String facilityId) {
        
        List<Analysis> analyses = analysisService.getAnalysesByFacilityId(facilityId);
        return ResponseEntity.ok(analyses);
    }

    @GetMapping("/incident/{incidentId}")
    @Operation(summary = "사고별 분석 결과 조회", description = "특정 사고의 모든 분석 결과를 조회합니다.")
    public ResponseEntity<List<Analysis>> getAnalysesByIncidentId(
            @Parameter(description = "사고 ID") @PathVariable String incidentId) {
        
        List<Analysis> analyses = analysisService.getAnalysesByIncidentId(incidentId);
        return ResponseEntity.ok(analyses);
    }

    @GetMapping("/type/{analysisType}")
    @Operation(summary = "타입별 분석 결과 조회", description = "특정 타입의 모든 분석 결과를 조회합니다.")
    public ResponseEntity<List<Analysis>> getAnalysesByType(
            @Parameter(description = "분석 타입") @PathVariable String analysisType) {
        
        List<Analysis> analyses = analysisService.getAnalysesByType(analysisType);
        return ResponseEntity.ok(analyses);
    }

    @GetMapping("/status/{status}")
    @Operation(summary = "상태별 분석 결과 조회", description = "특정 상태의 모든 분석 결과를 조회합니다.")
    public ResponseEntity<List<Analysis>> getAnalysesByStatus(
            @Parameter(description = "분석 상태") @PathVariable String status) {
        
        List<Analysis> analyses = analysisService.getAnalysesByStatus(status);
        return ResponseEntity.ok(analyses);
    }

    @GetMapping("/confidence-range")
    @Operation(summary = "신뢰도 범위별 분석 결과 조회", description = "특정 신뢰도 범위의 분석 결과를 조회합니다.")
    public ResponseEntity<List<Analysis>> getAnalysesByConfidenceRange(
            @Parameter(description = "최소 신뢰도") @RequestParam BigDecimal minConfidence,
            @Parameter(description = "최대 신뢰도") @RequestParam BigDecimal maxConfidence) {
        
        List<Analysis> analyses = analysisService.getAnalysesByConfidenceRange(minConfidence, maxConfidence);
        return ResponseEntity.ok(analyses);
    }

    @GetMapping("/risk-range")
    @Operation(summary = "위험도 범위별 분석 결과 조회", description = "특정 위험도 범위의 분석 결과를 조회합니다.")
    public ResponseEntity<List<Analysis>> getAnalysesByRiskRange(
            @Parameter(description = "최소 위험도") @RequestParam BigDecimal minRisk,
            @Parameter(description = "최대 위험도") @RequestParam BigDecimal maxRisk) {
        
        List<Analysis> analyses = analysisService.getAnalysesByRiskRange(minRisk, maxRisk);
        return ResponseEntity.ok(analyses);
    }

    @GetMapping("/date-range")
    @Operation(summary = "날짜 범위별 분석 결과 조회", description = "특정 날짜 범위의 분석 결과를 조회합니다.")
    public ResponseEntity<List<Analysis>> getAnalysesByDateRange(
            @Parameter(description = "시작 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startDate,
            @Parameter(description = "종료 날짜") @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endDate) {
        
        List<Analysis> analyses = analysisService.getAnalysesByDateRange(startDate, endDate);
        return ResponseEntity.ok(analyses);
    }

    @GetMapping("/high-confidence")
    @Operation(summary = "고신뢰도 분석 결과 조회", description = "특정 신뢰도 이상의 분석 결과를 조회합니다.")
    public ResponseEntity<List<Analysis>> getAnalysesWithHighConfidence(
            @Parameter(description = "신뢰도 임계값") @RequestParam BigDecimal threshold) {
        
        List<Analysis> analyses = analysisService.getAnalysesWithHighConfidence(threshold);
        return ResponseEntity.ok(analyses);
    }

    @GetMapping("/high-risk")
    @Operation(summary = "고위험도 분석 결과 조회", description = "특정 위험도 이상의 분석 결과를 조회합니다.")
    public ResponseEntity<List<Analysis>> getAnalysesWithHighRisk(
            @Parameter(description = "위험도 임계값") @RequestParam BigDecimal threshold) {
        
        List<Analysis> analyses = analysisService.getAnalysesWithHighRisk(threshold);
        return ResponseEntity.ok(analyses);
    }

    @GetMapping("/count")
    @Operation(summary = "총 분석 결과 수 조회", description = "시스템의 총 분석 결과 수를 조회합니다.")
    public ResponseEntity<Long> getTotalAnalysisCount() {
        long count = analysisService.getTotalAnalysisCount();
        return ResponseEntity.ok(count);
    }

    @PostMapping
    @Operation(summary = "분석 결과 생성", description = "새로운 분석 결과를 생성합니다.")
    public ResponseEntity<Analysis> createAnalysis(@RequestBody Analysis analysis) {
        Analysis savedAnalysis = analysisService.saveAnalysis(analysis);
        return ResponseEntity.ok(savedAnalysis);
    }

    @DeleteMapping("/{analysisId}")
    @Operation(summary = "분석 결과 삭제", description = "특정 분석 결과를 삭제합니다.")
    public ResponseEntity<Void> deleteAnalysis(
            @Parameter(description = "분석 ID") @PathVariable String analysisId) {
        
        boolean deleted = analysisService.deleteAnalysis(analysisId);
        if (deleted) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
