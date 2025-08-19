package com.fireiot.mockserver.repository;

import com.fireiot.mockserver.model.Facility;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface FacilityRepository extends JpaRepository<Facility, String> {

    List<Facility> findByFacilityType(String facilityType);

    List<Facility> findByRiskLevel(String riskLevel);

    List<Facility> findByManagerName(String managerName);

    List<Facility> findByActiveAlertsCountGreaterThan(Integer minCount);

    List<Facility> findByOnlineSensorsCountGreaterThan(Integer minCount);

    @Query("SELECT f FROM Facility f WHERE f.address LIKE %:address%")
    List<Facility> findByAddressContaining(@Param("address") String address);
}
