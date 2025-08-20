package com.fireiot.mockserver.service;

import com.fireiot.mockserver.model.Alert;
import com.fireiot.mockserver.repository.AlertRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class AlertService {

    @Autowired
    private AlertRepository alertRepository;

    public List<Alert> getAllAlerts() {
        return alertRepository.findAll();
    }

    public Optional<Alert> getAlertById(String alertId) {
        return alertRepository.findById(alertId);
    }

    public List<Alert> getAlertsByEquipmentId(String equipmentId) {
        return alertRepository.findByEquipmentId(equipmentId);
    }

    public List<Alert> getAlertsByFacilityId(String facilityId) {
        return alertRepository.findByFacilityId(facilityId);
    }

    public List<Alert> getAlertsByLocation(String equipmentLocation) {
        return alertRepository.findByEquipmentLocation(equipmentLocation);
    }

    public List<Alert> getAlertsByType(Alert.AlertType alertType) {
        return alertRepository.findByAlertType(alertType);
    }

    public List<Alert> getAlertsBySeverity(Alert.AlertSeverity severity) {
        return alertRepository.findBySeverity(severity);
    }

    public List<Alert> getAlertsByStatus(String status) {
        return alertRepository.findByStatus(status);
    }

    public List<Alert> getAlertsByDateRange(LocalDateTime startDate, LocalDateTime endDate) {
        return alertRepository.findByCreatedAtBetween(startDate, endDate);
    }

    public List<Alert> getActiveAlerts() {
        return alertRepository.findByStatus("ACTIVE");
    }

    public List<Alert> getResolvedAlerts() {
        return alertRepository.findByStatus("RESOLVED");
    }

    public List<Alert> getUnresolvedAlerts() {
        return alertRepository.findByResolvedAtIsNull();
    }

    public List<Alert> getAlertsByLocationContaining(String location) {
        return alertRepository.findByLocationContaining(location);
    }

    public Alert saveAlert(Alert alert) {
        return alertRepository.save(alert);
    }

    public boolean deleteAlert(String alertId) {
        if (alertRepository.existsById(alertId)) {
            alertRepository.deleteById(alertId);
            return true;
        }
        return false;
    }

    public long getTotalAlertCount() {
        return alertRepository.count();
    }
}
