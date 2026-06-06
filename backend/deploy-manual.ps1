# Manual AWS Lambda Deployment Script
# This creates a deployment package for AWS Lambda

Write-Host "Creating Lambda deployment package..." -ForegroundColor Green

# Create temp directory for package
$packageDir = "lambda-package"
if (Test-Path $packageDir) {
    Remove-Item -Recurse -Force $packageDir
}
New-Item -ItemType Directory -Path $packageDir | Out-Null

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt -t $packageDir --platform manylinux2014_x86_64 --only-binary=:all:

# Copy application files
Write-Host "Copying application files..." -ForegroundColor Yellow
Copy-Item -Recurse -Path "app" -Destination "$packageDir/app"
Copy-Item "lambda_handler.py" -Destination "$packageDir/"
Copy-Item "index.py" -Destination "$packageDir/"

# Create ZIP file
Write-Host "Creating deployment.zip..." -ForegroundColor Yellow
Set-Location $packageDir
Compress-Archive -Path * -DestinationPath "../deployment.zip" -Force
Set-Location ..

# Cleanup
Remove-Item -Recurse -Force $packageDir

Write-Host "`nDeployment package created: deployment.zip" -ForegroundColor Green
Write-Host "Size: $((Get-Item deployment.zip).Length / 1MB) MB" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Go to AWS Lambda Console: https://eu-north-1.console.aws.amazon.com/lambda/home?region=eu-north-1#/functions"
Write-Host "2. Click 'Create function'"
Write-Host "3. Choose 'Author from scratch'"
Write-Host "4. Function name: todo-api"
Write-Host "5. Runtime: Python 3.11"
Write-Host "6. Create function"
Write-Host "7. Upload deployment.zip"
Write-Host "8. Set handler to: lambda_handler.handler"
Write-Host "9. Add environment variables from .env file"
Write-Host "10. Create API Gateway trigger"
