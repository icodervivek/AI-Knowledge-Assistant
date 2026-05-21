# Runs the evaluation report and opens the output chart

Write-Host "Running evaluation report..." -ForegroundColor Cyan

$serverPath = "D:\desk26\AI Knowledge Assistant\server"
$python = "$serverPath\venv\Scripts\python.exe"
$script = "$serverPath\tools\eval_report.py"
$output = "$serverPath\exports\eval_report.png"

try {
    & $python $script

    if (Test-Path $output) {
        Write-Host ""
        Write-Host "Report saved to: $output" -ForegroundColor Green
        Write-Host "Opening chart..." -ForegroundColor Cyan
        Start-Process $output
    }
} catch {
    Write-Host "Eval failed: $_" -ForegroundColor Red
}
