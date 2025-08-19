package com.fireiot.mockserver.repository;

import com.fireiot.mockserver.model.Analysis;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface AnalysisRepository extends JpaRepository<Analysis, String> {

    List<Analysis> findByFacilityId(String facilityId);

    List<Analysis> findByIncidentId(String incidentId);

    List<Analysis> findByAnalysisType(String analysisType);

    List<Analysis> findByStatus(String status);

    List<Analysis> findByConfidenceScoreGreaterThan(BigDecimal minScore);

    List<Analysis> findByRiskProbabilityGreaterThan(BigDecimal minProbability);

    @Query("SELECT a FROM Analysis a WHERE a.confidenceScore >= :minScore AND a.confidenceScore <= :maxScore")
    List<Analysis> findByConfidenceScoreRange(@Param("minScore") BigDecimal minScore, @Param("maxScore") BigDecimal maxScore);

    @Query("SELECT a FROM Analysis a WHERE a.riskProbability >= :minProb AND a.riskProbability <= :maxProb")
    List<Analysis> findByRiskProbabilityRange(@Param("minProb") BigDecimal minProb, @Param("maxProb") BigDecimal maxProb);
}
