package com.fireiot.mockserver.service;

import com.fireiot.mockserver.dto.RawSensorDataDto;
import com.fireiot.mockserver.model.Realtime;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.UUID;

@Service
public class RealtimeDataGeneratorService {

  private final Random random = new Random();

  // 정상 데이터 범위
  private static final BigDecimal NORMAL_TEMP_MIN = new BigDecimal("15.0");
  private static final BigDecimal NORMAL_TEMP_MAX = new BigDecimal("35.0");
  private static final BigDecimal NORMAL_HUMIDITY_MIN = new BigDecimal("30.0");
  private static final BigDecimal NORMAL_HUMIDITY_MAX = new BigDecimal("70.0");
  private static final BigDecimal NORMAL_SMOKE_MIN = new BigDecimal("0.001");
  private static final BigDecimal NORMAL_SMOKE_MAX = new BigDecimal("0.050");
  private static final BigDecimal NORMAL_CO_MIN = new BigDecimal("0.001");
  private static final BigDecimal NORMAL_CO_MAX = new BigDecimal("0.030");
  private static final BigDecimal NORMAL_GAS_MIN = new BigDecimal("0.001");
  private static final BigDecimal NORMAL_GAS_MAX = new BigDecimal("0.040");

  // 이상 데이터 범위
  private static final BigDecimal ABNORMAL_TEMP_MIN = new BigDecimal("80.0");
  private static final BigDecimal ABNORMAL_TEMP_MAX = new BigDecimal("120.0");
  private static final BigDecimal ABNORMAL_HUMIDITY_MIN = new BigDecimal("95.0");
  private static final BigDecimal ABNORMAL_HUMIDITY_MAX = new BigDecimal("100.0");
  private static final BigDecimal ABNORMAL_SMOKE_MIN = new BigDecimal("0.200");
  private static final BigDecimal ABNORMAL_SMOKE_MAX = new BigDecimal("1.000");
  private static final BigDecimal ABNORMAL_CO_MIN = new BigDecimal("0.100");
  private static final BigDecimal ABNORMAL_CO_MAX = new BigDecimal("0.500");
  private static final BigDecimal ABNORMAL_GAS_MIN = new BigDecimal("0.150");
  private static final BigDecimal ABNORMAL_GAS_MAX = new BigDecimal("0.800");

  // 장비 및 시설 정보
  private static final String[] EQUIPMENT_IDS =
      {"EQ001", "EQ002", "EQ003", "EQ004", "EQ005", "EQ006", "EQ007", "EQ008", "EQ009", "EQ010"};
  private static final String[] FACILITY_IDS = {"FC001", "FC002", "FC003", "FC004", "FC005"};
  private static final String[] LOCATIONS =
      {"1층_화재감지구역A", "1층_화재감지구역B", "2층_화재감지구역A", "2층_화재감지구역B", "지하1층_주차장"};

  /**
   * 지정된 개수만큼 실시간 데이터를 생성합니다. 90%는 정상 데이터, 10%는 이상 데이터를 생성합니다.
   */
  public List<Realtime> generateRealtimeData(int count) {
    List<Realtime> dataList = new ArrayList<>();

    for (int i = 0; i < count; i++) {
      // 90% 확률로 정상 데이터, 10% 확률로 이상 데이터 생성
      boolean isAbnormal = random.nextDouble() < 0.1;

      Realtime data = isAbnormal ? generateAbnormalData() : generateNormalData();
      dataList.add(data);
    }

    return dataList;
  }

  /**
   * Datalake용 RawSensorDataDto를 생성합니다. 90%는 정상 데이터, 10%는 이상 데이터를 생성합니다.
   */
  public List<RawSensorDataDto> generateRawSensorData(int count) {
    List<RawSensorDataDto> dataList = new ArrayList<>();

    for (int i = 0; i < count; i++) {
      // 90% 확률로 정상 데이터, 10% 확률로 이상 데이터 생성
      boolean isAbnormal = random.nextDouble() < 0.1;

      RawSensorDataDto data =
          isAbnormal ? generateAbnormalRawSensorData() : generateNormalRawSensorData();
      dataList.add(data);
    }

    return dataList;
  }

  /**
   * 정상 범위 내의 데이터를 생성합니다.
   */
  private Realtime generateNormalData() {
    Realtime data = new Realtime();
    data.setEquipmentDataId(generateEquipmentDataId());
    data.setEquipmentId(getRandomElement(EQUIPMENT_IDS));
    data.setFacilityId(getRandomElement(FACILITY_IDS));
    data.setEquipmentLocation(getRandomElement(LOCATIONS));
    data.setMeasuredAt(LocalDateTime.now().minusSeconds(random.nextInt(300))); // 최근 5분 내
    data.setIngestedAt(LocalDateTime.now());
    data.setTemperature(generateRandomBigDecimal(NORMAL_TEMP_MIN, NORMAL_TEMP_MAX, 2));
    data.setHumidity(generateRandomBigDecimal(NORMAL_HUMIDITY_MIN, NORMAL_HUMIDITY_MAX, 2));
    data.setSmokeDensity(generateRandomBigDecimal(NORMAL_SMOKE_MIN, NORMAL_SMOKE_MAX, 3));
    data.setCoLevel(generateRandomBigDecimal(NORMAL_CO_MIN, NORMAL_CO_MAX, 3));
    data.setGasLevel(generateRandomBigDecimal(NORMAL_GAS_MIN, NORMAL_GAS_MAX, 3));
    data.setVersion(1);

    return data;
  }

  /**
   * 다양한 이상 데이터를 생성합니다.
   */
  private Realtime generateAbnormalData() {
    Realtime data = new Realtime();
    data.setEquipmentDataId(generateEquipmentDataId());
    data.setEquipmentId(getRandomElement(EQUIPMENT_IDS));
    data.setFacilityId(getRandomElement(FACILITY_IDS));
    data.setEquipmentLocation(getRandomElement(LOCATIONS));
    data.setMeasuredAt(LocalDateTime.now().minusSeconds(random.nextInt(300)));
    data.setIngestedAt(LocalDateTime.now());
    data.setVersion(1);

    // 다양한 이상 상황을 시뮬레이션
    int anomalyType = random.nextInt(8);

    switch (anomalyType) {
      case 0: // 고온 이상
        data.setTemperature(generateRandomBigDecimal(ABNORMAL_TEMP_MIN, ABNORMAL_TEMP_MAX, 2));
        data.setHumidity(generateRandomBigDecimal(NORMAL_HUMIDITY_MIN, NORMAL_HUMIDITY_MAX, 2));
        data.setSmokeDensity(generateRandomBigDecimal(NORMAL_SMOKE_MIN, NORMAL_SMOKE_MAX, 3));
        data.setCoLevel(generateRandomBigDecimal(NORMAL_CO_MIN, NORMAL_CO_MAX, 3));
        data.setGasLevel(generateRandomBigDecimal(NORMAL_GAS_MIN, NORMAL_GAS_MAX, 3));
        break;

      case 1: // 고습도 이상
        data.setTemperature(generateRandomBigDecimal(NORMAL_TEMP_MIN, NORMAL_TEMP_MAX, 2));
        data.setHumidity(generateRandomBigDecimal(ABNORMAL_HUMIDITY_MIN, ABNORMAL_HUMIDITY_MAX, 2));
        data.setSmokeDensity(generateRandomBigDecimal(NORMAL_SMOKE_MIN, NORMAL_SMOKE_MAX, 3));
        data.setCoLevel(generateRandomBigDecimal(NORMAL_CO_MIN, NORMAL_CO_MAX, 3));
        data.setGasLevel(generateRandomBigDecimal(NORMAL_GAS_MIN, NORMAL_GAS_MAX, 3));
        break;

      case 2: // 연기 밀도 이상
        data.setTemperature(generateRandomBigDecimal(NORMAL_TEMP_MIN, NORMAL_TEMP_MAX, 2));
        data.setHumidity(generateRandomBigDecimal(NORMAL_HUMIDITY_MIN, NORMAL_HUMIDITY_MAX, 2));
        data.setSmokeDensity(generateRandomBigDecimal(ABNORMAL_SMOKE_MIN, ABNORMAL_SMOKE_MAX, 3));
        data.setCoLevel(generateRandomBigDecimal(NORMAL_CO_MIN, NORMAL_CO_MAX, 3));
        data.setGasLevel(generateRandomBigDecimal(NORMAL_GAS_MIN, NORMAL_GAS_MAX, 3));
        break;

      case 3: // CO 레벨 이상
        data.setTemperature(generateRandomBigDecimal(NORMAL_TEMP_MIN, NORMAL_TEMP_MAX, 2));
        data.setHumidity(generateRandomBigDecimal(NORMAL_HUMIDITY_MIN, NORMAL_HUMIDITY_MAX, 2));
        data.setSmokeDensity(generateRandomBigDecimal(NORMAL_SMOKE_MIN, NORMAL_SMOKE_MAX, 3));
        data.setCoLevel(generateRandomBigDecimal(ABNORMAL_CO_MIN, ABNORMAL_CO_MAX, 3));
        data.setGasLevel(generateRandomBigDecimal(NORMAL_GAS_MIN, NORMAL_GAS_MAX, 3));
        break;

      case 4: // 가스 레벨 이상
        data.setTemperature(generateRandomBigDecimal(NORMAL_TEMP_MIN, NORMAL_TEMP_MAX, 2));
        data.setHumidity(generateRandomBigDecimal(NORMAL_HUMIDITY_MIN, NORMAL_HUMIDITY_MAX, 2));
        data.setSmokeDensity(generateRandomBigDecimal(NORMAL_SMOKE_MIN, NORMAL_SMOKE_MAX, 3));
        data.setCoLevel(generateRandomBigDecimal(NORMAL_CO_MIN, NORMAL_CO_MAX, 3));
        data.setGasLevel(generateRandomBigDecimal(ABNORMAL_GAS_MIN, ABNORMAL_GAS_MAX, 3));
        break;

      case 5: // 복합 이상 (온도 + 연기)
        data.setTemperature(generateRandomBigDecimal(ABNORMAL_TEMP_MIN, ABNORMAL_TEMP_MAX, 2));
        data.setHumidity(generateRandomBigDecimal(NORMAL_HUMIDITY_MIN, NORMAL_HUMIDITY_MAX, 2));
        data.setSmokeDensity(generateRandomBigDecimal(ABNORMAL_SMOKE_MIN, ABNORMAL_SMOKE_MAX, 3));
        data.setCoLevel(generateRandomBigDecimal(NORMAL_CO_MIN, NORMAL_CO_MAX, 3));
        data.setGasLevel(generateRandomBigDecimal(NORMAL_GAS_MIN, NORMAL_GAS_MAX, 3));
        break;

      case 6: // 복합 이상 (CO + 가스)
        data.setTemperature(generateRandomBigDecimal(NORMAL_TEMP_MIN, NORMAL_TEMP_MAX, 2));
        data.setHumidity(generateRandomBigDecimal(NORMAL_HUMIDITY_MIN, NORMAL_HUMIDITY_MAX, 2));
        data.setSmokeDensity(generateRandomBigDecimal(NORMAL_SMOKE_MIN, NORMAL_SMOKE_MAX, 3));
        data.setCoLevel(generateRandomBigDecimal(ABNORMAL_CO_MIN, ABNORMAL_CO_MAX, 3));
        data.setGasLevel(generateRandomBigDecimal(ABNORMAL_GAS_MIN, ABNORMAL_GAS_MAX, 3));
        break;

      case 7: // 극한 이상 (모든 값이 위험 수준)
        data.setTemperature(generateRandomBigDecimal(ABNORMAL_TEMP_MIN, ABNORMAL_TEMP_MAX, 2));
        data.setHumidity(generateRandomBigDecimal(ABNORMAL_HUMIDITY_MIN, ABNORMAL_HUMIDITY_MAX, 2));
        data.setSmokeDensity(generateRandomBigDecimal(ABNORMAL_SMOKE_MIN, ABNORMAL_SMOKE_MAX, 3));
        data.setCoLevel(generateRandomBigDecimal(ABNORMAL_CO_MIN, ABNORMAL_CO_MAX, 3));
        data.setGasLevel(generateRandomBigDecimal(ABNORMAL_GAS_MIN, ABNORMAL_GAS_MAX, 3));
        break;
    }

    return data;
  }

  /**
   * 지정된 범위 내의 랜덤 BigDecimal 값을 생성합니다.
   */
  private BigDecimal generateRandomBigDecimal(BigDecimal min, BigDecimal max, int scale) {
    double minValue = min.doubleValue();
    double maxValue = max.doubleValue();
    double randomValue = minValue + (maxValue - minValue) * random.nextDouble();
    return BigDecimal.valueOf(randomValue).setScale(scale, BigDecimal.ROUND_HALF_UP);
  }

  /**
   * 지정된 범위 내의 랜덤 Float 값을 생성합니다.
   */
  private Float generateRandomFloat(float min, float max) {
    return min + (max - min) * random.nextFloat();
  }

  /**
   * 정상 범위 내의 RawSensorDataDto를 생성합니다.
   */
  private RawSensorDataDto generateNormalRawSensorData() {
    RawSensorDataDto data = new RawSensorDataDto();
    data.setEquipmentId(getRandomElement(EQUIPMENT_IDS));
    data.setFacilityId(getRandomElement(FACILITY_IDS));
    data.setEquipmentLocation(getRandomElement(LOCATIONS));
    data.setMeasuredAt(LocalDateTime.now().minusSeconds(random.nextInt(300))); // 최근 5분 내
    data.setTemperature(generateRandomFloat(15.0f, 35.0f));
    data.setHumidity(generateRandomFloat(30.0f, 70.0f));
    data.setSmokeDensity(generateRandomFloat(0.001f, 0.050f));
    data.setCoLevel(generateRandomFloat(0.001f, 0.030f));
    data.setGasLevel(generateRandomFloat(0.001f, 0.040f));

    // metadata 추가
    Map<String, Object> metadata = new HashMap<>();
    metadata.put("source", "mock-server");
    metadata.put("data_type", "normal");
    metadata.put("generated_at", LocalDateTime.now().toString());
    data.setMetadata(metadata);

    return data;
  }

  /**
   * 다양한 이상 RawSensorDataDto를 생성합니다.
   */
  private RawSensorDataDto generateAbnormalRawSensorData() {
    RawSensorDataDto data = new RawSensorDataDto();
    data.setEquipmentId(getRandomElement(EQUIPMENT_IDS));
    data.setFacilityId(getRandomElement(FACILITY_IDS));
    data.setEquipmentLocation(getRandomElement(LOCATIONS));
    data.setMeasuredAt(LocalDateTime.now().minusSeconds(random.nextInt(300)));

    // 다양한 이상 상황을 시뮬레이션
    int anomalyType = random.nextInt(8);

    switch (anomalyType) {
      case 0: // 고온 이상
        data.setTemperature(generateRandomFloat(80.0f, 120.0f));
        data.setHumidity(generateRandomFloat(30.0f, 70.0f));
        data.setSmokeDensity(generateRandomFloat(0.001f, 0.050f));
        data.setCoLevel(generateRandomFloat(0.001f, 0.030f));
        data.setGasLevel(generateRandomFloat(0.001f, 0.040f));
        break;

      case 1: // 고습도 이상
        data.setTemperature(generateRandomFloat(15.0f, 35.0f));
        data.setHumidity(generateRandomFloat(95.0f, 100.0f));
        data.setSmokeDensity(generateRandomFloat(0.001f, 0.050f));
        data.setCoLevel(generateRandomFloat(0.001f, 0.030f));
        data.setGasLevel(generateRandomFloat(0.001f, 0.040f));
        break;

      case 2: // 연기 밀도 이상
        data.setTemperature(generateRandomFloat(15.0f, 35.0f));
        data.setHumidity(generateRandomFloat(30.0f, 70.0f));
        data.setSmokeDensity(generateRandomFloat(0.200f, 1.000f));
        data.setCoLevel(generateRandomFloat(0.001f, 0.030f));
        data.setGasLevel(generateRandomFloat(0.001f, 0.040f));
        break;

      case 3: // CO 레벨 이상
        data.setTemperature(generateRandomFloat(15.0f, 35.0f));
        data.setHumidity(generateRandomFloat(30.0f, 70.0f));
        data.setSmokeDensity(generateRandomFloat(0.001f, 0.050f));
        data.setCoLevel(generateRandomFloat(0.100f, 0.500f));
        data.setGasLevel(generateRandomFloat(0.001f, 0.040f));
        break;

      case 4: // 가스 레벨 이상
        data.setTemperature(generateRandomFloat(15.0f, 35.0f));
        data.setHumidity(generateRandomFloat(30.0f, 70.0f));
        data.setSmokeDensity(generateRandomFloat(0.001f, 0.050f));
        data.setCoLevel(generateRandomFloat(0.001f, 0.030f));
        data.setGasLevel(generateRandomFloat(0.150f, 0.800f));
        break;

      case 5: // 복합 이상 (온도 + 연기)
        data.setTemperature(generateRandomFloat(80.0f, 120.0f));
        data.setHumidity(generateRandomFloat(30.0f, 70.0f));
        data.setSmokeDensity(generateRandomFloat(0.200f, 1.000f));
        data.setCoLevel(generateRandomFloat(0.001f, 0.030f));
        data.setGasLevel(generateRandomFloat(0.001f, 0.040f));
        break;

      case 6: // 복합 이상 (CO + 가스)
        data.setTemperature(generateRandomFloat(15.0f, 35.0f));
        data.setHumidity(generateRandomFloat(30.0f, 70.0f));
        data.setSmokeDensity(generateRandomFloat(0.001f, 0.050f));
        data.setCoLevel(generateRandomFloat(0.100f, 0.500f));
        data.setGasLevel(generateRandomFloat(0.150f, 0.800f));
        break;

      case 7: // 극한 이상 (모든 값이 위험 수준)
        data.setTemperature(generateRandomFloat(80.0f, 120.0f));
        data.setHumidity(generateRandomFloat(95.0f, 100.0f));
        data.setSmokeDensity(generateRandomFloat(0.200f, 1.000f));
        data.setCoLevel(generateRandomFloat(0.100f, 0.500f));
        data.setGasLevel(generateRandomFloat(0.150f, 0.800f));
        break;
    }

    // metadata 추가
    Map<String, Object> metadata = new HashMap<>();
    metadata.put("source", "mock-server");
    metadata.put("data_type", "abnormal");
    metadata.put("anomaly_type", anomalyType);
    metadata.put("generated_at", LocalDateTime.now().toString());
    data.setMetadata(metadata);

    return data;
  }

  /**
   * 배열에서 랜덤 요소를 선택합니다.
   */
  private String getRandomElement(String[] array) {
    return array[random.nextInt(array.length)];
  }

  /**
   * 고유한 장비 데이터 ID를 생성합니다.
   */
  private String generateEquipmentDataId() {
    return "ED" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
  }
}
