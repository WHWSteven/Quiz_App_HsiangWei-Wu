# Windows PowerShell Script to Start All Services
# Run this script to start all services needed for Saga Orchestration

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Saga Orchestration Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Check if Redis is running
Write-Host "Checking Redis..." -ForegroundColor Green
try {
    $redisTest = redis-cli ping 2>&1
    if ($redisTest -match "PONG") {
        Write-Host "✓ Redis is running" -ForegroundColor Green
    } else {
        Write-Host "✗ Redis is not running" -ForegroundColor Red
        Write-Host "Please start Redis first:" -ForegroundColor Yellow
        Write-Host "  Option 1: redis-server" -ForegroundColor Yellow
        Write-Host "  Option 2: docker run -d -p 6379:6379 --name redis redis:latest" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to continue anyway..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
} catch {
    Write-Host "✗ Redis CLI not found. Make sure Redis is installed and running." -ForegroundColor Red
    Write-Host "Press any key to continue anyway..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Check if eventlet is installed
Write-Host "Checking dependencies..." -ForegroundColor Green
$eventlet = pip show eventlet 2>&1
if ($eventlet -match "Name: eventlet") {
    Write-Host "✓ eventlet is installed" -ForegroundColor Green
} else {
    Write-Host "Installing eventlet..." -ForegroundColor Yellow
    pip install eventlet
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service Startup Instructions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You need to open 6 separate PowerShell terminals:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Terminal 1 - Redis:" -ForegroundColor Cyan
Write-Host "  redis-server" -ForegroundColor White
Write-Host "  OR: docker run -d -p 6379:6379 --name redis redis:latest" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 - Celery Worker:" -ForegroundColor Cyan
Write-Host "  cd `"$PWD`"" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  celery -A saga_orchestrator.celery_app worker --loglevel=info --pool=eventlet" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 3 - Saga Orchestrator:" -ForegroundColor Cyan
Write-Host "  cd `"$PWD`"" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python saga_orchestrator/run_orchestrator.py" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 4 - User Service:" -ForegroundColor Cyan
Write-Host "  cd `"$PWD`"" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  cd user_service" -ForegroundColor White
Write-Host "  python app.py" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 5 - Quiz Service:" -ForegroundColor Cyan
Write-Host "  cd `"$PWD`"" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python run.py" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 6 - Gateway:" -ForegroundColor Cyan
Write-Host "  cd `"$PWD\gateway`"" -ForegroundColor White
Write-Host "  npm start" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quick Test Commands" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "After starting all services, test with:" -ForegroundColor Yellow
Write-Host "  curl http://localhost:5002/health  # Saga Orchestrator" -ForegroundColor White
Write-Host "  curl http://localhost:5001/health  # User Service" -ForegroundColor White
Write-Host "  curl http://localhost:5000/api/health  # Quiz Service" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see: WINDOWS_SETUP.md" -ForegroundColor Green
Write-Host ""
