import redis
import logging
import json
import re
from typing import Optional, Any, List, Dict
from datetime import datetime
from urllib.parse import urlparse
from .config import settings
import os

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client wrapper for caching and session management"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        redis_url = settings.redis_url
        print('asddfdff', redis_url)
        self._connect()
    
    def _connect(self):
        """Redis 연결 설정 및 연결"""
        try:
            # Redis URL을 환경변수나 설정에서 가져옴
            redis_url = settings.redis_url
            print(redis_url)
            redis_url = 'rediss://:0IjI1IN6GmjPTjXk3B4pUJEB2DRRB936AAzCaFDskPk=@fire-iot-redis-dev.redis.cache.windows.net:6380'
            if not redis_url:
                logger.warning("REDIS_URL이 설정되지 않았습니다. Redis 연결을 건너뜁니다.")
                return
            
            # Redis URL 파싱
            connection_params = self._parse_redis_url(redis_url)
            print('asdf', connection_params)
            
            # Redis 클라이언트 생성 및 연결
            self.client = redis.Redis(**connection_params)
            
            # 연결 테스트
            self.client.ping()
            logger.info("Redis 연결 성공")
            
        except Exception as e:
            logger.error(f"Redis 연결 실패: {e}")
            self.client = None
    
    def _parse_redis_url(self, redis_url: str) -> Dict[str, Any]:
        """Redis URL을 파싱하여 연결 파라미터로 변환"""
        try:
            # rediss:// 형식의 URL 파싱
            if redis_url.startswith('rediss://'):
                # SSL 연결을 위한 설정
                parsed = urlparse(redis_url)
                
                # 비밀번호 추출 (URL 인코딩된 형태)
                password = parsed.password
                if password:
                    # URL 디코딩
                    import urllib.parse
                    password = urllib.parse.unquote(password)
                
                # 호스트와 포트 추출
                host = parsed.hostname
                port = parsed.port or 6380  # 기본 포트
                
                connection_params = {
                    'host': host,
                    'port': port,
                    'password': password,
                    'ssl': True,
                    'ssl_cert_reqs': None,  # SSL 인증서 검증 비활성화 (Azure Redis용)
                    'decode_responses': True,  # 응답을 자동으로 디코딩
                    # 'socket_connect_timeout': 10,
                    # 'socket_timeout': 10,
                    'retry_on_timeout': True,
                    'health_check_interval': 30
                }
                
                logger.debug(f"Redis 연결 파라미터: host={host}, port={port}, ssl=True")
                return connection_params
                
            else:
                # 일반 redis:// 형식 처리
                parsed = urlparse(redis_url)
                connection_params = {
                    'host': parsed.hostname,
                    'port': parsed.port or 6379,
                    'password': parsed.password,
                    'decode_responses': True,
                    'socket_connect_timeout': 10,
                    'socket_timeout': 10,
                    'retry_on_timeout': True,
                    'health_check_interval': 30
                }
                
                logger.debug(f"Redis 연결 파라미터: host={parsed.hostname}, port={parsed.port}")
                return connection_params
                
        except Exception as e:
            logger.error(f"Redis URL 파싱 실패: {e}")
            raise ValueError(f"잘못된 Redis URL 형식: {redis_url}")
    
    def reconnect(self) -> bool:
        """Redis 재연결 시도"""
        try:
            if self.client:
                self.client.close()
            
            self._connect()
            return self.is_connected()
        except Exception as e:
            logger.error(f"Redis 재연결 실패: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        if not self.is_connected():
            return None
        try:
            value = self.client.get(key)
            
            # JSON 문자열인 경우 자동 파싱
            if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                try:
                    import json
                    return json.loads(value)
                except json.JSONDecodeError:
                    # JSON 파싱 실패 시 원본 값 반환
                    pass
            
            return value
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration"""
        if not self.is_connected():
            return False
        try:
            # 딕셔너리나 리스트인 경우 JSON으로 직렬화
            if isinstance(value, (dict, list)):
                import json
                value = json.dumps(value)
            return self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.is_connected():
            return False
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self.is_connected():
            return False
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False
    
    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            self.client = None

    # 센서 데이터 저장 관련 메서드들
    def save_sensor_data(self, data: Dict[str, Any]) -> bool:
        """센서 데이터를 Redis에 저장"""
        if not self.is_connected():
            return False
        
        try:
            # 입력 데이터 검증
            if not isinstance(data, dict):
                logger.error(f"입력 데이터가 딕셔너리가 아님: {type(data)}")
                return False
            
            if 'equipment_id' not in data:
                logger.error("equipment_id 필드가 없습니다")
                return False
            
            # datetime 객체를 ISO 문자열로 변환
            serializable_data = self._make_json_serializable(data)
            
            # 고유 키 생성 (equipment_id + timestamp)
            timestamp = serializable_data.get('measured_at', datetime.utcnow().isoformat())
            if isinstance(timestamp, str):
                # 이미 ISO 문자열인 경우 그대로 사용
                pass
            else:
                # datetime 객체인 경우 ISO 문자열로 변환
                timestamp = timestamp.isoformat()
            
            key = f"sensor_data:{serializable_data['equipment_id']}:{timestamp}"
            
            # 데이터 저장
            success = self.client.set(key, json.dumps(serializable_data))
            
            if success:
                # 센서 데이터 목록에 키 추가
                list_key = f"sensor_data_list:{serializable_data['equipment_id']}"
                self.client.lpush(list_key, key)
                
                # 전체 센서 데이터 목록에도 추가
                all_sensors_key = "all_sensor_data_keys"
                self.client.lpush(all_sensors_key, key)
                
                logger.debug(f"센서 데이터 Redis 저장 성공: {key}")
                return True
            else:
                logger.error(f"Redis 저장 실패: {key}")
                return False
                
        except Exception as e:
            logger.error(f"센서 데이터 Redis 저장 실패: {e}")
            logger.error(f"문제가 된 데이터: {data}")
            return False
    
    def _make_json_serializable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터를 JSON 직렬화 가능한 형태로 변환"""
        serializable_data = {}
        
        for key, value in data.items():
            if isinstance(value, datetime):
                # datetime 객체를 ISO 문자열로 변환
                serializable_data[key] = value.isoformat()
            elif isinstance(value, dict):
                # 중첩된 딕셔너리도 재귀적으로 처리
                serializable_data[key] = self._make_json_serializable(value)
            elif isinstance(value, list):
                # 리스트의 각 항목도 처리
                serializable_data[key] = [
                    self._make_json_serializable(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                # 기본 타입은 그대로 사용
                serializable_data[key] = value
        
        return serializable_data
    
    def get_all_sensor_data_keys(self) -> List[str]:
        """모든 센서 데이터 키 목록 반환"""
        if not self.is_connected():
            return []
        try:
            all_sensors_key = "all_sensor_data_keys"
            keys = self.client.lrange(all_sensors_key, 0, -1)
            return keys
        except Exception as e:
            logger.error(f"센서 데이터 키 목록 조회 실패: {e}")
            return []
    
    def get_sensor_data_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """키로 센서 데이터 조회"""
        if not self.is_connected():
            return None
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"센서 데이터 조회 실패 ({key}): {e}")
            return None
    
    def flush_sensor_data_to_storage(self) -> List[Dict[str, Any]]:
        """Redis의 모든 센서 데이터를 조회하고 반환 (flush용)"""
        if not self.is_connected():
            return []
        try:
            all_keys = self.get_all_sensor_data_keys()
            sensor_data_list = []
            
            for key in all_keys:
                try:
                    data = self.get_sensor_data_by_key(key)
                    if data:
                        # ISO 문자열을 datetime 객체로 변환
                        converted_data = self._convert_iso_strings_to_datetime(data)
                        
                        # 데이터 유효성 검증
                        if self._validate_sensor_data(converted_data):
                            sensor_data_list.append(converted_data)
                        else:
                            logger.warning(f"유효하지 않은 센서 데이터 제외: {key}")
                            # 유효하지 않은 데이터는 Redis에서 삭제
                            self.client.delete(key)
                    else:
                        logger.warning(f"Redis에서 데이터를 가져올 수 없음: {key}")
                        # 데이터가 없는 키도 삭제
                        self.client.delete(key)
                        
                except Exception as e:
                    logger.error(f"개별 센서 데이터 처리 오류 ({key}): {e}")
                    # 오류가 발생한 키도 삭제
                    try:
                        self.client.delete(key)
                    except:
                        pass
                    continue
            
            logger.info(f"Redis에서 {len(sensor_data_list)}개의 센서 데이터를 flush용으로 조회")
            return sensor_data_list
        except Exception as e:
            logger.error(f"센서 데이터 flush 조회 실패: {e}")
            return []
    
    def _convert_iso_strings_to_datetime(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """ISO 문자열을 datetime 객체로 변환"""
        converted_data = {}
        
        for key, value in data.items():
            if isinstance(value, str) and key in ['measured_at', 'ingested_at']:
                try:
                    # ISO 문자열을 datetime 객체로 변환
                    if value.endswith('Z'):
                        value = value[:-1] + '+00:00'
                    converted_data[key] = datetime.fromisoformat(value)
                except ValueError:
                    # 변환 실패 시 원본 값 유지
                    logger.warning(f"날짜 변환 실패 ({key}): {value}")
                    converted_data[key] = value
            elif isinstance(value, dict):
                # 중첩된 딕셔너리도 재귀적으로 처리
                converted_data[key] = self._convert_iso_strings_to_datetime(value)
            elif isinstance(value, list):
                # 리스트의 각 항목도 처리
                converted_data[key] = [
                    self._convert_iso_strings_to_datetime(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                # 기본 타입은 그대로 사용
                converted_data[key] = value
        
        return converted_data
    
    def _validate_sensor_data(self, data: Dict[str, Any]) -> bool:
        """센서 데이터의 유효성을 검증"""
        required_fields = ['equipment_id', 'measured_at']
        
        for field in required_fields:
            if field not in data:
                logger.warning(f"필수 필드 누락: {field}")
                return False
        
        # equipment_id가 문자열인지 확인
        if not isinstance(data.get('equipment_id'), str):
            logger.warning(f"equipment_id가 문자열이 아님: {type(data.get('equipment_id'))}")
            return False
        
        # measured_at가 datetime인지 확인
        if not isinstance(data.get('measured_at'), datetime):
            logger.warning(f"measured_at가 datetime이 아님: {type(data.get('measured_at'))}")
            return False
        
        return True
    
    def clear_sensor_data(self) -> bool:
        """Redis의 모든 센서 데이터 삭제 (flush 후 정리용)"""
        if not self.is_connected():
            return False
        try:
            all_keys = self.get_all_sensor_data_keys()
            
            # 개별 센서 데이터 삭제
            for key in all_keys:
                self.client.delete(key)
            
            # 센서별 목록 키들 삭제
            pattern = "sensor_data_list:*"
            list_keys = self.client.keys(pattern)
            for key in list_keys:
                self.client.delete(key)
            
            # 전체 목록 키 삭제
            self.client.delete("all_sensor_data_keys")
            
            logger.info(f"Redis 센서 데이터 {len(all_keys)}개 삭제 완료")
            return True
        except Exception as e:
            logger.error(f"센서 데이터 삭제 실패: {e}")
            return False
    
    def get_sensor_data_count(self) -> int:
        """Redis에 저장된 센서 데이터 개수 반환"""
        if not self.is_connected():
            return 0
        try:
            all_keys = self.get_all_sensor_data_keys()
            return len(all_keys)
        except Exception as e:
            logger.error(f"센서 데이터 개수 조회 실패: {e}")
            return 0

# Global Redis client instance
redis_client = RedisClient()
