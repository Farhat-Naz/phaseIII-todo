# Build deployment package for AWS Lambda

Write-Host "Building Lambda deployment package..." -ForegroundColor Green

# Clean up previous builds
if (Test-Path "package") { Remove-Item -Recurse -Force "package" }
if (Test-Path "deployment-new.zip") { Remove-Item "deployment-new.zip" }

# Create package directory
New-Item -ItemType Directory -Path "package" | Out-Null

# Install dependencies
Write-Host "`nInstalling Python dependencies..." -ForegroundColor Yellow
# Use system Python (Python314)
& "C:\Users\aasif\AppData\Local\Programs\Python\Python314\python.exe" -m pip install -r requirements.txt -t package --upgrade 2>&1 | Out-Host

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error installing dependencies" -ForegroundColor Red
    exit 1
}

# Copy application code
Write-Host "`nCopying application code..." -ForegroundColor Yellow
Copy-Item -Recurse -Path "app" -Destination "package/app" -Force
Copy-Item "lambda_handler.py" -Destination "package/" -Force
Copy-Item "index.py" -Destination "package/" -Force

# Create ZIP
Write-Host "`nCreating deployment package..." -ForegroundColor Yellow
Set-Location package
Compress-Archive -Path * -DestinationPath "../deployment-new.zip" -Force
Set-Location ..

# Cleanup
Remove-Item -Recurse -Force package

$size = (Get-Item deployment-new.zip).Length / 1MB
Write-Host "`n✓ Deployment package created: deployment-new.zip" -ForegroundColor Green
Write-Host "✓ Size: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
Write-Host "`nRename to deployment.zip and redeploy with: serverless deploy" -ForegroundColor Yellow
