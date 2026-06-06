# Generate Secret Keys for .env file
# .env فائل کے لیے خفیہ کلیدیں بنائیں
# .env file ke liye khufia klidein banayein

Write-Host "`n=== Todo App Secret Keys Generator ===" -ForegroundColor Cyan
Write-Host "=== Todo App خفیہ کلیدیں بنانے والا ===" -ForegroundColor Cyan
Write-Host ""

# Function to generate a random secret key
function Generate-SecretKey {
    param(
        [int]$Length = 64
    )

    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    $key = -join ((1..$Length) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
    return $key
}

# Generate SECRET_KEY
Write-Host "Generating SECRET_KEY..." -ForegroundColor Yellow
Write-Host "SECRET_KEY بنا رہے ہیں..." -ForegroundColor Yellow
$secretKey = Generate-SecretKey -Length 64
Write-Host "SECRET_KEY=$secretKey" -ForegroundColor Green
Write-Host ""

# Generate REFRESH_TOKEN_SECRET
Write-Host "Generating REFRESH_TOKEN_SECRET..." -ForegroundColor Yellow
Write-Host "REFRESH_TOKEN_SECRET بنا رہے ہیں..." -ForegroundColor Yellow
$refreshTokenSecret = Generate-SecretKey -Length 64
Write-Host "REFRESH_TOKEN_SECRET=$refreshTokenSecret" -ForegroundColor Green
Write-Host ""

# Display instructions
Write-Host "=== Instructions | ہدایات ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Copy these keys to your backend/.env file" -ForegroundColor White
Write-Host "   ان کلیدوں کو اپنی backend/.env فائل میں نقل کریں" -ForegroundColor White
Write-Host ""
Write-Host "2. NEVER commit .env file to Git" -ForegroundColor Red
Write-Host "   .env فائل کبھی Git میں جمع نہ کریں" -ForegroundColor Red
Write-Host ""
Write-Host "3. Keep these keys secure and private" -ForegroundColor White
Write-Host "   ان کلیدوں کو محفوظ اور نجی رکھیں" -ForegroundColor White
Write-Host ""

# Ask if user wants to save to file
$save = Read-Host "Save to .env.generated file? (y/n) | .env.generated فائل میں محفوظ کریں؟ (y/n)"

if ($save -eq 'y' -or $save -eq 'Y') {
    $envContent = @"
# Generated Secret Keys - $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# Copy these to your backend/.env file
# ان کو اپنی backend/.env فائل میں نقل کریں

SECRET_KEY=$secretKey
REFRESH_TOKEN_SECRET=$refreshTokenSecret

# Remember to also add:
# یاد رکھیں کہ یہ بھی شامل کریں:

# DATABASE_URL=postgresql://username:password@host/database?sslmode=require
# CORS_ORIGINS=*
# EMAIL_PROVIDER=sendgrid
# SENDGRID_API_KEY=your-key-here
# EMAIL_FROM_ADDRESS=noreply@yourdomain.com
# FRONTEND_URL=http://localhost:3000
# OPENAI_API_KEY=your-key-here
"@

    $envContent | Out-File -FilePath ".env.generated" -Encoding UTF8
    Write-Host "`nKeys saved to .env.generated" -ForegroundColor Green
    Write-Host "کلیدیں .env.generated میں محفوظ ہو گئیں" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Rename to .env and add other required variables" -ForegroundColor Yellow
    Write-Host "اہم: .env میں نام تبدیل کریں اور دیگر ضروری متغیرات شامل کریں" -ForegroundColor Yellow
}

Write-Host "`nDone! | مکمل!" -ForegroundColor Green
Write-Host ""
