package com.fireiot.mockserver.repository;

import com.fireiot.mockserver.model.Equipment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface EquipmentRepository extends JpaRepository<Equipment, String> {

    List<Equipment> findByFacilityId(String facilityId);

    List<Equipment> findByEquipmentType(String equipmentType);

    List<Equipment> findByStatusCode(String statusCode);

    List<Equipment> findByEquipmentLocation(String equipmentLocation);

    List<Equipment> findByInstalledAtBetween(LocalDateTime startDate, LocalDateTime endDate);

    List<Equipment> findByExpiredAtBefore(LocalDateTime date);

    @Query("SELECT e FROM Equipment e WHERE e.facilityId = :facilityId AND e.equipmentType = :equipmentType")
    List<Equipment> findByFacilityIdAndEquipmentType(@Param("facilityId") String facilityId, @Param("equipmentType") String equipmentType);

    @Query("SELECT e FROM Equipment e WHERE e.installedAt >= :startDate AND e.installedAt <= :endDate")
    List<Equipment> findEquipmentInstalledInPeriod(@Param("startDate") LocalDateTime startDate, @Param("endDate") LocalDateTime endDate);

    @Query("SELECT e FROM Equipment e WHERE e.expiredAt <= :expiryDate")
    List<Equipment> findExpiringEquipment(@Param("expiryDate") LocalDateTime expiryDate);
}
