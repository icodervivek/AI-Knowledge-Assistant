# Triggers a full re-index of all documents via the API

$apiKey = "ai-knowledge-assistant-secret-2026"
$url = "http://localhost:8000/reindex"

Write-Host "Triggering re-index..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri $url -Method POST -Headers @{ "X-API-Key" = $apiKey } -ContentType "application/json"
    Write-Host ""
    Write-Host "Re-index complete!" -ForegroundColor Green
    Write-Host "  Files indexed  : $($response.files_indexed)" -ForegroundColor White
    Write-Host "  Chunks indexed : $($response.chunks_indexed)" -ForegroundColor White
} catch {
    Write-Host ""
    Write-Host "Re-index failed. Is the backend running?" -ForegroundColor Red
    Write-Host "Start it with: make run" -ForegroundColor Yellow
}
