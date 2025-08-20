#!/bin/bash

echo "🚀 CCTV 스트리밍 기능 테스트 시작"
echo "=================================="

# 서버 상태 확인
echo "1. 서버 상태 확인 중..."
curl -s http://localhost:8080/actuator/health || echo "서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요."

echo ""
echo "2. 사용 가능한 비디오 목록 확인 중..."
curl -s http://localhost:8080/api/cctv/videos | jq '.' 2>/dev/null || curl -s http://localhost:8080/api/cctv/videos

echo ""
echo "3. 스트리밍 상태 확인 중..."
curl -s http://localhost:8080/api/cctv/stream/status | jq '.' 2>/dev/null || curl -s http://localhost:8080/api/cctv/stream/status

echo ""
echo "4. 테스트 페이지 접속:"
echo "   http://localhost:8080/cctv-streaming.html"
echo ""
echo "5. WebSocket 연결 테스트:"
echo "   ws://localhost:8080/cctv-websocket"

echo ""
echo "✅ 테스트 완료!"
echo "브라우저에서 테스트 페이지에 접속하여 실제 스트리밍을 확인해보세요."
