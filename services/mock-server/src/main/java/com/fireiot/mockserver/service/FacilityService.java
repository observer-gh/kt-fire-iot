package com.fireiot.mockserver.service;

import com.fireiot.mockserver.model.Facility;
import com.fireiot.mockserver.repository.FacilityRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class FacilityService {

    @Autowired
    private FacilityRepository facilityRepository;

    public List<Facility> getAllFacilities() {
        return facilityRepository.findAll();
    }

    public Optional<Facility> getFacilityById(String facilityId) {
        return facilityRepository.findById(facilityId);
    }

    public List<Facility> getFacilitiesByType(String facilityType) {
        return facilityRepository.findByFacilityType(facilityType);
    }

    public List<Facility> getFacilitiesByRiskLevel(String riskLevel) {
        return facilityRepository.findByRiskLevel(riskLevel);
    }

    public List<Facility> getFacilitiesByManager(String managerName) {
        return facilityRepository.findByManagerName(managerName);
    }

    public List<Facility> getFacilitiesWithActiveAlerts(Integer minCount) {
        return facilityRepository.findByActiveAlertsCountGreaterThan(minCount);
    }

    public List<Facility> getFacilitiesWithOnlineSensors(Integer minCount) {
        return facilityRepository.findByOnlineSensorsCountGreaterThan(minCount);
    }

    public List<Facility> getFacilitiesByAddress(String address) {
        return facilityRepository.findByAddressContaining(address);
    }

    public Facility saveFacility(Facility facility) {
        return facilityRepository.save(facility);
    }

    public boolean deleteFacility(String facilityId) {
        if (facilityRepository.existsById(facilityId)) {
            facilityRepository.deleteById(facilityId);
            return true;
        }
        return false;
    }

    public long getTotalFacilityCount() {
        return facilityRepository.count();
    }
}
