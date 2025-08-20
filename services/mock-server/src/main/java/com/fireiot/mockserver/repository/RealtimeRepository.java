package com.fireiot.mockserver.repository;

import com.fireiot.mockserver.model.Realtime;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface RealtimeRepository extends JpaRepository<Realtime, String> {

    List<Realtime> findByEquipmentId(String equipmentId);

    List<Realtime> findByFacilityId(String facilityId);

    List<Realtime> findByEquipmentLocation(String equipmentLocation);

    List<Realtime> findByTemperatureBetween(BigDecimal minTemp, BigDecimal maxTemp);

    List<Realtime> findByHumidityBetween(BigDecimal minHumidity, BigDecimal maxHumidity);

    List<Realtime> findBySmokeDensityGreaterThan(BigDecimal threshold);

    List<Realtime> findByCoLevelGreaterThan(BigDecimal threshold);

    List<Realtime> findByGasLevelGreaterThan(BigDecimal threshold);

    @Query("SELECT r FROM Realtime r WHERE r.temperature BETWEEN :minTemp AND :maxTemp")
    List<Realtime> findByTemperatureRange(@Param("minTemp") BigDecimal minTemp, @Param("maxTemp") BigDecimal maxTemp);

    @Query("SELECT r FROM Realtime r WHERE r.humidity BETWEEN :minHumidity AND :maxHumidity")
    List<Realtime> findByHumidityRange(@Param("minHumidity") BigDecimal minHumidity, @Param("maxHumidity") BigDecimal maxHumidity);

    @Query("SELECT r FROM Realtime r WHERE r.smokeDensity > :threshold")
    List<Realtime> findBySmokeDensityThreshold(@Param("threshold") BigDecimal threshold);
}
