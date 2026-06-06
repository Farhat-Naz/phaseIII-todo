# Upload large deployment package to Lambda via S3

$bucketName = "todo-api-deployment-$(Get-Random -Maximum 99999)"
$region = "ap-south-1"
$functionName = "todo-api"
$zipFile = "C:\Users\aasif\Desktop\deployment.zip"

Write-Host "Uploading deployment package to Lambda via S3..." -ForegroundColor Green

# Check if file exists
if (-not (Test-Path $zipFile)) {
    Write-Host "Error: deployment.zip not found at $zipFile" -ForegroundColor Red
    exit 1
}

# Step 1: Create S3 bucket
Write-Host "`nStep 1: Creating S3 bucket: $bucketName" -ForegroundColor Yellow
aws s3 mb s3://$bucketName --region $region

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error creating bucket. Make sure AWS credentials are set." -ForegroundColor Red
    exit 1
}

# Step 2: Upload ZIP to S3
Write-Host "`nStep 2: Uploading deployment.zip to S3..." -ForegroundColor Yellow
aws s3 cp $zipFile s3://$bucketName/deployment.zip --region $region

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error uploading to S3." -ForegroundColor Red
    exit 1
}

# Step 3: Update Lambda function from S3
Write-Host "`nStep 3: Updating Lambda function code from S3..." -ForegroundColor Yellow
aws lambda update-function-code --function-name $functionName --s3-bucket $bucketName --s3-key deployment.zip --region $region

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error updating Lambda function." -ForegroundColor Red
    exit 1
}

Write-Host "`nDeployment Complete!" -ForegroundColor Green
Write-Host "Test your API: https://YOUR_API_URL/health" -ForegroundColor Cyan
Write-Host "`nS3 bucket created: $bucketName (you can delete it later)" -ForegroundColor Yellow
