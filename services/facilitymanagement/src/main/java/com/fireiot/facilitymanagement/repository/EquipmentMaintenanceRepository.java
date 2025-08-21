package com.fireiot.facilitymanagement.repository;

import com.fireiot.facilitymanagement.entity.EquipmentMaintenance;
import com.fireiot.facilitymanagement.enums.MaintenanceType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface EquipmentMaintenanceRepository
                extends JpaRepository<EquipmentMaintenance, String> {

        // 장비별 유지보수 기록 조회
        List<EquipmentMaintenance> findByEquipmentId(String equipmentId);

        // 시설별 유지보수 기록 조회
        List<EquipmentMaintenance> findByFacilityId(String facilityId);

        // 유지보수 타입별 조회
        List<EquipmentMaintenance> findByMaintenanceType(MaintenanceType maintenanceType);

        // 상태별 유지보수 기록 조회
        List<EquipmentMaintenance> findByStatusCode(String statusCode);

        // 예정된 유지보수 조회
        List<EquipmentMaintenance> findByScheduledDateBetween(LocalDateTime startDate,
                        LocalDateTime endDate);

        // 수행된 유지보수 조회
        List<EquipmentMaintenance> findByPerformedDateBetween(LocalDateTime startDate,
                        LocalDateTime endDate);

        // 담당자별 유지보수 기록 조회
        List<EquipmentMaintenance> findByManager(String manager);

        // 장비 및 시설별 유지보수 기록 조회
        List<EquipmentMaintenance> findByEquipmentIdAndFacilityId(String equipmentId,
                        String facilityId);

        // 예정일이 지난 미수행 유지보수 조회
        @Query("SELECT em FROM EquipmentMaintenance em WHERE em.scheduledDate < :currentDate AND em.performedDate IS NULL")
        List<EquipmentMaintenance> findOverdueMaintenance(
                        @Param("currentDate") LocalDateTime currentDate);

        // 다음 예정 유지보수 조회
        @Query("SELECT em FROM EquipmentMaintenance em WHERE em.equipmentId = :equipmentId AND em.nextScheduledDate >= :currentDate ORDER BY em.nextScheduledDate ASC")
        List<EquipmentMaintenance> findNextScheduledMaintenance(
                        @Param("equipmentId") String equipmentId,
                        @Param("currentDate") LocalDateTime currentDate);

        // 복합 검색 쿼리
        @Query("SELECT em FROM EquipmentMaintenance em WHERE "
                        + "(:equipmentId IS NULL OR em.equipmentId = :equipmentId) AND "
                        + "(:facilityId IS NULL OR em.facilityId = :facilityId) AND "
                        + "(:maintenanceType IS NULL OR em.maintenanceType = :maintenanceType) AND "
                        + "(:statusCode IS NULL OR em.statusCode = :statusCode) AND "
                        + "(:manager IS NULL OR em.manager = :manager)")
        List<EquipmentMaintenance> findMaintenanceByCriteria(
                        @Param("equipmentId") String equipmentId,
                        @Param("facilityId") String facilityId,
                        @Param("maintenanceType") MaintenanceType maintenanceType,
                        @Param("statusCode") String statusCode, @Param("manager") String manager);

        // 시설별 유지보수 통계
        @Query("SELECT em.facilityId, COUNT(em), em.statusCode FROM EquipmentMaintenance em GROUP BY em.facilityId, em.statusCode")
        List<Object[]> getMaintenanceStatisticsByFacility();

        // 장비별 유지보수 이력 수 조회
        @Query("SELECT COUNT(em) FROM EquipmentMaintenance em WHERE em.equipmentId = :equipmentId")
        long countByEquipmentId(@Param("equipmentId") String equipmentId);
}
