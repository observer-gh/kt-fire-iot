#!/usr/bin/env python3
"""
Mock Server 연동 테스트 스크립트
DataLake가 Mock Server에서 데이터를 가져와서 처리하는지 테스트합니다.
"""

import asyncio
import httpx
import json
from datetime import datetime

# DataLake API 설정
DATALAKE_BASE_URL = "http://localhost:8080"
MOCK_SERVER_BASE_URL = "http://localhost:8081"

async def test_mock_server_health():
    """Mock Server 상태 확인"""
    print("🔍 Mock Server 상태 확인 중...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MOCK_SERVER_BASE_URL}/mock/realtime-generator/generate/health-check")
            if response.status_code == 200:
                print("✅ Mock Server 정상 동작")
                return True
            else:
                print(f"❌ Mock Server 오류: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Mock Server 연결 실패: {e}")
        return False

async def test_datalake_health():
    """DataLake 상태 확인"""
    print("🔍 DataLake 상태 확인 중...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DATALAKE_BASE_URL}/healthz")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ DataLake 정상 동작")
                print(f"   - Redis: {data.get('redis', 'unknown')}")
                print(f"   - Mock Server: {data.get('mock_server', 'unknown')}")
                return True
            else:
                print(f"❌ DataLake 오류: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ DataLake 연결 실패: {e}")
        return False

async def test_mock_data_generation():
    """Mock Server에서 데이터 생성 테스트"""
    print("🔍 Mock Server 데이터 생성 테스트 중...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Datalake용 데이터 생성
            response = await client.get(f"{MOCK_SERVER_BASE_URL}/mock/realtime-generator/datalake/generate", params={"count": 5})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Mock Server에서 {len(data)}개의 데이터 생성됨")
                
                # 첫 번째 데이터 샘플 출력
                if data:
                    sample = data[0]
                    print(f"   샘플 데이터: {sample.get('equipment_id')} - 온도: {sample.get('temperature')}°C")
                return True
            else:
                print(f"❌ Mock Server 데이터 생성 실패: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Mock Server 데이터 생성 테스트 실패: {e}")
        return False

async def test_datalake_ingest():
    """DataLake ingest API 테스트"""
    print("🔍 DataLake ingest API 테스트 중...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Mock Server에서 데이터를 가져와서 처리
            response = await client.post(f"{DATALAKE_BASE_URL}/ingest")
            if response.status_code in [200, 204]:
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 이상치 탐지됨: {data.get('equipment_id')} - {data.get('metric')} = {data.get('value')}")
                else:
                    print("✅ 정상 데이터 처리 완료 (204 No Content)")
                return True
            else:
                print(f"❌ DataLake ingest 실패: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ DataLake ingest 테스트 실패: {e}")
        return False

async def test_mock_scheduler_status():
    """Mock Scheduler 상태 확인"""
    print("🔍 Mock Scheduler 상태 확인 중...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DATALAKE_BASE_URL}/mock-scheduler/status")
            if response.status_code == 200:
                data = response.json()
                is_running = data.get('status', {}).get('is_running', False)
                polling_interval = data.get('status', {}).get('polling_interval_seconds', 0)
                mock_server_url = data.get('mock_server_url', 'unknown')
                
                print(f"✅ Mock Scheduler 상태: {'실행 중' if is_running else '중지됨'}")
                print(f"   - 폴링 간격: {polling_interval}초")
                print(f"   - Mock Server URL: {mock_server_url}")
                
                # 5초 간격인지 확인
                if polling_interval == 5:
                    print("   ✅ 폴링 간격이 5초로 올바르게 설정됨")
                else:
                    print(f"   ⚠️  폴링 간격이 5초가 아님 (현재: {polling_interval}초)")
                
                return True
            else:
                print(f"❌ Mock Scheduler 상태 확인 실패: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Mock Scheduler 상태 확인 테스트 실패: {e}")
        return False

async def test_manual_trigger():
    """수동 트리거 테스트"""
    print("🔍 수동 트리거 테스트 중...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{DATALAKE_BASE_URL}/trigger-mock-data-process")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 수동 트리거 성공: {data.get('message', '')}")
                return True
            else:
                print(f"❌ 수동 트리거 실패: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 수동 트리거 테스트 실패: {e}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🚀 Mock Server 연동 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("Mock Server 상태 확인", test_mock_server_health),
        ("DataLake 상태 확인", test_datalake_health),
        ("Mock Server 데이터 생성", test_mock_data_generation),
        ("Mock Scheduler 상태 확인", test_mock_scheduler_status),
        ("DataLake ingest API", test_datalake_ingest),
        ("수동 트리거 테스트", test_manual_trigger),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️  일부 테스트 실패. 설정을 확인해주세요.")

if __name__ == "__main__":
    asyncio.run(main())
