package com.fireiot.mockserver.config;

import com.fireiot.mockserver.model.*;
import com.fireiot.mockserver.repository.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

@Component
public class DataInitializer implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(DataInitializer.class);

    @Autowired
    private FacilityRepository facilityRepository;

    @Autowired
    private EquipmentRepository equipmentRepository;

    @Autowired
    private IncidentRepository incidentRepository;

    @Autowired
    private EquipmentMaintenanceRepository equipmentMaintenanceRepository;

    @Autowired
    private RealtimeRepository realtimeRepository;

    @Autowired
    private AnalysisRepository analysisRepository;

    @Autowired
    private AlertRepository alertRepository;

    @Override
    public void run(String... args) throws Exception {
        logger.info("Starting data initialization...");

        // Clear existing data
        clearAllData();

        // Initialize data
        initializeFacilities();
        initializeEquipment();
        initializeIncidents();
        initializeEquipmentMaintenance();
        initializeRealtimeData();
        initializeAnalysis();
        initializeAlerts();

        logger.info("Data initialization completed successfully!");
    }

    private void clearAllData() {
        logger.info("Clearing existing data...");
        alertRepository.deleteAll();
        analysisRepository.deleteAll();
        realtimeRepository.deleteAll();
        equipmentMaintenanceRepository.deleteAll();
        incidentRepository.deleteAll();
        equipmentRepository.deleteAll();
        facilityRepository.deleteAll();
    }

    private void initializeFacilities() {
        logger.info("Initializing facilities...");

        List<Facility> facilities = Arrays.asList(
                createFacility("FAC001", "서울시 강남구 테헤란로", "A동1층", "공장", "김철수", "010-1234-5678",
                        "HIGH", 5, 15, 20, 1),
                createFacility("FAC002", "부산시 해운대구 해운대로", "B동2층", "창고", "이영희", "010-2345-6789",
                        "MEDIUM", 3, 12, 18, 1),
                createFacility("FAC003", "대구시 수성구 동대구로", "C동3층", "사무실", "박민수", "010-3456-7890",
                        "LOW", 2, 8, 12, 1),
                createFacility("FAC004", "인천시 연수구 송도대로", "D동1층", "연구소", "최지영", "010-4567-8901",
                        "MEDIUM", 4, 10, 15, 1),
                createFacility("FAC005", "광주시 서구 상무대로", "E동2층", "공장", "정수민", "010-5678-9012",
                        "HIGH", 6, 18, 25, 1));

        facilityRepository.saveAll(facilities);
        logger.info("Facilities initialized: {}", facilities.size());
    }

    private Facility createFacility(String id, String address, String internalAddress, String type,
            String managerName, String managerPhone, String riskLevel, int activeAlerts,
            int onlineSensors, int totalSensors, int version) {
        Facility facility = new Facility(id);
        facility.setAddress(address);
        facility.setInternalAddress(internalAddress);
        facility.setFacilityType(type);
        facility.setManagerName(managerName);
        facility.setManagerPhone(managerPhone);
        facility.setRiskLevel(riskLevel);
        facility.setActiveAlertsCount(activeAlerts);
        facility.setOnlineSensorsCount(onlineSensors);
        facility.setTotalSensorsCount(totalSensors);
        facility.setUpdatedAt(LocalDateTime.now());
        facility.setVersion(version);
        return facility;
    }

    private void initializeEquipment() {
        logger.info("Initializing equipment...");

        List<Equipment> equipment =
                Arrays.asList(createEquipment("EQ001", "FAC001", "센서패널", "ACTIVE", "SENSOR", 1),
                        createEquipment("EQ002", "FAC001", "화재감지기", "ACTIVE", "DETECTOR", 1),
                        createEquipment("EQ003", "FAC002", "온도센서", "ACTIVE", "SENSOR", 1),
                        createEquipment("EQ004", "FAC002", "가스감지기", "MAINT", "DETECTOR", 1),
                        createEquipment("EQ005", "FAC003", "습도센서", "ACTIVE", "SENSOR", 1),
                        createEquipment("EQ006", "FAC003", "연기감지기", "ACTIVE", "DETECTOR", 1),
                        createEquipment("EQ007", "FAC004", "압력센서", "ACTIVE", "SENSOR", 1),
                        createEquipment("EQ008", "FAC004", "열감지기", "ACTIVE", "DETECTOR", 1),
                        createEquipment("EQ009", "FAC005", "진동센서", "ACTIVE", "SENSOR", 1),
                        createEquipment("EQ010", "FAC005", "일산화탄소감지기", "ACTIVE", "DETECTOR", 1));

        equipmentRepository.saveAll(equipment);
        logger.info("Equipment initialized: {}", equipment.size());
    }

    private Equipment createEquipment(String id, String facilityId, String location,
            String statusCode, String type, int version) {
        Equipment equipment = new Equipment(id, facilityId);
        equipment.setEquipmentLocation(location);
        equipment.setStatusCode(statusCode);
        equipment.setEquipmentType(type);
        equipment.setCreatedAt(LocalDateTime.now());
        equipment.setInstalledAt(LocalDateTime.now().minusDays(30));
        equipment.setExpiredAt(LocalDateTime.now().plusYears(5));
        equipment.setVersion(version);
        return equipment;
    }

    private void initializeIncidents() {
        logger.info("Initializing incidents...");

        List<Incident> incidents = Arrays.asList(createIncident("INC001", "FAC001", "화재",
                Incident.IncidentSeverity.EMERGENCY, "화재보고서.pdf",
                "전기단락으로 인한 화재 발생. 전기배선의 노후화와 과부하가 주요 원인으로 분석됨. 즉시 전원 차단 및 소화기로 진화 완료. 재발 방지를 위한 전기배선 교체 작업 진행 예정.",
                1),
                createIncident("INC002", "FAC002", "가스누출", Incident.IncidentSeverity.WARN,
                        "가스누출보고서.pdf",
                        "가스배관 이음새에서 미세한 누출 발견. 누출량은 안전 기준 이하이나 지속적인 모니터링 필요. 배관 이음새 재조정 및 누출 검사 완료.",
                        1),
                createIncident("INC003", "FAC003", "장비고장", Incident.IncidentSeverity.INFO,
                        "장비고장보고서.pdf",
                        "센서 패널 일부 기능 이상. 온도 측정 센서의 정확도 저하 및 통신 지연 현상 발생. 센서 교체 및 펌웨어 업데이트로 문제 해결.",
                        1),
                createIncident("INC004", "FAC004", "온도이상", Incident.IncidentSeverity.WARN,
                        "온도이상보고서.pdf",
                        "실내 온도가 정상 범위를 초과. 냉각 시스템의 효율성 저하 및 외부 온도 상승이 주요 원인. 냉각 시스템 점검 및 필터 교체 완료.",
                        1),
                createIncident("INC005", "FAC005", "통신장애", Incident.IncidentSeverity.INFO,
                        "통신장애보고서.pdf",
                        "센서와 중앙 시스템 간 통신 불안정. 네트워크 신호 간섭 및 통신 프로토콜 호환성 문제로 인한 일시적 통신 중단. 네트워크 설정 최적화로 문제 해결.",
                        1));

        incidentRepository.saveAll(incidents);
        logger.info("Incidents initialized: {}", incidents.size());
    }

    private Incident createIncident(String id, String facilityId, String type,
            Incident.IncidentSeverity severity, String reportFileName, String description,
            int version) {
        Incident incident = new Incident(id, facilityId);
        incident.setIncidentType(type);
        incident.setSeverity(severity);
        incident.setCreatedAt(LocalDateTime.now().minusDays(5));
        incident.setResolvedAt(LocalDateTime.now().minusDays(2));
        incident.setReportFileName(reportFileName);
        incident.setDescription(description);
        incident.setVersion(version);
        return incident;
    }

    private void initializeEquipmentMaintenance() {
        logger.info("Initializing equipment maintenance...");

        List<EquipmentMaintenance> maintenance = Arrays.asList(
                createMaintenance("MAINT001", "EQ001", "FAC001", "센서패널",
                        EquipmentMaintenance.MaintenanceType.INSPECTION, "COMPLETED", "김기술", 1),
                createMaintenance("MAINT002", "EQ002", "FAC001", "화재감지기",
                        EquipmentMaintenance.MaintenanceType.REPAIR, "IN_PROG", "이기술", 1),
                createMaintenance("MAINT003", "EQ003", "FAC002", "온도센서",
                        EquipmentMaintenance.MaintenanceType.CALIBRATE, "SCHEDULED", "박기술", 1),
                createMaintenance("MAINT004", "EQ004", "FAC002", "가스감지기",
                        EquipmentMaintenance.MaintenanceType.REPLACE, "COMPLETED", "최기술", 1),
                createMaintenance("MAINT005", "EQ005", "FAC003", "습도센서",
                        EquipmentMaintenance.MaintenanceType.CLEAN, "SCHEDULED", "정기술", 1));

        equipmentMaintenanceRepository.saveAll(maintenance);
        logger.info("Equipment maintenance initialized: {}", maintenance.size());
    }

    private EquipmentMaintenance createMaintenance(String id, String equipmentId, String facilityId,
            String location, EquipmentMaintenance.MaintenanceType type, String statusCode,
            String manager, int version) {
        EquipmentMaintenance maintenance = new EquipmentMaintenance(id, equipmentId);
        maintenance.setFacilityId(facilityId);
        maintenance.setEquipmentLocation(location);
        maintenance.setMaintenanceType(type);
        maintenance.setScheduledDate(LocalDateTime.now().plusDays(7));
        maintenance.setPerformedDate(LocalDateTime.now().minusDays(2));
        maintenance.setManager(manager);
        maintenance.setStatusCode(statusCode);
        maintenance.setNextScheduledDate(LocalDateTime.now().plusMonths(6));
        maintenance.setNote(
                "정기 유지보수 작업 수행. 장비 상태 점검 및 성능 최적화를 위한 표준 프로세스에 따라 진행됨. 모든 안전 기준을 준수하며 작업 완료.");
        maintenance.setCreatedAt(LocalDateTime.now().minusDays(10));
        maintenance.setUpdatedAt(LocalDateTime.now());
        maintenance.setVersion(version);
        return maintenance;
    }

    private void initializeRealtimeData() {
        logger.info("Initializing realtime data...");

        List<Realtime> realtimeData = Arrays.asList(
                createRealtimeData("RT001", "EQ001", "FAC001", "센서패널", new BigDecimal("23.50"),
                        new BigDecimal("45.20"), new BigDecimal("0.001"), new BigDecimal("0.002"),
                        new BigDecimal("0.003"), 1),
                createRealtimeData("RT002", "EQ002", "FAC001", "화재감지기", new BigDecimal("24.10"),
                        new BigDecimal("46.80"), new BigDecimal("0.002"), new BigDecimal("0.001"),
                        new BigDecimal("0.004"), 1),
                createRealtimeData("RT003", "EQ003", "FAC002", "온도센서", new BigDecimal("22.80"),
                        new BigDecimal("44.50"), new BigDecimal("0.001"), new BigDecimal("0.003"),
                        new BigDecimal("0.002"), 1),
                createRealtimeData("RT004", "EQ004", "FAC002", "가스감지기", new BigDecimal("25.30"),
                        new BigDecimal("47.10"), new BigDecimal("0.003"), new BigDecimal("0.004"),
                        new BigDecimal("0.005"), 1),
                createRealtimeData("RT005", "EQ005", "FAC003", "습도센서", new BigDecimal("21.90"),
                        new BigDecimal("43.70"), new BigDecimal("0.001"), new BigDecimal("0.002"),
                        new BigDecimal("0.001"), 1));

        realtimeRepository.saveAll(realtimeData);
        logger.info("Realtime data initialized: {}", realtimeData.size());
    }

    private Realtime createRealtimeData(String id, String equipmentId, String facilityId,
            String location, BigDecimal temperature, BigDecimal humidity, BigDecimal smokeDensity,
            BigDecimal coLevel, BigDecimal gasLevel, int version) {
        Realtime realtime = new Realtime(id);
        realtime.setEquipmentId(equipmentId);
        realtime.setFacilityId(facilityId);
        realtime.setEquipmentLocation(location);
        realtime.setMeasuredAt(LocalDateTime.now().minusMinutes(5));
        realtime.setIngestedAt(LocalDateTime.now().minusMinutes(4));
        realtime.setTemperature(temperature);
        realtime.setHumidity(humidity);
        realtime.setSmokeDensity(smokeDensity);
        realtime.setCoLevel(coLevel);
        realtime.setGasLevel(gasLevel);
        realtime.setVersion(version);
        return realtime;
    }

    private void initializeAnalysis() {
        logger.info("Initializing analysis...");

        List<Analysis> analyses = Arrays.asList(
                createAnalysis("ANAL001", "FAC001", "INC001", "화재위험분석", new BigDecimal("0.9500"),
                        new BigDecimal("0.8500"), "COMPLETED", 1),
                createAnalysis("ANAL002", "FAC002", "INC002", "가스누출분석", new BigDecimal("0.8700"),
                        new BigDecimal("0.7200"), "IN_PROG", 1),
                createAnalysis("ANAL003", "FAC003", "INC003", "장비상태분석", new BigDecimal("0.9200"),
                        new BigDecimal("0.6800"), "COMPLETED", 1),
                createAnalysis("ANAL004", "FAC004", "INC004", "온도패턴분석", new BigDecimal("0.8900"),
                        new BigDecimal("0.7500"), "SCHEDULED", 1),
                createAnalysis("ANAL005", "FAC005", "INC005", "통신품질분석", new BigDecimal("0.9400"),
                        new BigDecimal("0.8100"), "COMPLETED", 1));

        analysisRepository.saveAll(analyses);
        logger.info("Analysis initialized: {}", analyses.size());
    }

    private Analysis createAnalysis(String id, String facilityId, String incidentId, String type,
            BigDecimal confidenceScore, BigDecimal riskProbability, String status, int version) {
        Analysis analysis = new Analysis(id, facilityId);
        analysis.setIncidentId(incidentId);
        analysis.setAnalysisType(type);
        analysis.setConfidenceScore(confidenceScore);
        analysis.setRiskProbability(riskProbability);
        analysis.setStatus(status);
        analysis.setCreatedAt(LocalDateTime.now().minusDays(3));
        analysis.setUpdatedAt(LocalDateTime.now().minusDays(1));
        analysis.setReportFileName("분석보고서" + id + ".pdf");
        analysis.setVersion(version);
        return analysis;
    }

    private void initializeAlerts() {
        logger.info("Initializing alerts...");

        List<Alert> alerts = Arrays.asList(
                createAlert("ALT001", "EQ001", "FAC001", "센서패널", Alert.AlertType.SMOKE,
                        Alert.AlertSeverity.WARN, "ACTIVE", 1),
                createAlert("ALT002", "EQ002", "FAC001", "화재감지기", Alert.AlertType.HEAT,
                        Alert.AlertSeverity.EMERGENCY, "ACTIVE", 1),
                createAlert("ALT003", "EQ003", "FAC002", "온도센서", Alert.AlertType.HEAT,
                        Alert.AlertSeverity.INFO, "RESOLVED", 1),
                createAlert("ALT004", "EQ004", "FAC002", "가스감지기", Alert.AlertType.GAS,
                        Alert.AlertSeverity.WARN, "ACTIVE", 1),
                createAlert("ALT005", "EQ005", "FAC003", "습도센서", Alert.AlertType.CUSTOM,
                        Alert.AlertSeverity.INFO, "RESOLVED", 1));

        alertRepository.saveAll(alerts);
        logger.info("Alerts initialized: {}", alerts.size());
    }

    private Alert createAlert(String id, String equipmentId, String facilityId, String location,
            Alert.AlertType type, Alert.AlertSeverity severity, String status, int version) {
        Alert alert = new Alert(id);
        alert.setEquipmentId(equipmentId);
        alert.setFacilityId(facilityId);
        alert.setEquipmentLocation(location);
        alert.setAlertType(type);
        alert.setSeverity(severity);
        alert.setStatus(status);
        alert.setCreatedAt(LocalDateTime.now().minusHours(2));
        alert.setUpdatedAt(LocalDateTime.now().minusMinutes(30));
        if ("RESOLVED".equals(status)) {
            alert.setResolvedAt(LocalDateTime.now().minusMinutes(15));
        }
        alert.setVersion(version);
        return alert;
    }
}
