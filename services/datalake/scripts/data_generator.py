#!/usr/bin/env python3
"""
DataLake 대시보드용 데이터 생성 및 전송 스크립트
일정 주기로 센서 데이터를 생성하여 API에 전송
"""

import requests
import time
import random
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List
import signal
import sys

class DataGenerator:
    def __init__(self, api_url: str = "http://localhost:8084", interval: float = 2.0):
        self.api_url = api_url
        self.interval = interval
        self.running = True
        self.counter = 0
        
        # 시그널 핸들러 설정
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 센서 ID 풀
        self.equipment_ids = [f"EQ{i:03d}" for i in range(1, 21)]
        self.facility_ids = [f"FAC{i:03d}" for i in range(1, 6)]
        self.locations = [
            "Building1_Floor1", "Building1_Floor2", "Building1_Floor3",
            "Building2_Floor1", "Building2_Floor2", "Building2_Floor3",
            "Building3_Floor1", "Building3_Floor2"
        ]
        
        print(f"🚀 DataLake 데이터 생성기 시작")
        print(f"📡 API URL: {api_url}")
        print(f"⏱️  전송 주기: {interval}초")
        print(f"🛑 중지하려면 Ctrl+C를 누르세요")
        print("-" * 50)
    
    def signal_handler(self, signum, frame):
        """시그널 핸들러 - 안전한 종료"""
        print(f"\n🛑 시그널 {signum} 수신, 종료 중...")
        self.running = False
    
    def generate_normal_data(self) -> Dict:
        """정상 센서 데이터 생성"""
        self.counter += 1
        
        # 기본 데이터
        data = {
            "equipment_id": random.choice(self.equipment_ids),
            "facility_id": random.choice(self.facility_ids),
            "equipment_location": random.choice(self.locations),
            "measured_at": datetime.utcnow().isoformat() + "Z",
            "temperature": round(random.uniform(20.0, 30.0), 2),
            "humidity": round(random.uniform(40.0, 70.0), 2),
            "smoke_density": round(random.uniform(0.001, 0.050), 4),
            "co_level": round(random.uniform(0.001, 0.020), 4),
            "gas_level": round(random.uniform(0.001, 0.030), 4),
            "metadata": {
                "test": True,
                "batch": self.counter,
                "generator": "data_generator.py"
            }
        }
        
        return data
    
    def generate_anomaly_data(self, anomaly_type: str = None) -> Dict:
        """이상치 데이터 생성"""
        if anomaly_type is None:
            anomaly_type = random.choice(['temperature', 'smoke', 'co'])
        
        base_data = self.generate_normal_data()
        
        if anomaly_type == 'temperature':
            # 온도 이상치 (85-95°C)
            base_data['temperature'] = round(random.uniform(85.0, 95.0), 2)
            base_data['metadata']['anomaly'] = 'temperature'
            base_data['metadata']['severity'] = 'high'
            
        elif anomaly_type == 'smoke':
            # 연기 이상치 (600-800 ppm)
            base_data['smoke_density'] = round(random.uniform(600.0, 800.0), 2)
            base_data['metadata']['anomaly'] = 'smoke'
            base_data['metadata']['severity'] = 'critical'
            
        elif anomaly_type == 'co':
            # CO 이상치 (250-300 ppm)
            base_data['co_level'] = round(random.uniform(250.0, 300.0), 2)
            base_data['metadata']['anomaly'] = 'co'
            base_data['metadata']['severity'] = 'critical'
        
        return base_data
    
    def send_data(self, data: Dict) -> bool:
        """데이터를 API에 전송"""
        try:
            response = requests.post(
                f"{self.api_url}/ingest",
                json=data,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                return True
            else:
                print(f"❌ 데이터 전송 실패: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 네트워크 오류: {e}")
            return False
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return False
    
    def run(self, anomaly_ratio: float = 0.1):
        """메인 실행 루프"""
        print(f"📊 이상치 비율: {anomaly_ratio * 100:.1f}%")
        print(f"🔄 데이터 전송 시작...")
        print("-" * 50)
        
        while self.running:
            try:
                # 이상치 데이터 생성 여부 결정
                if random.random() < anomaly_ratio:
                    anomaly_type = random.choice(['temperature', 'smoke', 'co'])
                    data = self.generate_anomaly_data(anomaly_type)
                    data_type = f"🚨 {anomaly_type.upper()} 이상치"
                else:
                    data = self.generate_normal_data()
                    data_type = "✅ 정상"
                
                # 데이터 전송
                if self.send_data(data):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {data_type} | {data['equipment_id']} | "
                          f"온도: {data['temperature']}°C | "
                          f"연기: {data['smoke_density']:.4f} | "
                          f"CO: {data['co_level']:.4f}")
                else:
                    print(f"❌ 데이터 전송 실패: {data['equipment_id']}")
                
                # 카운터 업데이트
                if self.counter % 10 == 0:
                    print(f"📈 총 전송된 데이터: {self.counter}개")
                
                # 대기
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 루프 오류: {e}")
                time.sleep(1)
        
        print(f"\n🏁 데이터 생성기 종료")
        print(f"📊 총 전송된 데이터: {self.counter}개")

def main():
    parser = argparse.ArgumentParser(description="DataLake 데이터 생성기")
    parser.add_argument("--api-url", default="http://localhost:8084", 
                       help="DataLake API URL (기본값: http://localhost:8084)")
    parser.add_argument("--interval", type=float, default=2.0,
                       help="데이터 전송 주기 (초, 기본값: 2.0)")
    parser.add_argument("--anomaly-ratio", type=float, default=0.1,
                       help="이상치 데이터 비율 (0.0-1.0, 기본값: 0.1)")
    parser.add_argument("--count", type=int, default=None,
                       help="전송할 데이터 개수 (기본값: 무한)")
    
    args = parser.parse_args()
    
    # 유효성 검사
    if args.interval < 0.1:
        print("❌ 전송 주기는 0.1초 이상이어야 합니다.")
        sys.exit(1)
    
    if not (0.0 <= args.anomaly_ratio <= 1.0):
        print("❌ 이상치 비율은 0.0-1.0 사이여야 합니다.")
        sys.exit(1)
    
    # 데이터 생성기 시작
    generator = DataGenerator(args.api_url, args.interval)
    
    try:
        if args.count:
            print(f"🎯 목표: {args.count}개 데이터 전송")
            # 지정된 개수만큼만 실행
            for i in range(args.count):
                if not generator.running:
                    break
                    
                if random.random() < args.anomaly_ratio:
                    anomaly_type = random.choice(['temperature', 'smoke', 'co'])
                    data = generator.generate_anomaly_data(anomaly_type)
                    data_type = f"🚨 {anomaly_type.upper()} 이상치"
                else:
                    data = generator.generate_normal_data()
                    data_type = "✅ 정상"
                
                if generator.send_data(data):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {data_type} | {data['equipment_id']} | "
                          f"온도: {data['temperature']}°C | "
                          f"연기: {data['smoke_density']:.4f} | "
                          f"CO: {data['co_level']:.4f}")
                
                if i < args.count - 1:  # 마지막 데이터가 아니면 대기
                    time.sleep(args.interval)
        else:
            # 무한 실행
            generator.run(args.anomaly_ratio)
            
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단됨")
    finally:
        print(f"📊 총 전송된 데이터: {generator.counter}개")

if __name__ == "__main__":
    main()
