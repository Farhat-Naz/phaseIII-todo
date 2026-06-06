# AWS Lambda Deployment using Docker (for Python 3.11 compatibility)

Write-Host "Creating Lambda deployment package using Docker..." -ForegroundColor Green

# Clean up previous builds
if (Test-Path "deployment.zip") {
    Remove-Item "deployment.zip"
}
if (Test-Path "lambda-package") {
    Remove-Item -Recurse -Force "lambda-package"
}

# Create package directory
New-Item -ItemType Directory -Path "lambda-package" | Out-Null

# Copy application files
Write-Host "Copying application files..." -ForegroundColor Yellow
Copy-Item -Recurse -Path "app" -Destination "lambda-package/app"
Copy-Item "lambda_handler.py" -Destination "lambda-package/"
Copy-Item "index.py" -Destination "lambda-package/"
Copy-Item "requirements.txt" -Destination "lambda-package/"

# Use Docker to install dependencies with Python 3.11
Write-Host "Installing dependencies using Docker (Python 3.11)..." -ForegroundColor Yellow
docker run --rm -v "${PWD}/lambda-package:/var/task" public.ecr.aws/lambda/python:3.11 pip install -r /var/task/requirements.txt -t /var/task/

# Remove requirements.txt from package
Remove-Item "lambda-package/requirements.txt"

# Create ZIP
Write-Host "Creating deployment.zip..." -ForegroundColor Yellow
Set-Location lambda-package
Compress-Archive -Path * -DestinationPath "../deployment.zip" -Force
Set-Location ..

# Cleanup
Remove-Item -Recurse -Force lambda-package

$size = (Get-Item deployment.zip).Length / 1MB
Write-Host "`n✓ Deployment package created: deployment.zip" -ForegroundColor Green
Write-Host "✓ Size: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan

Write-Host "`n=== Next Steps ===" -ForegroundColor Yellow
Write-Host "1. Open AWS Lambda Console:"
Write-Host "   https://eu-north-1.console.aws.amazon.com/lambda/home?region=eu-north-1#/create/function" -ForegroundColor Cyan
Write-Host "`n2. Create Function:"
Write-Host "   - Choose: 'Author from scratch'"
Write-Host "   - Function name: todo-api"
Write-Host "   - Runtime: Python 3.11"
Write-Host "   - Click 'Create function'"
Write-Host "`n3. Upload Code:"
Write-Host "   - In 'Code' tab, click 'Upload from' > '.zip file'"
Write-Host "   - Upload: deployment.zip"
Write-Host "`n4. Configure Runtime:"
Write-Host "   - Click 'Runtime settings' > 'Edit'"
Write-Host "   - Handler: lambda_handler.handler"
Write-Host "   - Save"
Write-Host "`n5. Add Environment Variables:"
Write-Host "   - Go to 'Configuration' > 'Environment variables'"
Write-Host "   - Click 'Edit' and add from your .env file:"
Write-Host "     DATABASE_URL, SECRET_KEY, REFRESH_TOKEN_SECRET, etc."
Write-Host "`n6. Increase Timeout:"
Write-Host "   - Go to 'Configuration' > 'General configuration'"
Write-Host "   - Edit: Timeout to 30 seconds"
Write-Host "   - Memory to 512 MB"
Write-Host "`n7. Create API Gateway:"
Write-Host "   - Click 'Add trigger'"
Write-Host "   - Select 'API Gateway'"
Write-Host "   - Create new REST API"
Write-Host "   - Security: Open"
Write-Host "   - Click 'Add'"
Write-Host "`n8. Get your API URL from the trigger configuration"
Write-Host "`nDeployment package ready! Follow the steps above." -ForegroundColor Green
