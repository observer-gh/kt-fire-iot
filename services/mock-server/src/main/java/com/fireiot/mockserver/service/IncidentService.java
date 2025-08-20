package com.fireiot.mockserver.service;

import com.fireiot.mockserver.model.Incident;
import com.fireiot.mockserver.repository.IncidentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class IncidentService {

    @Autowired
    private IncidentRepository incidentRepository;

    public List<Incident> getAllIncidents() {
        return incidentRepository.findAll();
    }

    public Optional<Incident> getIncidentById(String incidentId) {
        return incidentRepository.findById(incidentId);
    }

    public List<Incident> getIncidentsByFacilityId(String facilityId) {
        return incidentRepository.findByFacilityId(facilityId);
    }

    public List<Incident> getIncidentsByType(String incidentType) {
        return incidentRepository.findByIncidentType(incidentType);
    }

    public List<Incident> getIncidentsBySeverity(Incident.IncidentSeverity severity) {
        return incidentRepository.findBySeverity(severity);
    }

    public List<Incident> getIncidentsByDateRange(LocalDateTime startDate, LocalDateTime endDate) {
        return incidentRepository.findByCreatedAtBetween(startDate, endDate);
    }

    public List<Incident> getUnresolvedIncidents() {
        return incidentRepository.findByResolvedAtIsNull();
    }

    public Incident saveIncident(Incident incident) {
        return incidentRepository.save(incident);
    }

    public boolean deleteIncident(String incidentId) {
        if (incidentRepository.existsById(incidentId)) {
            incidentRepository.deleteById(incidentId);
            return true;
        }
        return false;
    }

    public long getTotalIncidentCount() {
        return incidentRepository.count();
    }
}
