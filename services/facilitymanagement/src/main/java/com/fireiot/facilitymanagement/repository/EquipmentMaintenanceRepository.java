package com.fireiot.facilitymanagement.repository;

import com.fireiot.facilitymanagement.entity.EquipmentMaintenance;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import com.fireiot.facilitymanagement.enums.MaintenanceType;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface EquipmentMaintenanceRepository
        extends JpaRepository<EquipmentMaintenance, String> {

    /**
     * 장비 ID로 유지보수 기록 조회
     */
    List<EquipmentMaintenance> findByEquipmentId(String equipmentId);

    /**
     * 시설 ID로 유지보수 기록 조회
     */
    List<EquipmentMaintenance> findByFacilityId(String facilityId);

    /**
     * 상태 코드로 유지보수 기록 조회
     */
    List<EquipmentMaintenance> findByStatusCode(String statusCode);

    /**
     * 장비 ID와 상태 코드로 유지보수 기록 조회
     */
    List<EquipmentMaintenance> findByEquipmentIdAndStatusCode(String equipmentId,
            String statusCode);

    /**
     * 예정된 날짜 범위로 유지보수 기록 조회
     */
    List<EquipmentMaintenance> findByScheduledDateBetween(LocalDateTime startDate,
            LocalDateTime endDate);

    /**
     * 특정 날짜 이후에 예정된 유지보수 기록 조회
     */
    List<EquipmentMaintenance> findByScheduledDateAfter(LocalDateTime date);

    /**
     * 유지보수 타입으로 유지보수 기록 조회
     */
    List<EquipmentMaintenance> findByMaintenanceType(MaintenanceType maintenanceType);

    /**
     * 담당자로 유지보수 기록 조회
     */
    List<EquipmentMaintenance> findByManager(String manager);
}
