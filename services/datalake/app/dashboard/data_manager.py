import asyncio
import logging
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import pandas as pd

from app.database import execute_query

logger = logging.getLogger(__name__)

class FireSensorDataManager:
    """Manage real-time sensor data from realtime table"""
    
    def __init__(self):
        # API service configuration
        self.api_url = os.getenv('DATALAKE_API_URL', 'http://localhost:8080')
        self.api_host = os.getenv('DATALAKE_API_HOST', 'localhost')
        self.api_port = os.getenv('DATALAKE_API_PORT', '8080')
        
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
            
            rows = execute_query(query, params)
            
            data_list = []
            for row in rows:
                try:
                    data = {
                        'equipment_data_id': str(row['equipment_data_id']) if row['equipment_data_id'] is not None else 'UNKNOWN',
                        'equipment_id': str(row['equipment_id']) if row['equipment_id'] is not None else 'UNKNOWN',
                        'facility_id': str(row['facility_id']) if row['facility_id'] is not None else 'UNKNOWN',
                        'equipment_location': str(row['equipment_location']) if row['equipment_location'] is not None else 'UNKNOWN',
                        'measured_at': row['measured_at'],
                        'ingested_at': row['ingested_at'],
                        'temperature': float(row['temperature']) if row['temperature'] is not None else None,
                        'humidity': float(row['humidity']) if row['humidity'] is not None else None,
                        'smoke_density': float(row['smoke_density']) if row['smoke_density'] is not None else None,
                        'co_level': float(row['co_level']) if row['co_level'] is not None else None,
                        'gas_level': float(row['gas_level']) if row['gas_level'] is not None else None,
                        'version': int(row['version']) if row['version'] is not None else 1
                    }
                    data_list.append(data)
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"Skipping invalid row data: {e}, row: {row}")
                    continue
            
            return data_list
        except Exception as e:
            logger.error(f"Error getting realtime data from database: {e}")
            # Fallback to API service if database is not available
            return self._get_data_from_api(facility_id, equipment_id)
        
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
            
            rows = execute_query(query, params)
            
            data_list = []
            for row in rows:
                try:
                    data = {
                        'equipment_data_id': str(row['equipment_data_id']) if row['equipment_data_id'] is not None else 'UNKNOWN',
                        'equipment_id': str(row['equipment_id']) if row['equipment_id'] is not None else 'UNKNOWN',
                        'facility_id': str(row['facility_id']) if row['facility_id'] is not None else 'UNKNOWN',
                        'equipment_location': str(row['equipment_location']) if row['equipment_location'] is not None else 'UNKNOWN',
                        'measured_at': row['measured_at'],
                        'temperature': float(row['temperature']) if row['temperature'] is not None else None,
                        'humidity': float(row['humidity']) if row['humidity'] is not None else None,
                        'smoke_density': float(row['smoke_density']) if row['smoke_density'] is not None else None,
                        'co_level': float(row['co_level']) if row['co_level'] is not None else None,
                        'gas_level': float(row['gas_level']) if row['gas_level'] is not None else None
                    }
                    data_list.append(data)
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"Skipping invalid historical data row: {e}, row: {row}")
                    continue
            
            return data_list
        except Exception as e:
            logger.error(f"Error getting historical data from database: {e}")
            # Fallback to API service if database is not available
            return self._get_historical_data_from_api(start_time, end_time, facility_id)
        
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
            
            rows = execute_query(query)
            
            summary_list = []
            for row in rows:
                try:
                    summary = {
                        'facility_id': str(row['facility_id']) if row['facility_id'] is not None else 'UNKNOWN',
                        'equipment_count': int(row['equipment_count']) if row['equipment_count'] is not None else 0,
                        'total_readings': int(row['total_readings']) if row['total_readings'] is not None else 0,
                        'temp_readings': int(row['temp_readings']) if row['temp_readings'] is not None else 0,
                        'smoke_readings': int(row['smoke_readings']) if row['smoke_readings'] is not None else 0,
                        'avg_temperature': float(row['avg_temperature']) if row['avg_temperature'] is not None else None,
                        'max_smoke_density': float(row['max_smoke_density']) if row['max_smoke_density'] is not None else None
                    }
                    summary_list.append(summary)
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"Skipping invalid facility summary row: {e}, row: {row}")
                    continue
            
            return summary_list
        except Exception as e:
            logger.error(f"Error getting facility summary from database: {e}")
            # Fallback to API service if database is not available
            return self._get_facility_summary_from_api()
        
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
            
            rows = execute_query(query)
            
            equipment_list = []
            for row in rows:
                try:
                    equipment_data = {
                        'equipment_data_id': str(row['equipment_data_id']) if row['equipment_data_id'] is not None else 'UNKNOWN',
                        'equipment_id': str(row['equipment_id']) if row['equipment_id'] is not None else 'UNKNOWN',
                        'facility_id': str(row['facility_id']) if row['facility_id'] is not None else 'UNKNOWN',
                        'equipment_location': str(row['equipment_location']) if row['equipment_location'] is not None else 'UNKNOWN',
                        'measured_at': row['measured_at'],
                        'ingested_at': row['ingested_at'],
                        'temperature': float(row['temperature']) if row['temperature'] is not None else None,
                        'humidity': float(row['humidity']) if row['humidity'] is not None else None,
                        'smoke_density': float(row['smoke_density']) if row['smoke_density'] is not None else None,
                        'co_level': float(row['co_level']) if row['co_level'] is not None else None,
                        'gas_level': float(row['gas_level']) if row['gas_level'] is not None else None,
                        'version': int(row['version']) if row['version'] is not None else 1
                    }
                    equipment_list.append(equipment_data)
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"Skipping invalid row data: {e}, row: {row}")
                    continue
            
            return equipment_list
        except Exception as e:
            logger.error(f"Error getting equipment status: {e}")
            return []
    
    def get_facilities(self) -> List[str]:
        """Get list of all facilities"""
        try:
            rows = execute_query("SELECT DISTINCT facility_id FROM realtime WHERE facility_id IS NOT NULL")
            return [row['facility_id'] for row in rows]
        except Exception as e:
            logger.error(f"Error getting facilities: {e}")
            return []
    
    def get_equipment_count(self) -> int:
        """Get total equipment count"""
        try:
            result = execute_query("SELECT COUNT(DISTINCT equipment_id) as count FROM realtime")
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error getting equipment count: {e}")
            return 0
    
    def get_storage_metadata_summary(self) -> Optional[Dict[str, Any]]:
        """Get storage metadata summary from API"""
        try:
            response = requests.get(f"{self.api_url}/storage/metadata/stats/summary", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get metadata summary: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting storage metadata summary: {e}")
            return None
    
    def get_storage_metadata(self, limit: int = 100, offset: int = 0, 
                           storage_type: str = None, start_date: str = None, 
                           end_date: str = None) -> Optional[Dict[str, Any]]:
        """Get storage metadata with filtering and pagination"""
        try:
            params = {
                'limit': limit,
                'offset': offset
            }
            if storage_type:
                params['storage_type'] = storage_type
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            
            response = requests.get(f"{self.api_url}/storage/metadata", params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get storage metadata: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting storage metadata: {e}")
            return None
    
    def get_total_readings_count(self) -> int:
        """Get total count of readings in the last hour"""
        try:
            rows = execute_query("SELECT COUNT(*) as count FROM realtime WHERE measured_at > NOW() - INTERVAL '1 hour'")
            return rows[0]['count'] if rows else 0
        except Exception as e:
            logger.error(f"Error getting readings count: {e}")
            return 0
    
    def get_online_equipment_count(self) -> int:
        """Get count of equipment with recent readings (last 5 minutes)"""
        try:
            rows = execute_query("SELECT COUNT(DISTINCT equipment_id) as count FROM realtime WHERE measured_at > NOW() - INTERVAL '5 minutes' AND equipment_id IS NOT NULL")
            return rows[0]['count'] if rows else 0
        except Exception as e:
            logger.error(f"Error getting online equipment count from database: {e}")
            # Fallback to API service if database is not available
            return self._get_online_equipment_count_from_api()
    
    # API Fallback Methods
    def _get_data_from_api(self, facility_id: Optional[str] = None, equipment_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fallback method to get data from API service"""
        try:
            # Try to get stats from API to check if it's available
            response = requests.get(f"{self.api_url}/stats", timeout=5)
            if response.status_code == 200:
                logger.info("Using API service as fallback for realtime data")
                # For now, return empty data as API doesn't have direct data endpoint
                # In the future, you could add a /data endpoint to the API
                return []
            else:
                logger.warning("API service not available")
                return []
        except Exception as e:
            logger.error(f"Error accessing API service: {e}")
            return []
    
    def _get_historical_data_from_api(self, start_time: datetime, end_time: datetime, facility_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fallback method to get historical data from API service"""
        try:
            # Similar to realtime data, API would need a /historical-data endpoint
            logger.info("Using API service as fallback for historical data")
            return []
        except Exception as e:
            logger.error(f"Error accessing API service for historical data: {e}")
            return []
    
    def _get_facility_summary_from_api(self) -> List[Dict[str, Any]]:
        """Fallback method to get facility summary from API service"""
        try:
            # API would need a /facility-summary endpoint
            logger.info("Using API service as fallback for facility summary")
            return []
        except Exception as e:
            logger.error(f"Error accessing API service for facility summary: {e}")
            return []
    
    def _get_online_equipment_count_from_api(self) -> int:
        """Fallback method to get online equipment count from API service"""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                return stats.get('realtime_records', 0)
            else:
                return 0
        except Exception as e:
            logger.error(f"Error accessing API service for equipment count: {e}")
            return 0
