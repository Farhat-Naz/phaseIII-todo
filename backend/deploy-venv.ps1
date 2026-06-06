# Deploy using existing virtual environment dependencies

Write-Host "Creating Lambda package from virtual environment..." -ForegroundColor Green

# Clean up
if (Test-Path "deployment.zip") { Remove-Item "deployment.zip" }
if (Test-Path "lambda-package") { Remove-Item -Recurse -Force "lambda-package" }

# Create package directory
New-Item -ItemType Directory -Path "lambda-package" | Out-Null

# Copy site-packages from virtual environment
Write-Host "Copying Python packages from virtual environment..." -ForegroundColor Yellow
$venvPath = "D:\quarterr 4\phaseII-todo\.venv\Lib\site-packages"

if (Test-Path $venvPath) {
    # Copy all packages except __pycache__ and .dist-info
    Get-ChildItem $venvPath | Where-Object {
        $_.Name -notmatch '__pycache__|\.dist-info|\.egg-info|^pip|^setuptools|^wheel'
    } | ForEach-Object {
        Copy-Item $_.FullName -Destination "lambda-package\" -Recurse -Force
    }
} else {
    Write-Host "Virtual environment not found at: $venvPath" -ForegroundColor Red
    Write-Host "Please start Docker and use deploy-docker.ps1 instead" -ForegroundColor Yellow
    exit 1
}

# Copy application files
Write-Host "Copying application files..." -ForegroundColor Yellow
Copy-Item -Recurse -Path "app" -Destination "lambda-package/app" -Force
Copy-Item "lambda_handler.py" -Destination "lambda-package/" -Force
Copy-Item "index.py" -Destination "lambda-package/" -Force

# Create ZIP
Write-Host "Creating deployment.zip..." -ForegroundColor Yellow
Set-Location lambda-package
Compress-Archive -Path * -DestinationPath "../deployment.zip" -Force
Set-Location ..

# Cleanup
Remove-Item -Recurse -Force lambda-package

$size = (Get-Item deployment.zip).Length / 1MB
Write-Host "`n✓ Deployment package created!" -ForegroundColor Green
Write-Host "✓ Size: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
Write-Host "`nReady to upload to AWS Lambda!" -ForegroundColor Green
