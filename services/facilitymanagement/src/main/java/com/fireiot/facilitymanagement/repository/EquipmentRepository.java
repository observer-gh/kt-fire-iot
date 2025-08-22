package com.fireiot.facilitymanagement.repository;

import com.fireiot.facilitymanagement.entity.Equipment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface EquipmentRepository extends JpaRepository<Equipment, String> {

        // 시설별 장비 조회
        List<Equipment> findByFacilityId(String facilityId);

        // 장비 타입별 조회
        List<Equipment> findByEquipmentType(String equipmentType);

        // 상태별 장비 조회
        List<Equipment> findByStatusCode(String statusCode);

        // 만료 예정 장비 조회
        List<Equipment> findByExpiredAtBefore(LocalDateTime date);

        // 위치별 장비 조회
        List<Equipment> findByEquipmentLocation(String equipmentLocation);

        // 시설 및 상태별 장비 조회
        List<Equipment> findByFacilityIdAndStatusCode(String facilityId, String statusCode);

        // 설치일 기준 조회
        List<Equipment> findByInstalledAtBetween(LocalDateTime startDate, LocalDateTime endDate);

        // 복합 검색 쿼리
        @Query("SELECT e FROM Equipment e WHERE "
                        + "(:facilityId IS NULL OR e.facilityId = :facilityId) AND "
                        + "(:equipmentType IS NULL OR e.equipmentType = :equipmentType) AND "
                        + "(:statusCode IS NULL OR e.statusCode = :statusCode) AND "
                        + "(:location IS NULL OR e.equipmentLocation = :location)")
        List<Equipment> findEquipmentByCriteria(@Param("facilityId") String facilityId,
                        @Param("equipmentType") String equipmentType,
                        @Param("statusCode") String statusCode, @Param("location") String location);

        // 시설별 장비 수 조회
        @Query("SELECT COUNT(e) FROM Equipment e WHERE e.facilityId = :facilityId")
        long countByFacilityId(@Param("facilityId") String facilityId);

        // 상태별 장비 수 조회
        @Query("SELECT e.statusCode, COUNT(e) FROM Equipment e GROUP BY e.statusCode")
        List<Object[]> countByStatusCode();

        // 만료 예정 장비 조회 (지정된 날짜 이전에 만료되는 장비)
        @Query("SELECT e FROM Equipment e WHERE e.expiredAt IS NOT NULL AND e.expiredAt <= :expiryDate")
        List<Equipment> findExpiringEquipment(@Param("expiryDate") LocalDateTime expiryDate);
}
