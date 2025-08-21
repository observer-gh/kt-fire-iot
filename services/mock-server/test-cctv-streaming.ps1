Write-Host "🚀 CCTV 스트리밍 기능 테스트 시작" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# 서버 상태 확인
Write-Host "1. 서버 상태 확인 중..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/actuator/health" -Method Get -ErrorAction Stop
    Write-Host "✅ 서버가 정상적으로 실행 중입니다." -ForegroundColor Green
} catch {
    Write-Host "❌ 서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요." -ForegroundColor Red
}

Write-Host ""

# 사용 가능한 비디오 목록 확인
Write-Host "2. 사용 가능한 비디오 목록 확인 중..." -ForegroundColor Yellow
try {
    $videos = Invoke-RestMethod -Uri "http://localhost:8001/api/cctv/videos" -Method Get
    Write-Host "사용 가능한 비디오:" -ForegroundColor Cyan
    $videos | ForEach-Object { Write-Host "   - $_" -ForegroundColor White }
} catch {
    Write-Host "❌ 비디오 목록을 가져올 수 없습니다." -ForegroundColor Red
}

Write-Host ""

# 스트리밍 상태 확인
Write-Host "3. 스트리밍 상태 확인 중..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "http://localhost:8001/api/cctv/stream/status" -Method Get
    Write-Host "스트리밍 상태: $($status.streaming)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ 스트리밍 상태를 확인할 수 없습니다." -ForegroundColor Red
}

Write-Host ""
Write-Host "4. 테스트 페이지 접속:" -ForegroundColor Yellow
Write-Host "   http://localhost:8001/cctv-streaming.html" -ForegroundColor Cyan

Write-Host ""
Write-Host "5. WebSocket 연결 테스트:" -ForegroundColor Yellow
Write-Host "   ws://localhost:8001/cctv-websocket" -ForegroundColor Cyan

Write-Host ""
Write-Host "✅ 테스트 완료!" -ForegroundColor Green
Write-Host "브라우저에서 테스트 페이지에 접속하여 실제 스트리밍을 확인해보세요." -ForegroundColor White
