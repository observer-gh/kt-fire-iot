package com.fireiot.mockserver.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "realtime")
public class Realtime {

    @Id
    @Column(name = "equipment_data_id", length = 10, nullable = false)
    private String equipmentDataId;

    @Column(name = "equipment_id", length = 10)
    private String equipmentId;

    @Column(name = "facility_id", length = 10)
    private String facilityId;

    @Column(name = "equipment_location", length = 40)
    private String equipmentLocation;

    @Column(name = "measured_at")
    private LocalDateTime measuredAt;

    @Column(name = "ingested_at")
    private LocalDateTime ingestedAt;

    @Column(name = "temperature", precision = 6, scale = 2)
    private BigDecimal temperature;

    @Column(name = "humidity", precision = 5, scale = 2)
    private BigDecimal humidity;

    @Column(name = "smoke_density", precision = 6, scale = 3)
    private BigDecimal smokeDensity;

    @Column(name = "co_level", precision = 6, scale = 3)
    private BigDecimal coLevel;

    @Column(name = "gas_level", precision = 6, scale = 3)
    private BigDecimal gasLevel;

    @Column(name = "version")
    private Integer version;

    // Default constructor
    public Realtime() {}

    // Constructor with required fields
    public Realtime(String equipmentDataId) {
        this.equipmentDataId = equipmentDataId;
    }

    // Getters and Setters
    public String getEquipmentDataId() {
        return equipmentDataId;
    }

    public void setEquipmentDataId(String equipmentDataId) {
        this.equipmentDataId = equipmentDataId;
    }

    public String getEquipmentId() {
        return equipmentId;
    }

    public void setEquipmentId(String equipmentId) {
        this.equipmentId = equipmentId;
    }

    public String getFacilityId() {
        return facilityId;
    }

    public void setFacilityId(String facilityId) {
        this.facilityId = facilityId;
    }

    public String getEquipmentLocation() {
        return equipmentLocation;
    }

    public void setEquipmentLocation(String equipmentLocation) {
        this.equipmentLocation = equipmentLocation;
    }

    public LocalDateTime getMeasuredAt() {
        return measuredAt;
    }

    public void setMeasuredAt(LocalDateTime measuredAt) {
        this.measuredAt = measuredAt;
    }

    public LocalDateTime getIngestedAt() {
        return ingestedAt;
    }

    public void setIngestedAt(LocalDateTime ingestedAt) {
        this.ingestedAt = ingestedAt;
    }

    public BigDecimal getTemperature() {
        return temperature;
    }

    public void setTemperature(BigDecimal temperature) {
        this.temperature = temperature;
    }

    public BigDecimal getHumidity() {
        return humidity;
    }

    public void setHumidity(BigDecimal humidity) {
        this.humidity = humidity;
    }

    public BigDecimal getSmokeDensity() {
        return smokeDensity;
    }

    public void setSmokeDensity(BigDecimal smokeDensity) {
        this.smokeDensity = smokeDensity;
    }

    public BigDecimal getCoLevel() {
        return coLevel;
    }

    public void setCoLevel(BigDecimal coLevel) {
        this.coLevel = coLevel;
    }

    public BigDecimal getGasLevel() {
        return gasLevel;
    }

    public void setGasLevel(BigDecimal gasLevel) {
        this.gasLevel = gasLevel;
    }

    public Integer getVersion() {
        return version;
    }

    public void setVersion(Integer version) {
        this.version = version;
    }
}
