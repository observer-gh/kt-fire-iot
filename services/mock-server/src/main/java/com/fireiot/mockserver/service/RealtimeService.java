package com.fireiot.mockserver.service;

import com.fireiot.mockserver.model.Realtime;
import com.fireiot.mockserver.repository.RealtimeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Service
public class RealtimeService {

    @Autowired
    private RealtimeRepository realtimeRepository;

    public List<Realtime> getAllRealtimeData() {
        return realtimeRepository.findAll();
    }

    public Optional<Realtime> getRealtimeDataById(String equipmentDataId) {
        return realtimeRepository.findById(equipmentDataId);
    }

    public List<Realtime> getRealtimeDataByEquipmentId(String equipmentId) {
        return realtimeRepository.findByEquipmentId(equipmentId);
    }

    public List<Realtime> getRealtimeDataByFacilityId(String facilityId) {
        return realtimeRepository.findByFacilityId(facilityId);
    }

    public List<Realtime> getRealtimeDataByLocation(String equipmentLocation) {
        return realtimeRepository.findByEquipmentLocation(equipmentLocation);
    }

    public List<Realtime> getRealtimeDataByTemperatureRange(BigDecimal minTemp, BigDecimal maxTemp) {
        return realtimeRepository.findByTemperatureBetween(minTemp, maxTemp);
    }

    public List<Realtime> getRealtimeDataByHumidityRange(BigDecimal minHumidity, BigDecimal maxHumidity) {
        return realtimeRepository.findByHumidityBetween(minHumidity, maxHumidity);
    }

    public List<Realtime> getRealtimeDataWithHighSmokeDensity(BigDecimal threshold) {
        return realtimeRepository.findBySmokeDensityGreaterThan(threshold);
    }

    public List<Realtime> getRealtimeDataWithHighCoLevel(BigDecimal threshold) {
        return realtimeRepository.findByCoLevelGreaterThan(threshold);
    }

    public List<Realtime> getRealtimeDataWithHighGasLevel(BigDecimal threshold) {
        return realtimeRepository.findByGasLevelGreaterThan(threshold);
    }

    public List<Realtime> getRealtimeDataByTemperatureRangeQuery(BigDecimal minTemp, BigDecimal maxTemp) {
        return realtimeRepository.findByTemperatureRange(minTemp, maxTemp);
    }

    public List<Realtime> getRealtimeDataByHumidityRangeQuery(BigDecimal minHumidity, BigDecimal maxHumidity) {
        return realtimeRepository.findByHumidityRange(minHumidity, maxHumidity);
    }

    public List<Realtime> getRealtimeDataBySmokeDensityThreshold(BigDecimal threshold) {
        return realtimeRepository.findBySmokeDensityThreshold(threshold);
    }

    public Realtime saveRealtimeData(Realtime realtimeData) {
        return realtimeRepository.save(realtimeData);
    }

    public boolean deleteRealtimeData(String equipmentDataId) {
        if (realtimeRepository.existsById(equipmentDataId)) {
            realtimeRepository.deleteById(equipmentDataId);
            return true;
        }
        return false;
    }

    public long getTotalRealtimeDataCount() {
        return realtimeRepository.count();
    }
}
