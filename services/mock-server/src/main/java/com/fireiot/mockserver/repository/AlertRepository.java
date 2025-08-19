package com.fireiot.mockserver.repository;

import com.fireiot.mockserver.model.Alert;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AlertRepository extends JpaRepository<Alert, String> {

    List<Alert> findByEquipmentId(String equipmentId);

    List<Alert> findByFacilityId(String facilityId);

    List<Alert> findByEquipmentLocation(String equipmentLocation);

    List<Alert> findByAlertType(Alert.AlertType alertType);

    List<Alert> findBySeverity(Alert.AlertSeverity severity);

    List<Alert> findByStatus(String status);

    List<Alert> findByResolvedAtIsNull();

    @Query("SELECT a FROM Alert a WHERE a.equipmentLocation LIKE %:location%")
    List<Alert> findByLocationContaining(@Param("location") String location);
}
