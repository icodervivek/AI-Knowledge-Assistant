# Starts backend and frontend in separate terminal windows

Write-Host "Starting AI Knowledge Assistant..." -ForegroundColor Cyan

# Start backend
Write-Host "Starting backend on http://localhost:8000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'D:\desk26\AI Knowledge Assistant\server'; .\venv\Scripts\activate; uvicorn api.main:app --reload"

# Wait for backend to be ready
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting frontend on http://localhost:3000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'D:\desk26\AI Knowledge Assistant\client'; npm run dev"

Write-Host ""
Write-Host "App is starting up:" -ForegroundColor Cyan
Write-Host "  Backend  -> http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend -> http://localhost:3000" -ForegroundColor White
Write-Host "  API Docs -> http://localhost:8000/docs" -ForegroundColor White
