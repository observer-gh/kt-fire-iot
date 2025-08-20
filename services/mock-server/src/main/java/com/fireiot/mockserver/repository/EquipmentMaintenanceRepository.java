package com.fireiot.mockserver.repository;

import com.fireiot.mockserver.model.EquipmentMaintenance;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface EquipmentMaintenanceRepository extends JpaRepository<EquipmentMaintenance, String> {

    List<EquipmentMaintenance> findByEquipmentId(String equipmentId);

    List<EquipmentMaintenance> findByFacilityId(String facilityId);

    List<EquipmentMaintenance> findByEquipmentLocation(String equipmentLocation);

    List<EquipmentMaintenance> findByMaintenanceType(EquipmentMaintenance.MaintenanceType maintenanceType);

    List<EquipmentMaintenance> findByStatusCode(String statusCode);

    List<EquipmentMaintenance> findByManager(String manager);

    List<EquipmentMaintenance> findByScheduledDateBetween(LocalDateTime startDate, LocalDateTime endDate);

    List<EquipmentMaintenance> findByPerformedDateBetween(LocalDateTime startDate, LocalDateTime endDate);

    List<EquipmentMaintenance> findByNextScheduledDateBefore(LocalDateTime date);

    @Query("SELECT m FROM EquipmentMaintenance m WHERE m.equipmentId = :equipmentId AND m.statusCode = :statusCode")
    List<EquipmentMaintenance> findByEquipmentIdAndStatus(@Param("equipmentId") String equipmentId, @Param("statusCode") String statusCode);

    @Query("SELECT m FROM EquipmentMaintenance m WHERE m.scheduledDate >= :startDate AND m.scheduledDate <= :endDate AND m.statusCode = :statusCode")
    List<EquipmentMaintenance> findScheduledMaintenanceInPeriod(@Param("startDate") LocalDateTime startDate, @Param("endDate") LocalDateTime endDate, @Param("statusCode") String statusCode);

    @Query("SELECT m FROM EquipmentMaintenance m WHERE m.performedDate IS NULL AND m.scheduledDate <= :currentDate")
    List<EquipmentMaintenance> findOverdueMaintenance(@Param("currentDate") LocalDateTime currentDate);
}
