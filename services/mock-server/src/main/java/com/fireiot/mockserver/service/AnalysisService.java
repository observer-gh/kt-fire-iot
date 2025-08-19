package com.fireiot.mockserver.service;

import com.fireiot.mockserver.model.Analysis;
import com.fireiot.mockserver.repository.AnalysisRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Service
public class AnalysisService {

    @Autowired
    private AnalysisRepository analysisRepository;

    public List<Analysis> getAllAnalyses() {
        return analysisRepository.findAll();
    }

    public Optional<Analysis> getAnalysisById(String analysisId) {
        return analysisRepository.findById(analysisId);
    }

    public List<Analysis> getAnalysesByFacilityId(String facilityId) {
        return analysisRepository.findByFacilityId(facilityId);
    }

    public List<Analysis> getAnalysesByIncidentId(String incidentId) {
        return analysisRepository.findByIncidentId(incidentId);
    }

    public List<Analysis> getAnalysesByType(String analysisType) {
        return analysisRepository.findByAnalysisType(analysisType);
    }

    public List<Analysis> getAnalysesByStatus(String status) {
        return analysisRepository.findByStatus(status);
    }

    public List<Analysis> getAnalysesByConfidenceScore(BigDecimal minScore) {
        return analysisRepository.findByConfidenceScoreGreaterThan(minScore);
    }

    public List<Analysis> getAnalysesByRiskProbability(BigDecimal minProbability) {
        return analysisRepository.findByRiskProbabilityGreaterThan(minProbability);
    }

    public List<Analysis> getAnalysesByConfidenceScoreRange(BigDecimal minScore, BigDecimal maxScore) {
        return analysisRepository.findByConfidenceScoreRange(minScore, maxScore);
    }

    public List<Analysis> getAnalysesByRiskProbabilityRange(BigDecimal minProb, BigDecimal maxProb) {
        return analysisRepository.findByRiskProbabilityRange(minProb, maxProb);
    }

    public Analysis saveAnalysis(Analysis analysis) {
        return analysisRepository.save(analysis);
    }

    public boolean deleteAnalysis(String analysisId) {
        if (analysisRepository.existsById(analysisId)) {
            analysisRepository.deleteById(analysisId);
            return true;
        }
        return false;
    }

    public long getTotalAnalysisCount() {
        return analysisRepository.count();
    }
}
