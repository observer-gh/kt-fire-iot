package com.fireiot.mockserver.repository;

import com.fireiot.mockserver.model.Incident;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface IncidentRepository extends JpaRepository<Incident, String> {

    List<Incident> findByFacilityId(String facilityId);

    List<Incident> findByIncidentType(String incidentType);

    List<Incident> findBySeverity(Incident.IncidentSeverity severity);

    List<Incident> findByCreatedAtBetween(LocalDateTime startDate, LocalDateTime endDate);

    List<Incident> findByResolvedAtIsNull();

    @Query("SELECT i FROM Incident i WHERE i.createdAt >= :startDate AND i.createdAt <= :endDate")
    List<Incident> findIncidentsInPeriod(@Param("startDate") LocalDateTime startDate, @Param("endDate") LocalDateTime endDate);
}
