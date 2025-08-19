package com.fireiot.mockserver.controller;

import com.fireiot.mockserver.model.Realtime;
import com.fireiot.mockserver.service.RealtimeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/mock/realtime")
@Tag(name = "Realtime", description = "실시간 측정 데이터 관리 API")
public class RealtimeController {

    @Autowired
    private RealtimeService realtimeService;

    @GetMapping
    @Operation(summary = "모든 실시간 측정 데이터 조회", description = "시스템의 모든 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getAllRealtimeData() {
        List<Realtime> data = realtimeService.getAllRealtimeData();
        return ResponseEntity.ok(data);
    }

    @GetMapping("/{equipmentDataId}")
    @Operation(summary = "장비 데이터 ID로 실시간 측정 데이터 조회", description = "특정 장비 데이터 ID의 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<Realtime> getRealtimeDataById(
            @Parameter(description = "장비 데이터 ID") @PathVariable String equipmentDataId) {
        
        Optional<Realtime> data = realtimeService.getRealtimeDataById(equipmentDataId);
        return data.map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/equipment/{equipmentId}")
    @Operation(summary = "장비별 실시간 측정 데이터 조회", description = "특정 장비의 모든 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getRealtimeDataByEquipmentId(
            @Parameter(description = "장비 ID") @PathVariable String equipmentId) {
        
        List<Realtime> data = realtimeService.getRealtimeDataByEquipmentId(equipmentId);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/facility/{facilityId}")
    @Operation(summary = "시설별 실시간 측정 데이터 조회", description = "특정 시설의 모든 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getRealtimeDataByFacilityId(
            @Parameter(description = "시설 ID") @PathVariable String facilityId) {
        
        List<Realtime> data = realtimeService.getRealtimeDataByFacilityId(facilityId);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/location/{equipmentLocation}")
    @Operation(summary = "위치별 실시간 측정 데이터 조회", description = "특정 위치의 모든 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getRealtimeDataByLocation(
            @Parameter(description = "장비 위치") @PathVariable String equipmentLocation) {
        
        List<Realtime> data = realtimeService.getRealtimeDataByLocation(equipmentLocation);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/temperature-range")
    @Operation(summary = "온도 범위별 실시간 측정 데이터 조회", description = "특정 온도 범위의 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getRealtimeDataByTemperatureRange(
            @Parameter(description = "최소 온도") @RequestParam BigDecimal minTemp,
            @Parameter(description = "최대 온도") @RequestParam BigDecimal maxTemp) {
        
        List<Realtime> data = realtimeService.getRealtimeDataByTemperatureRange(minTemp, maxTemp);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/humidity-range")
    @Operation(summary = "습도 범위별 실시간 측정 데이터 조회", description = "특정 습도 범위의 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getRealtimeDataByHumidityRange(
            @Parameter(description = "최소 습도") @RequestParam BigDecimal minHumidity,
            @Parameter(description = "최대 습도") @RequestParam BigDecimal maxHumidity) {
        
        List<Realtime> data = realtimeService.getRealtimeDataByHumidityRange(minHumidity, maxHumidity);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/smoke-density-threshold/{threshold}")
    @Operation(summary = "연기 밀도 임계값 이상 실시간 측정 데이터 조회", description = "특정 연기 밀도 임계값 이상의 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getRealtimeDataWithHighSmokeDensity(
            @Parameter(description = "연기 밀도 임계값") @PathVariable BigDecimal threshold) {
        
        List<Realtime> data = realtimeService.getRealtimeDataWithHighSmokeDensity(threshold);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/co-level-threshold/{threshold}")
    @Operation(summary = "CO 레벨 임계값 이상 실시간 측정 데이터 조회", description = "특정 CO 레벨 임계값 이상의 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getRealtimeDataWithHighCoLevel(
            @Parameter(description = "CO 레벨 임계값") @PathVariable BigDecimal threshold) {
        
        List<Realtime> data = realtimeService.getRealtimeDataWithHighCoLevel(threshold);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/gas-level-threshold/{threshold}")
    @Operation(summary = "가스 레벨 임계값 이상 실시간 측정 데이터 조회", description = "특정 가스 레벨 임계값 이상의 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getRealtimeDataWithHighGasLevel(
            @Parameter(description = "가스 레벨 임계값") @PathVariable BigDecimal threshold) {
        
        List<Realtime> data = realtimeService.getRealtimeDataWithHighGasLevel(threshold);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/temperature-range-query")
    @Operation(summary = "온도 범위별 실시간 측정 데이터 조회 (Query)", description = "@Query를 사용하여 특정 온도 범위의 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getRealtimeDataByTemperatureRangeQuery(
            @Parameter(description = "최소 온도") @RequestParam BigDecimal minTemp,
            @Parameter(description = "최대 온도") @RequestParam BigDecimal maxTemp) {
        
        List<Realtime> data = realtimeService.getRealtimeDataByTemperatureRangeQuery(minTemp, maxTemp);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/humidity-range-query")
    @Operation(summary = "습도 범위별 실시간 측정 데이터 조회 (Query)", description = "@Query를 사용하여 특정 습도 범위의 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getRealtimeDataByHumidityRangeQuery(
            @Parameter(description = "최소 습도") @RequestParam BigDecimal minHumidity,
            @Parameter(description = "최대 습도") @RequestParam BigDecimal maxHumidity) {
        
        List<Realtime> data = realtimeService.getRealtimeDataByHumidityRangeQuery(minHumidity, maxHumidity);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/smoke-density-threshold-query/{threshold}")
    @Operation(summary = "연기 밀도 임계값 이상 실시간 측정 데이터 조회 (Query)", description = "@Query를 사용하여 특정 연기 밀도 임계값 이상의 실시간 측정 데이터를 조회합니다.")
    public ResponseEntity<List<Realtime>> getRealtimeDataBySmokeDensityThreshold(
            @Parameter(description = "연기 밀도 임계값") @PathVariable BigDecimal threshold) {
        
        List<Realtime> data = realtimeService.getRealtimeDataBySmokeDensityThreshold(threshold);
        return ResponseEntity.ok(data);
    }

    @PostMapping
    @Operation(summary = "실시간 측정 데이터 생성", description = "새로운 실시간 측정 데이터를 생성합니다.")
    public ResponseEntity<Realtime> createRealtimeData(@RequestBody Realtime realtimeData) {
        Realtime savedData = realtimeService.saveRealtimeData(realtimeData);
        return ResponseEntity.ok(savedData);
    }

    @DeleteMapping("/{equipmentDataId}")
    @Operation(summary = "실시간 측정 데이터 삭제", description = "특정 실시간 측정 데이터를 삭제합니다.")
    public ResponseEntity<Void> deleteRealtimeData(
            @Parameter(description = "장비 데이터 ID") @PathVariable String equipmentDataId) {
        
        boolean deleted = realtimeService.deleteRealtimeData(equipmentDataId);
        if (deleted) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
