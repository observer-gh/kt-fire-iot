package com.fireiot.mockserver.controller;

import com.fireiot.mockserver.dto.RawSensorDataDto;
import com.fireiot.mockserver.model.Realtime;
import com.fireiot.mockserver.service.RealtimeDataGeneratorService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/mock/realtime-generator")
@Tag(name = "Realtime Data Generator", description = "실시간 데이터 생성 API - Datalake 연동용")
public class RealtimeDataGeneratorController {

    @Autowired
    private RealtimeDataGeneratorService realtimeDataGeneratorService;

    @GetMapping("/generate")
    @Operation(summary = "기본 실시간 데이터 생성",
            description = "기본값(10개)의 실시간 데이터를 생성합니다. 90%는 정상, 10%는 이상 데이터입니다.")
    public ResponseEntity<List<Realtime>> generateDefaultRealtimeData() {
        List<Realtime> data = realtimeDataGeneratorService.generateRealtimeData(10);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/generate/{count}")
    @Operation(summary = "지정된 개수의 실시간 데이터 생성",
            description = "지정된 개수만큼 실시간 데이터를 생성합니다. 90%는 정상, 10%는 이상 데이터입니다.")
    public ResponseEntity<List<Realtime>> generateRealtimeData(
            @Parameter(description = "생성할 데이터 개수 (1-1000)") @PathVariable int count) {

        if (count < 1 || count > 1000) {
            return ResponseEntity.badRequest().build();
        }

        List<Realtime> data = realtimeDataGeneratorService.generateRealtimeData(count);
        return ResponseEntity.ok(data);
    }

    @PostMapping("/generate")
    @Operation(summary = "POST 요청으로 실시간 데이터 생성",
            description = "POST 요청을 통해 실시간 데이터를 생성합니다. 기본값은 10개입니다.")
    public ResponseEntity<List<Realtime>> generateRealtimeDataPost(@Parameter(
            description = "생성할 데이터 개수 (기본값: 10)") @RequestParam(defaultValue = "10") int count) {

        if (count < 1 || count > 1000) {
            return ResponseEntity.badRequest().build();
        }

        List<Realtime> data = realtimeDataGeneratorService.generateRealtimeData(count);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/generate/batch")
    @Operation(summary = "배치용 실시간 데이터 생성",
            description = "배치 처리용으로 대량의 실시간 데이터를 생성합니다. 기본값은 100개입니다.")
    public ResponseEntity<List<Realtime>> generateBatchRealtimeData(@Parameter(
            description = "생성할 데이터 개수 (기본값: 100)") @RequestParam(defaultValue = "100") int count) {

        if (count < 1 || count > 1000) {
            return ResponseEntity.badRequest().build();
        }

        List<Realtime> data = realtimeDataGeneratorService.generateRealtimeData(count);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/generate/stream")
    @Operation(summary = "스트리밍용 실시간 데이터 생성",
            description = "스트리밍 처리용으로 작은 단위의 실시간 데이터를 생성합니다. 기본값은 5개입니다.")
    public ResponseEntity<List<Realtime>> generateStreamRealtimeData(@Parameter(
            description = "생성할 데이터 개수 (기본값: 5)") @RequestParam(defaultValue = "5") int count) {

        if (count < 1 || count > 100) {
            return ResponseEntity.badRequest().build();
        }

        List<Realtime> data = realtimeDataGeneratorService.generateRealtimeData(count);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/generate/health-check")
    @Operation(summary = "헬스체크용 실시간 데이터 생성",
            description = "헬스체크용으로 최소한의 실시간 데이터를 생성합니다. 항상 1개를 생성합니다.")
    public ResponseEntity<List<Realtime>> generateHealthCheckRealtimeData() {
        List<Realtime> data = realtimeDataGeneratorService.generateRealtimeData(1);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/generate/performance-test")
    @Operation(summary = "성능 테스트용 실시간 데이터 생성",
            description = "성능 테스트용으로 중간 규모의 실시간 데이터를 생성합니다. 기본값은 500개입니다.")
    public ResponseEntity<List<Realtime>> generatePerformanceTestRealtimeData(@Parameter(
            description = "생성할 데이터 개수 (기본값: 500)") @RequestParam(defaultValue = "500") int count) {

        if (count < 100 || count > 1000) {
            return ResponseEntity.badRequest().build();
        }

        List<Realtime> data = realtimeDataGeneratorService.generateRealtimeData(count);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/datalake/generate")
    @Operation(summary = "Datalake용 실시간 데이터 생성",
            description = "Datalake의 RawSensorData 모델과 정확히 맞는 형태로 데이터를 생성합니다. 기본값은 10개입니다.")
    public ResponseEntity<List<RawSensorDataDto>> generateDatalakeData(@Parameter(
            description = "생성할 데이터 개수 (기본값: 10)") @RequestParam(defaultValue = "10") int count) {

        if (count < 1 || count > 1000) {
            return ResponseEntity.badRequest().build();
        }

        List<RawSensorDataDto> data = realtimeDataGeneratorService.generateRawSensorData(count);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/datalake/generate/stream")
    @Operation(summary = "Datalake용 스트리밍 데이터 생성",
            description = "Datalake 연동을 위한 스트리밍용 데이터를 생성합니다. 기본값은 5개입니다.")
    public ResponseEntity<List<RawSensorDataDto>> generateDatalakeStreamData(@Parameter(
            description = "생성할 데이터 개수 (기본값: 5)") @RequestParam(defaultValue = "5") int count) {

        if (count < 1 || count > 100) {
            return ResponseEntity.badRequest().build();
        }

        List<RawSensorDataDto> data = realtimeDataGeneratorService.generateRawSensorData(count);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/datalake/generate/batch")
    @Operation(summary = "Datalake용 배치 데이터 생성",
            description = "Datalake 연동을 위한 배치용 데이터를 생성합니다. 기본값은 100개입니다.")
    public ResponseEntity<List<RawSensorDataDto>> generateDatalakeBatchData(@Parameter(
            description = "생성할 데이터 개수 (기본값: 100)") @RequestParam(defaultValue = "100") int count) {

        if (count < 1 || count > 1000) {
            return ResponseEntity.badRequest().build();
        }

        List<RawSensorDataDto> data = realtimeDataGeneratorService.generateRawSensorData(count);
        return ResponseEntity.ok(data);
    }

    @GetMapping("/info")
    @Operation(summary = "데이터 생성기 정보", description = "실시간 데이터 생성기의 설정 정보와 사용법을 제공합니다.")
    public ResponseEntity<String> getGeneratorInfo() {
        String info =
                """
                        실시간 데이터 생성기 정보
                        ========================

                        사용 가능한 엔드포인트:
                        - GET /mock/realtime-generator/generate : 기본 10개 데이터 생성 (Realtime 모델)
                        - GET /mock/realtime-generator/generate/{count} : 지정된 개수만큼 데이터 생성 (Realtime 모델)
                        - POST /mock/realtime-generator/generate : POST 요청으로 데이터 생성 (Realtime 모델)
                        - GET /mock/realtime-generator/generate/batch : 배치용 데이터 생성 (기본 100개, Realtime 모델)
                        - GET /mock/realtime-generator/generate/stream : 스트리밍용 데이터 생성 (기본 5개, Realtime 모델)
                        - GET /mock/realtime-generator/generate/health-check : 헬스체크용 데이터 생성 (1개, Realtime 모델)
                        - GET /mock/realtime-generator/generate/performance-test : 성능테스트용 데이터 생성 (기본 500개, Realtime 모델)

                        Datalake 전용 엔드포인트:
                        - GET /mock/realtime-generator/datalake/generate : Datalake용 기본 데이터 생성 (RawSensorData 모델)
                        - GET /mock/realtime-generator/datalake/generate/stream : Datalake용 스트리밍 데이터 생성 (RawSensorData 모델)
                        - GET /mock/realtime-generator/datalake/generate/batch : Datalake용 배치 데이터 생성 (RawSensorData 모델)

                        데이터 특성:
                        - 90% 정상 데이터: 온도(15-35°C), 습도(30-70%), 연기밀도(0.001-0.050), CO(0.001-0.030), 가스(0.001-0.040)
                        - 10% 이상 데이터: 다양한 이상 상황 시뮬레이션 (고온, 고습도, 연기, CO, 가스, 복합 이상 등)

                        Datalake 연동 권장사항:
                        - 정기적인 데이터 수집: /datalake/generate/stream (5개씩, 1-5분 간격)
                        - 배치 처리: /datalake/generate/batch (100개씩, 10-30분 간격)
                        - 기본 생성: /datalake/generate (10개씩, 필요시)
                        """;

        return ResponseEntity.ok(info);
    }
}
