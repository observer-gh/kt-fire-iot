package com.fireiot.mockserver.service;

import com.fireiot.mockserver.model.EquipmentMaintenance;
import com.fireiot.mockserver.repository.EquipmentMaintenanceRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class EquipmentMaintenanceService {

    private static final Logger logger = LoggerFactory.getLogger(EquipmentMaintenanceService.class);

    @Autowired
    private EquipmentMaintenanceRepository equipmentMaintenanceRepository;

    public List<EquipmentMaintenance> getAllMaintenanceLogs() {
        logger.info("Retrieving all maintenance logs");
        return equipmentMaintenanceRepository.findAll();
    }

    public Optional<EquipmentMaintenance> getMaintenanceLogById(String maintenanceLogId) {
        logger.info("Retrieving maintenance log by ID: {}", maintenanceLogId);
        return equipmentMaintenanceRepository.findById(maintenanceLogId);
    }

    public List<EquipmentMaintenance> getMaintenanceLogsByEquipmentId(String equipmentId) {
        logger.info("Retrieving maintenance logs by equipment ID: {}", equipmentId);
        return equipmentMaintenanceRepository.findByEquipmentId(equipmentId);
    }

    public List<EquipmentMaintenance> getMaintenanceLogsByFacilityId(String facilityId) {
        logger.info("Retrieving maintenance logs by facility ID: {}", facilityId);
        return equipmentMaintenanceRepository.findByFacilityId(facilityId);
    }

    public List<EquipmentMaintenance> getMaintenanceLogsByLocation(String equipmentLocation) {
        logger.info("Retrieving maintenance logs by location: {}", equipmentLocation);
        return equipmentMaintenanceRepository.findByEquipmentLocation(equipmentLocation);
    }

    public List<EquipmentMaintenance> getMaintenanceLogsByType(EquipmentMaintenance.MaintenanceType maintenanceType) {
        logger.info("Retrieving maintenance logs by type: {}", maintenanceType);
        return equipmentMaintenanceRepository.findByMaintenanceType(maintenanceType);
    }

    public List<EquipmentMaintenance> getMaintenanceLogsByStatus(String statusCode) {
        logger.info("Retrieving maintenance logs by status code: {}", statusCode);
        return equipmentMaintenanceRepository.findByStatusCode(statusCode);
    }

    public List<EquipmentMaintenance> getMaintenanceLogsByManager(String manager) {
        logger.info("Retrieving maintenance logs by manager: {}", manager);
        return equipmentMaintenanceRepository.findByManager(manager);
    }

    public List<EquipmentMaintenance> getMaintenanceLogsByScheduledDateRange(LocalDateTime startDate, LocalDateTime endDate) {
        logger.info("Retrieving maintenance logs scheduled between {} and {}", startDate, endDate);
        return equipmentMaintenanceRepository.findByScheduledDateBetween(startDate, endDate);
    }

    public List<EquipmentMaintenance> getMaintenanceLogsByPerformedDateRange(LocalDateTime startDate, LocalDateTime endDate) {
        logger.info("Retrieving maintenance logs performed between {} and {}", startDate, endDate);
        return equipmentMaintenanceRepository.findByPerformedDateBetween(startDate, endDate);
    }

    public List<EquipmentMaintenance> getMaintenanceLogsByNextScheduledDate(LocalDateTime date) {
        logger.info("Retrieving maintenance logs with next scheduled date before: {}", date);
        return equipmentMaintenanceRepository.findByNextScheduledDateBefore(date);
    }

    public List<EquipmentMaintenance> getMaintenanceLogsByEquipmentAndStatus(String equipmentId, String statusCode) {
        logger.info("Retrieving maintenance logs by equipment ID: {} and status code: {}", equipmentId, statusCode);
        return equipmentMaintenanceRepository.findByEquipmentIdAndStatus(equipmentId, statusCode);
    }

    public List<EquipmentMaintenance> getScheduledMaintenanceInPeriod(LocalDateTime startDate, LocalDateTime endDate, String statusCode) {
        logger.info("Retrieving scheduled maintenance logs in period {} to {} with status code: {}", startDate, endDate, statusCode);
        return equipmentMaintenanceRepository.findScheduledMaintenanceInPeriod(startDate, endDate, statusCode);
    }

    public List<EquipmentMaintenance> getOverdueMaintenance(LocalDateTime currentDate) {
        logger.info("Retrieving overdue maintenance logs as of: {}", currentDate);
        return equipmentMaintenanceRepository.findOverdueMaintenance(currentDate);
    }

    public EquipmentMaintenance saveMaintenanceLog(EquipmentMaintenance maintenanceLog) {
        logger.info("Saving maintenance log with ID: {}", maintenanceLog.getMaintenanceLogId());
        return equipmentMaintenanceRepository.save(maintenanceLog);
    }

    public boolean deleteMaintenanceLog(String maintenanceLogId) {
        logger.info("Deleting maintenance log with ID: {}", maintenanceLogId);
        if (equipmentMaintenanceRepository.existsById(maintenanceLogId)) {
            equipmentMaintenanceRepository.deleteById(maintenanceLogId);
            return true;
        }
        return false;
    }

    public long getTotalMaintenanceLogCount() {
        return equipmentMaintenanceRepository.count();
    }
}
