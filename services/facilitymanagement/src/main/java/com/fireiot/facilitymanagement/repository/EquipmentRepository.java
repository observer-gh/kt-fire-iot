package com.fireiot.facilitymanagement.repository;

import com.fireiot.facilitymanagement.entity.Equipment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface EquipmentRepository extends JpaRepository<Equipment, String> {

    /**
     * 장비 ID로 장비 조회
     */
    Optional<Equipment> findByEquipmentId(String equipmentId);

    /**
     * 시설 ID로 장비 목록 조회
     */
    List<Equipment> findByFacilityId(String facilityId);

    /**
     * 장비 상태 코드로 장비 목록 조회
     */
    List<Equipment> findByStatusCode(String statusCode);

    /**
     * 시설 ID와 장비 상태 코드로 장비 목록 조회
     */
    List<Equipment> findByFacilityIdAndStatusCode(String facilityId, String statusCode);

    /**
     * 만료일이 임박한 장비 목록 조회 (30일 이내)
     */
    @Query("SELECT e FROM Equipment e WHERE e.expiredAt IS NOT NULL AND e.expiredAt <= :expiryDate")
    List<Equipment> findExpiringEquipment(@Param("expiryDate") LocalDateTime expiryDate);

    /**
     * 장비 상태 업데이트
     */
    @Modifying
    @Query("UPDATE Equipment e SET e.statusCode = :statusCode, e.equipmentLocation = :location, e.expiredAt = :expiredAt, e.version = e.version + 1 WHERE e.equipmentId = :equipmentId")
    int updateEquipmentStatus(@Param("equipmentId") String equipmentId,
            @Param("statusCode") String statusCode, @Param("location") String location,
            @Param("expiredAt") LocalDateTime expiredAt);

    /**
     * 장비 위치 업데이트
     */
    @Modifying
    @Query("UPDATE Equipment e SET e.equipmentLocation = :location, e.version = e.version + 1 WHERE e.equipmentId = :equipmentId")
    int updateEquipmentLocation(@Param("equipmentId") String equipmentId,
            @Param("location") String location);

    /**
     * 장비 만료일 업데이트
     */
    @Modifying
    @Query("UPDATE Equipment e SET e.expiredAt = :expiredAt, e.version = e.version + 1 WHERE e.equipmentId = :equipmentId")
    int updateEquipmentExpiry(@Param("equipmentId") String equipmentId,
            @Param("expiredAt") LocalDateTime expiredAt);
}
