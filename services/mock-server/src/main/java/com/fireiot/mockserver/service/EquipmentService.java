package com.fireiot.mockserver.service;

import com.fireiot.mockserver.model.Equipment;
import com.fireiot.mockserver.repository.EquipmentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class EquipmentService {

    @Autowired
    private EquipmentRepository equipmentRepository;

    public List<Equipment> getAllEquipment() {
        return equipmentRepository.findAll();
    }

    public Optional<Equipment> getEquipmentById(String equipmentId) {
        return equipmentRepository.findById(equipmentId);
    }

    public List<Equipment> getEquipmentByFacilityId(String facilityId) {
        return equipmentRepository.findByFacilityId(facilityId);
    }

    public List<Equipment> getEquipmentByType(String equipmentType) {
        return equipmentRepository.findByEquipmentType(equipmentType);
    }

    public List<Equipment> getEquipmentByStatusCode(String statusCode) {
        return equipmentRepository.findByStatusCode(statusCode);
    }

    public List<Equipment> getEquipmentByLocation(String equipmentLocation) {
        return equipmentRepository.findByEquipmentLocation(equipmentLocation);
    }

    public List<Equipment> getEquipmentByInstallationPeriod(LocalDateTime startDate, LocalDateTime endDate) {
        return equipmentRepository.findByInstalledAtBetween(startDate, endDate);
    }

    public List<Equipment> getExpiringEquipment(LocalDateTime expiryDate) {
        return equipmentRepository.findByExpiredAtBefore(expiryDate);
    }

    public List<Equipment> getEquipmentByFacilityAndType(String facilityId, String equipmentType) {
        return equipmentRepository.findByFacilityIdAndEquipmentType(facilityId, equipmentType);
    }

    public List<Equipment> getEquipmentInstalledInPeriod(LocalDateTime startDate, LocalDateTime endDate) {
        return equipmentRepository.findEquipmentInstalledInPeriod(startDate, endDate);
    }

    public List<Equipment> getExpiringEquipmentData(LocalDateTime expiryDate) {
        return equipmentRepository.findExpiringEquipment(expiryDate);
    }

    public Equipment saveEquipment(Equipment equipment) {
        return equipmentRepository.save(equipment);
    }

    public boolean deleteEquipment(String equipmentId) {
        if (equipmentRepository.existsById(equipmentId)) {
            equipmentRepository.deleteById(equipmentId);
            return true;
        }
        return false;
    }

    public long getTotalEquipmentCount() {
        return equipmentRepository.count();
    }
}
