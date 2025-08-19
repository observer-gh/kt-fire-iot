import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import pandas as pd

from ..database import get_db
from ..db_models import Realtime, Facility, Equipment, Alert

logger = logging.getLogger(__name__)

class FireSensorDataManager:
    """Manage real-time sensor data from realtime table"""
    
    def __init__(self):
        self.db = next(get_db())
        
    def get_realtime_data(self, facility_id: Optional[str] = None, equipment_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get latest sensor readings from realtime table"""
        try:
            query = """
            SELECT equipment_data_id, equipment_id, facility_id, equipment_location,
                   measured_at, ingested_at, temperature, humidity, smoke_density, 
                   co_level, gas_level, version
            FROM realtime 
            WHERE 1=1
            """
            params = []
            
            if facility_id:
                query += " AND facility_id = %s"
                params.append(facility_id)
            if equipment_id:
                query += " AND equipment_id = %s" 
                params.append(equipment_id)
                
            query += " ORDER BY measured_at DESC LIMIT 1000"
            
            result = self.db.execute(text(query), params)
            rows = result.fetchall()
            
            return [
                {
                    'equipment_data_id': row[0],
                    'equipment_id': row[1],
                    'facility_id': row[2],
                    'equipment_location': row[3],
                    'measured_at': row[4],
                    'ingested_at': row[5],
                    'temperature': float(row[6]) if row[6] is not None else None,
                    'humidity': float(row[7]) if row[7] is not None else None,
                    'smoke_density': float(row[8]) if row[8] is not None else None,
                    'co_level': float(row[9]) if row[9] is not None else None,
                    'gas_level': float(row[10]) if row[10] is not None else None,
                    'version': row[11]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error getting realtime data: {e}")
            return []
        
    def get_historical_data(self, start_time: datetime, end_time: datetime, facility_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get historical sensor data for charts - handle NULL values"""
        try:
            query = """
            SELECT equipment_data_id, equipment_id, facility_id, equipment_location,
                   measured_at, temperature, humidity, smoke_density, co_level, gas_level
            FROM realtime 
            WHERE measured_at BETWEEN %s AND %s
            """
            params = [start_time, end_time]
            
            if facility_id:
                query += " AND facility_id = %s"
                params.append(facility_id)
                
            query += " ORDER BY measured_at ASC"
            
            result = self.db.execute(text(query), params)
            rows = result.fetchall()
            
            return [
                {
                    'equipment_data_id': row[0],
                    'equipment_id': row[1],
                    'facility_id': row[2],
                    'equipment_location': row[3],
                    'measured_at': row[4],
                    'temperature': float(row[5]) if row[5] is not None else None,
                    'humidity': float(row[6]) if row[6] is not None else None,
                    'smoke_density': float(row[7]) if row[7] is not None else None,
                    'co_level': float(row[8]) if row[8] is not None else None,
                    'gas_level': float(row[9]) if row[9] is not None else None
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []
        
    def get_facility_summary(self) -> List[Dict[str, Any]]:
        """Get facility-level aggregated data - handle NULL facility_id"""
        try:
            query = """
            SELECT COALESCE(facility_id, 'UNKNOWN') as facility_id,
                   COUNT(DISTINCT equipment_id) as equipment_count,
                   COUNT(*) as total_readings,
                   COUNT(CASE WHEN temperature IS NOT NULL THEN 1 END) as temp_readings,
                   COUNT(CASE WHEN smoke_density IS NOT NULL THEN 1 END) as smoke_readings,
                   AVG(CASE WHEN temperature IS NOT NULL THEN temperature END) as avg_temperature,
                   MAX(CASE WHEN smoke_density IS NOT NULL THEN smoke_density END) as max_smoke_density
            FROM realtime 
            WHERE measured_at > NOW() - INTERVAL '1 hour'
            GROUP BY facility_id
            """
            
            result = self.db.execute(text(query))
            rows = result.fetchall()
            
            return [
                {
                    'facility_id': row[0],
                    'equipment_count': row[1],
                    'total_readings': row[2],
                    'temp_readings': row[3],
                    'smoke_readings': row[4],
                    'avg_temperature': float(row[5]) if row[5] is not None else None,
                    'max_smoke_density': float(row[6]) if row[6] is not None else None
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error getting facility summary: {e}")
            return []
        
    def get_equipment_status(self) -> List[Dict[str, Any]]:
        """Get latest status for each equipment - handle NULL equipment_id"""
        try:
            query = """
            SELECT DISTINCT ON (COALESCE(equipment_id, equipment_data_id)) 
                   equipment_data_id,
                   COALESCE(equipment_id, 'UNKNOWN') as equipment_id,
                   COALESCE(facility_id, 'UNKNOWN') as facility_id,
                   COALESCE(equipment_location, 'UNKNOWN') as equipment_location,
                   measured_at, ingested_at,
                   temperature, humidity, smoke_density, co_level, gas_level, version
            FROM realtime 
            ORDER BY COALESCE(equipment_id, equipment_data_id), measured_at DESC
            """
            
            result = self.db.execute(text(query))
            rows = result.fetchall()
            
            return [
                {
                    'equipment_data_id': row[0],
                    'equipment_id': row[1],
                    'facility_id': row[2],
                    'equipment_location': row[3],
                    'measured_at': row[4],
                    'ingested_at': row[5],
                    'temperature': float(row[6]) if row[6] is not None else None,
                    'humidity': float(row[7]) if row[7] is not None else None,
                    'smoke_density': float(row[8]) if row[8] is not None else None,
                    'co_level': float(row[9]) if row[9] is not None else None,
                    'gas_level': float(row[10]) if row[10] is not None else None,
                    'version': row[11]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error getting equipment status: {e}")
            return []
    
    def get_facilities(self) -> List[str]:
        """Get list of all facilities"""
        try:
            result = self.db.execute(text("SELECT DISTINCT facility_id FROM realtime WHERE facility_id IS NOT NULL"))
            return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error getting facilities: {e}")
            return []
    
    def get_equipment_count(self) -> int:
        """Get total count of equipment"""
        try:
            result = self.db.execute(text("SELECT COUNT(DISTINCT equipment_id) FROM realtime WHERE equipment_id IS NOT NULL"))
            return result.fetchone()[0] or 0
        except Exception as e:
            logger.error(f"Error getting equipment count: {e}")
            return 0
    
    def get_total_readings_count(self) -> int:
        """Get total count of readings in the last hour"""
        try:
            result = self.db.execute(text("SELECT COUNT(*) FROM realtime WHERE measured_at > NOW() - INTERVAL '1 hour'"))
            return result.fetchone()[0] or 0
        except Exception as e:
            logger.error(f"Error getting readings count: {e}")
            return 0
    
    def get_online_equipment_count(self) -> int:
        """Get count of equipment with recent readings (last 5 minutes)"""
        try:
            result = self.db.execute(text("SELECT COUNT(DISTINCT equipment_id) FROM realtime WHERE measured_at > NOW() - INTERVAL '5 minutes' AND equipment_id IS NOT NULL"))
            return result.fetchone()[0] or 0
        except Exception as e:
            logger.error(f"Error getting online equipment count: {e}")
            return 0
