# AWS پر Todo App کی خودکار تعیناتی کی مکمل رہنمائی
# AWS par Todo App ki Khudkar Tainaati ki Mukammal Rahnumai

---

## شروعات سے پہلے ضروری باتیں | Shuruat se Pehle Zaroori Batein

آپ کو یہ چیزیں تیار کرنی ہوں گی:
Aap ko ye cheezein tayyar karni hongi:

1. **AWS اکاؤنٹ** (مفت ٹائر دستیاب ہے)
   - **AWS Account** (muft tier dastyab hai)

2. **GitHub اکاؤنٹ** (frontend کے لیے)
   - **GitHub Account** (frontend ke liye)

3. **Neon PostgreSQL Database** (مفت ٹائر)
   - https://neon.tech پر جائیں اور database بنائیں
   - https://neon.tech par jayein aur database banayein
   - Connection string محفوظ رکھیں
   - Connection string mehfooz rakhein

4. **SendGrid اکاؤنٹ** (ای میل کے لیے، اختیاری)
   - **SendGrid Account** (email ke liye, ikhtiyari)
   - مفت ٹائر 100 emails/day دیتا ہے
   - Muft tier 100 emails/day deta hai

5. **OpenAI API Key** (چیٹ بوٹ کے لیے، اختیاری)
   - **OpenAI API Key** (chatbot ke liye, ikhtiyari)

---

## حصہ اول: Backend کی تعیناتی (AWS Lambda)
## Hissa Awwal: Backend ki Tainaati (AWS Lambda)

### قدم 1: AWS CLI انسٹال اور کنفیگر کریں
### Qadam 1: AWS CLI Install aur Configure karein

```powershell
# AWS CLI ڈاؤن لوڈ کریں
# AWS CLI download karein
# https://awscli.amazonaws.com/AWSCLIV2.msi

# انسٹالیشن کے بعد تصدیق کریں
# Installation ke baad tasdeeq karein
aws --version
```

**AWS Credentials کنفیگر کریں:**
**AWS Credentials configure karein:**

```powershell
aws configure
```

یہ معلومات درج کریں:
Ye maloomat darj karein:

- **AWS Access Key ID**: آپ کا access key (AWS Console > IAM > Users > Security credentials)
- **AWS Secret Access Key**: آپ کا secret key
- **Default region name**: `ap-south-1` (ممبئی)
- **Default output format**: `json`

---

### قدم 2: Serverless Framework انسٹال کریں
### Qadam 2: Serverless Framework Install karein

```powershell
# Node.js کی ضرورت ہے (پہلے سے انسٹال ہونا چاہیے)
# Node.js ki zaroorat hai (pehle se install hona chahiye)
node --version
npm --version

# Serverless Framework globally انسٹال کریں
# Serverless Framework globally install karein
npm install -g serverless

# تصدیق کریں
# Tasdeeq karein
serverless --version
```

---

### قدم 3: Serverless Plugin انسٹال کریں
### Qadam 3: Serverless Plugin Install karein

```powershell
# اپنے پراجیکٹ فولڈر میں جائیں
# Apne project folder mein jayein
cd "D:\quarterr 4\phaseIII-todoapp"

# Plugin انسٹال کریں
# Plugin install karein
npm install --save-dev serverless-python-requirements
```

---

### قدم 4: Backend کے لیے .env فائل بنائیں
### Qadam 4: Backend ke liye .env file banayein

**اہم:** یہ فائل `backend` فولڈر میں بنانی ہے
**Ahem:** Ye file `backend` folder mein banani hai

```powershell
# backend فولڈر میں جائیں
# backend folder mein jayein
cd backend

# .env فائل بنائیں (notepad یا کسی editor میں)
# .env file banayein (notepad ya kisi editor mein)
notepad .env
```

**.env فائل میں یہ لکھیں:**
**.env file mein ye likhein:**

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host/database?sslmode=require

# Security Keys (نئی keys generate کریں)
# Security Keys (nayi keys generate karein)
SECRET_KEY=your-secret-key-here-use-random-64-chars
REFRESH_TOKEN_SECRET=your-refresh-token-secret-different-from-above

# JWT Configuration
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (پہلے * رکھیں، بعد میں update کریں گے)
# CORS (pehle * rakhein, baad mein update karenge)
CORS_ORIGINS=*

# Email Configuration (SendGrid)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your-sendgrid-api-key-here
EMAIL_FROM_ADDRESS=noreply@yourdomain.com
EMAIL_FROM_NAME=TodoApp

# Frontend URL (پہلے localhost رکھیں)
# Frontend URL (pehle localhost rakhein)
FRONTEND_URL=http://localhost:3000

# OpenAI Configuration (اختیاری - chatbot کے لیے)
# OpenAI Configuration (ikhtiyari - chatbot ke liye)
OPENAI_API_KEY=your-openai-api-key-here
AI_MODEL=gpt-4o

# Logging
LOG_LEVEL=INFO
```

---

### قدم 5: Secret Keys Generate کریں
### Qadam 5: Secret Keys Generate karein

**PowerShell میں random keys بنانے کے لیے:**
**PowerShell mein random keys banane ke liye:**

```powershell
# SECRET_KEY کے لیے
# SECRET_KEY ke liye
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})

# REFRESH_TOKEN_SECRET کے لیے (دوبارہ چلائیں، مختلف key چاہیے)
# REFRESH_TOKEN_SECRET ke liye (dobara chalayein, mukhtalif key chahiye)
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

ان keys کو copy کر کے .env فائل میں paste کریں
In keys ko copy kar ke .env file mein paste karein

---

### قدم 6: Database URL حاصل کریں
### Qadam 6: Database URL Hasil karein

1. https://neon.tech پر جائیں اور لاگ ان کریں
   - https://neon.tech par jayein aur log in karein

2. اپنا project کھولیں
   - Apna project kholein

3. **Connection String** تلاش کریں
   - **Connection String** talash karein
   - مثال: `postgresql://user:password@ep-xyz.ap-south-1.aws.neon.tech/mydb?sslmode=require`
   - Misal: `postgresql://user:password@ep-xyz.ap-south-1.aws.neon.tech/mydb?sslmode=require`

4. اس کو copy کر کے .env میں `DATABASE_URL` کی جگہ paste کریں
   - Is ko copy kar ke .env mein `DATABASE_URL` ki jagah paste karein

---

### قدم 7: SendGrid API Key حاصل کریں (اختیاری)
### Qadam 7: SendGrid API Key Hasil karein (Ikhtiyari)

اگر email بھیجنا چاہتے ہیں:
Agar email bhejna chahte hain:

1. https://sendgrid.com پر جائیں اور sign up کریں
   - https://sendgrid.com par jayein aur sign up karein

2. **Settings > API Keys** میں جائیں
   - **Settings > API Keys** mein jayein

3. **Create API Key** پر کلک کریں
   - **Create API Key** par click karein

4. Full Access دیں اور key generate کریں
   - Full Access dein aur key generate karein

5. Key کو محفوظ رکھیں (دوبارہ نہیں دکھائی دے گی)
   - Key ko mehfooz rakhein (dobara nahi dikhayi degi)

6. .env میں `SENDGRID_API_KEY` کی جگہ paste کریں
   - .env mein `SENDGRID_API_KEY` ki jagah paste karein

---

### قدم 8: Docker انسٹال کریں (ضروری)
### Qadam 8: Docker Install karein (Zaroori)

Serverless Framework کو Docker کی ضرورت ہے Python packages build کرنے کے لیے:
Serverless Framework ko Docker ki zaroorat hai Python packages build karne ke liye:

1. Docker Desktop ڈاؤن لوڈ کریں:
   - Docker Desktop download karein:
   - https://www.docker.com/products/docker-desktop/

2. انسٹال کریں اور چلائیں
   - Install karein aur chalayein

3. تصدیق کریں:
   - Tasdeeq karein:
   ```powershell
   docker --version
   ```

4. Docker Desktop کو چلنے دیں (system tray میں icon دیکھیں)
   - Docker Desktop ko chalne dein (system tray mein icon dekhein)

---

### قدم 9: Backend Deploy کریں
### Qadam 9: Backend Deploy karein

```powershell
# Backend فولڈر میں ہونا چاہیے
# Backend folder mein hona chahiye
cd backend

# Deploy کریں (پہلی بار 5-10 منٹ لگ سکتے ہیں)
# Deploy karein (pehli baar 5-10 minute lag sakte hain)
serverless deploy
```

**یہ کیا کرے گا:**
**Ye kya karega:**
- Lambda function بنائے گا
- API Gateway setup کرے گا
- IAM roles بنائے گا
- CloudFormation stack deploy کرے گا

**کامیابی کی علامت:**
**Kamyabi ki alamat:**
```
✔ Service deployed to stack todo-api-dev

endpoints:
  ANY - https://xxxxxxxxxx.execute-api.ap-south-1.amazonaws.com/dev
  ANY - https://xxxxxxxxxx.execute-api.ap-south-1.amazonaws.com/dev/{proxy+}

functions:
  api: todo-api-dev-api
```

**اہم:** API Gateway URL کو محفوظ رکھیں (endpoints کے نیچے والا URL)
**Ahem:** API Gateway URL ko mehfooz rakhein (endpoints ke neeche wala URL)

---

### قدم 10: Backend Test کریں
### Qadam 10: Backend Test karein

```powershell
# Health check endpoint test کریں
# Health check endpoint test karein
curl https://your-api-url.execute-api.ap-south-1.amazonaws.com/dev/health
```

**صحیح response:**
**Sahih response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

---

## حصہ دوم: Frontend کی تعیناتی (AWS Amplify)
## Hissa Dovom: Frontend ki Tainaati (AWS Amplify)

### قدم 11: Code کو GitHub پر Push کریں
### Qadam 11: Code ko GitHub par Push karein

اگر پہلے سے GitHub پر نہیں ہے:
Agar pehle se GitHub par nahi hai:

```powershell
# Main folder میں جائیں
# Main folder mein jayein
cd "D:\quarterr 4\phaseIII-todoapp"

# Git repository initialize کریں (اگر نہیں ہے)
# Git repository initialize karein (agar nahi hai)
git init

# تمام files add کریں
# Tamam files add karein
git add .

# Commit بنائیں
# Commit banayein
git commit -m "feat: Add Todo App with AWS deployment configuration"

# GitHub پر repository بنائیں
# GitHub par repository banayein
# https://github.com/new پر جائیں
# Repository name: phaseIII-todoapp
# Public یا Private (آپ کی مرضی)

# Remote add کریں
# Remote add karein
git remote add origin https://github.com/your-username/phaseIII-todoapp.git

# Push کریں
# Push karein
git branch -M main
git push -u origin main
```

---

### قدم 12: AWS Amplify Console میں جائیں
### Qadam 12: AWS Amplify Console mein jayein

1. AWS Console میں لاگ ان کریں
   - AWS Console mein log in karein
   - https://console.aws.amazon.com/

2. **Services** میں **AWS Amplify** تلاش کریں
   - **Services** mein **AWS Amplify** talash karein

3. **Get Started** یا **Create new app** پر کلک کریں
   - **Get Started** ya **Create new app** par click karein

4. **Host web app** منتخب کریں
   - **Host web app** muntakhib karein

---

### قدم 13: GitHub Repository Connect کریں
### Qadam 13: GitHub Repository Connect karein

1. **GitHub** منتخب کریں اور **Continue** پر کلک کریں
   - **GitHub** muntakhib karein aur **Continue** par click karein

2. **Authorize AWS Amplify** کی اجازت دیں
   - **Authorize AWS Amplify** ki ijazat dein

3. اپنی repository منتخب کریں: `phaseIII-todoapp`
   - Apni repository muntakhib karein: `phaseIII-todoapp`

4. Branch منتخب کریں: `main` یا `008-mcp-chatbot`
   - Branch muntakhib karein: `main` ya `008-mcp-chatbot`

5. **Next** پر کلک کریں
   - **Next** par click karein

---

### قدم 14: Build Settings کنفیگر کریں
### Qadam 14: Build Settings Configure karein

1. **App name** دیں: `todo-app`
   - **App name** dein: `todo-app`

2. **Monorepo setup** کے لیے:
   - **Monorepo setup** ke liye:
   - **Edit** پر کلک کریں
   - **Edit** par click karein

3. `amplify.yml` کی location بتائیں:
   - `amplify.yml` ki location batayein:
   - `frontend/amplify.yml`

4. **Build and test settings** میں:
   - **Build and test settings** mein:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/.next
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
      - frontend/.next/cache/**/*
```

---

### قدم 15: Environment Variables Add کریں
### Qadam 15: Environment Variables Add karein

**Advanced settings** میں environment variables شامل کریں:
**Advanced settings** mein environment variables shamil karein:

| Variable | Value | مثال / Misal |
|----------|-------|--------------|
| `NEXT_PUBLIC_API_URL` | آپ کا Lambda API URL | `https://xxxxxxxxxx.execute-api.ap-south-1.amazonaws.com/dev` |

**نوٹ:** یہ وہی URL ہے جو Backend deploy کرتے وقت ملا تھا
**Note:** Ye wahi URL hai jo Backend deploy karte waqt mila tha

---

### قدم 16: Deploy شروع کریں
### Qadam 16: Deploy Shuru karein

1. **Save and deploy** پر کلک کریں
   - **Save and deploy** par click karein

2. Amplify خودکار طور پر:
   - Amplify khudkar taur par:
   - Code clone کرے گا
   - Code clone karega
   - Dependencies انسٹال کرے گا
   - Dependencies install karega
   - Build بنائے گا
   - Build banayega
   - Deploy کرے گا
   - Deploy karega

3. **Deployment مکمل ہونے میں 5-10 منٹ لگیں گے**
   - **Deployment mukammal hone mein 5-10 minute lagenge**

4. جب complete ہو، آپ کو URL ملے گا:
   - Jab complete ho, aap ko URL milega:
   - مثال: `https://main.d1234567890.amplifyapp.com`
   - Misal: `https://main.d1234567890.amplifyapp.com`

---

## حصہ سوم: Post-Deployment کنفیگریشن
## Hissa Sovom: Post-Deployment Configuration

### قدم 17: Backend CORS Update کریں
### Qadam 17: Backend CORS Update karein

اب جب frontend کا URL مل گیا ہے:
Ab jab frontend ka URL mil gaya hai:

1. `backend/.env` فائل کھولیں
   - `backend/.env` file kholein

2. `CORS_ORIGINS` update کریں:
   - `CORS_ORIGINS` update karein:

```env
CORS_ORIGINS=https://main.d1234567890.amplifyapp.com,http://localhost:3000
```

3. `FRONTEND_URL` بھی update کریں:
   - `FRONTEND_URL` bhi update karein:

```env
FRONTEND_URL=https://main.d1234567890.amplifyapp.com
```

4. Backend دوبارہ deploy کریں:
   - Backend dobara deploy karein:

```powershell
cd backend
serverless deploy
```

---

### قدم 18: Frontend Environment Variables Update کریں
### Qadam 18: Frontend Environment Variables Update karein

1. AWS Amplify Console میں جائیں
   - AWS Amplify Console mein jayein

2. اپنی app منتخب کریں
   - Apni app muntakhib karein

3. **App settings > Environment variables** میں جائیں
   - **App settings > Environment variables** mein jayein

4. `NEXT_PUBLIC_API_URL` کی value check کریں
   - `NEXT_PUBLIC_API_URL` ki value check karein

5. اگر ضرورت ہو تو update کر کے **Save** کریں
   - Agar zaroorat ho to update kar ke **Save** karein

6. **Redeploy** پر کلک کریں
   - **Redeploy** par click karein

---

### قدم 19: پوری App Test کریں
### Qadam 19: Poori App Test karein

اپنے Amplify URL پر جائیں:
Apne Amplify URL par jayein:

**✅ یہ چیک کریں:**
**✅ Ye check karein:**

1. **صفحہ لوڈ ہوتا ہے**
   - **Safha load hota hai**

2. **Sign Up کام کر رہا ہے**
   - **Sign Up kaam kar raha hai**
   - نیا user بنائیں
   - Naya user banayein

3. **Login کام کر رہا ہے**
   - **Login kaam kar raha hai**

4. **Todo items add ہو رہے ہیں**
   - **Todo items add ho rahe hain**

5. **Complete/Delete کام کر رہے ہیں**
   - **Complete/Delete kaam kar rahe hain**

6. **Voice commands کام کر رہے ہیں** (اگر chatbot enabled ہے)
   - **Voice commands kaam kar rahe hain** (agar chatbot enabled hai)

---

## حصہ چہارم: مانیٹرنگ اور Logs
## Hissa Chaharum: Monitoring aur Logs

### Backend Logs دیکھیں
### Backend Logs dekhein

```powershell
# Lambda logs دیکھیں
# Lambda logs dekhein
serverless logs -f api --tail

# یا AWS Console میں:
# Ya AWS Console mein:
# CloudWatch > Log groups > /aws/lambda/todo-api-dev-api
```

### Frontend Logs دیکھیں
### Frontend Logs dekhein

1. AWS Amplify Console میں جائیں
   - AWS Amplify Console mein jayein

2. اپنی app کھولیں
   - Apni app kholein

3. **App settings > Monitoring** میں جائیں
   - **App settings > Monitoring** mein jayein

---

## اخراجات (Costs) | Ikharajat (Costs)

### Free Tier کے اندر:
### Free Tier ke andar:

**AWS Lambda:**
- 1 ملین requests/ماہ مفت
- 1 million requests/mah muft

**AWS API Gateway:**
- 1 ملین API calls/ماہ مفت (پہلے 12 مہینے)
- 1 million API calls/mah muft (pehle 12 mahine)

**AWS Amplify:**
- 1000 build منٹس/ماہ مفت
- 1000 build minutes/mah muft
- 15 GB bandwidth/ماہ مفت
- 15 GB bandwidth/mah muft

**Neon PostgreSQL:**
- 0.5 GB storage مفت
- 0.5 GB storage muft

**SendGrid:**
- 100 emails/دن مفت
- 100 emails/din muft

**تخمینہ:** چھوٹے استعمال کے لیے تقریباً مفت
**Takhmina:** Chhote istemaal ke liye taqreeban muft

---

## عام مسائل اور حل | Aam Masail aur Hall

### مسئلہ 1: Docker error during deploy
### Masla 1: Docker error during deploy

**علامت:** `Error: docker: command not found`
**Alamat:** `Error: docker: command not found`

**حل:**
**Hall:**
1. Docker Desktop انسٹال کریں
2. Docker Desktop ko چلائیں
3. PowerShell دوبارہ کھولیں
4. `docker --version` سے تصدیق کریں

---

### مسئلہ 2: AWS credentials error
### Masla 2: AWS credentials error

**علامت:** `Error: The security token included in the request is invalid`
**Alamat:** `Error: The security token included in the request is invalid`

**حل:**
**Hall:**
```powershell
aws configure
# دوبارہ credentials درج کریں
# Dobara credentials darj karein
```

---

### مسئلہ 3: Database connection error
### Masla 3: Database connection error

**علامت:** Backend deploy تو ہو گیا لیکن API کام نہیں کر رہی
**Alamat:** Backend deploy to ho gaya lekin API kaam nahi kar rahi

**حل:**
**Hall:**
1. `backend/.env` میں `DATABASE_URL` check کریں
2. Neon dashboard میں database running ہے check کریں
3. Connection string میں `?sslmode=require` شامل ہے check کریں
4. Redeploy کریں: `serverless deploy`

---

### مسئلہ 4: CORS error in frontend
### Masla 4: CORS error in frontend

**علامت:** Browser console میں CORS error
**Alamat:** Browser console mein CORS error

**حل:**
**Hall:**
1. `backend/.env` میں `CORS_ORIGINS` update کریں
2. Amplify URL شامل کریں
3. Redeploy: `serverless deploy`

---

### مسئلہ 5: Amplify build fail
### Masla 5: Amplify build fail

**علامت:** Build میں error
**Alamat:** Build mein error

**حل:**
**Hall:**
1. Amplify Console میں logs check کریں
2. `amplify.yml` path check کریں: `frontend/amplify.yml`
3. Build commands میں `cd frontend` شامل ہے check کریں
4. Environment variable `NEXT_PUBLIC_API_URL` set ہے check کریں

---

## اگلے قدمات | Agle Qadmaat

### 1. Custom Domain Add کریں
### 1. Custom Domain Add karein

**Frontend (Amplify):**
- Amplify Console > Domain management
- اپنا domain add کریں (مثلاً: mytodoapp.com)
- Apna domain add karein (maslan: mytodoapp.com)

**Backend (API Gateway):**
- API Gateway > Custom domain names
- Certificate Manager سے SSL certificate بنائیں
- Certificate Manager se SSL certificate banayein

---

### 2. CI/CD Setup کریں
### 2. CI/CD Setup karein

Amplify خودکار طور پر CD فراہم کرتا ہے:
Amplify khudkar taur par CD faraham karta hai:
- ہر push پر auto-deploy
- Har push par auto-deploy
- Preview deployments for PRs

---

### 3. Monitoring Setup کریں
### 3. Monitoring Setup karein

**CloudWatch Alarms:**
- Lambda errors
- API Gateway latency
- Database connections

---

## مدد کے لیے Resources | Madad ke liye Resources

**Documentation:**
- AWS Lambda: https://docs.aws.amazon.com/lambda/
- AWS Amplify: https://docs.amplify.aws/
- Serverless Framework: https://www.serverless.com/framework/docs/

**Support:**
- AWS Free Tier: https://aws.amazon.com/free/
- Community Forums: https://forums.aws.amazon.com/

---

## خلاصہ | Khulasa

آپ نے کامیابی سے:
Aap ne kamyabi se:

✅ Backend AWS Lambda پر deploy کیا
✅ Backend AWS Lambda par deploy kiya

✅ Frontend AWS Amplify پر deploy کیا
✅ Frontend AWS Amplify par deploy kiya

✅ Database Neon PostgreSQL سے connect کیا
✅ Database Neon PostgreSQL se connect kiya

✅ CORS اور Environment Variables کنفیگر کیے
✅ CORS aur Environment Variables configure kiye

✅ پوری application production میں چل رہی ہے
✅ Poori application production mein chal rahi hai

---

## اہم یاد رکھیں | Ahem Yaad rakhein

1. **.env files کبھی git میں commit نہ کریں**
   - **.env files kabhi git mein commit na karein**

2. **Production میں strong secret keys استعمال کریں**
   - **Production mein strong secret keys istemaal karein**

3. **Regular backups لیں**
   - **Regular backups lein**

4. **Free tier limits monitor کریں**
   - **Free tier limits monitor karein**

5. **Logs regularly چیک کریں**
   - **Logs regularly check karein**

---

## مبارک ہو! 🎉 | Mubarak Ho! 🎉

آپ کی Todo App اب AWS پر live ہے!
Aap ki Todo App ab AWS par live hai!

اگر کوئی مسئلہ آئے تو مجھ سے پوچھیں، میں ہر قدم میں آپ کی مدد کروں گا۔
Agar koi masla aaye to mujh se poochein, main har qadam mein aap ki madad karunga.

---

**تاریخ:** 4 جون 2026
**Tarikh:** 4 June 2026

**تیار کردہ:** Claude (Anthropic AI Assistant)
**Tayyar Kardah:** Claude (Anthropic AI Assistant)
