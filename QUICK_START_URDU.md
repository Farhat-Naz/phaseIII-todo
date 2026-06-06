# فوری شروعات - AWS Deployment
# Fori Shuruat - AWS Deployment

---

## 5 منٹ میں Deploy کریں | 5 Minute mein Deploy karein

یہ فوری رہنمائی ہے۔ تفصیلی ہدایات کے لیے `DEPLOYMENT_GUIDE_URDU.md` دیکھیں۔
Ye fori rahnumai hai. Tafsili hidayat ke liye `DEPLOYMENT_GUIDE_URDU.md` dekhein.

---

## قدم 1: پہلے سے تیار کریں (5 منٹ)
## Qadam 1: Pehle se Tayyar karein (5 minutes)

### ✅ Accounts بنائیں:
1. AWS Account: https://aws.amazon.com/
2. GitHub Account: https://github.com/
3. Neon Database: https://neon.tech/
4. SendGrid (optional): https://sendgrid.com/

### ✅ Software انسٹال کریں:
```powershell
# Check کریں:
node --version   # v18 یا زیادہ
npm --version
python --version # 3.11
git --version
```

---

## قدم 2: Backend Setup (10 منٹ)
## Qadam 2: Backend Setup (10 minutes)

### A. AWS CLI کنفیگر کریں:
```powershell
# AWS CLI ڈاؤن لوڈ: https://awscli.amazonaws.com/AWSCLIV2.msi
aws configure
# اپنی credentials درج کریں
```

### B. Serverless انسٹال کریں:
```powershell
# Global installation
npm install -g serverless

# Project plugin
cd "D:\quarterr 4\phaseIII-todoapp"
npm install --save-dev serverless-python-requirements
```

### C. Docker انسٹال کریں:
- https://www.docker.com/products/docker-desktop/ سے ڈاؤن لوڈ کریں
- انسٹال کر کے چلائیں

### D. Environment Variables سیٹ کریں:
```powershell
cd backend

# Secret keys بنائیں
.\generate-secrets.ps1

# .env فائل بنائیں
copy .env.example .env

# Notepad میں کھولیں
notepad .env
```

**ضروری Variables بھریں:**
```env
DATABASE_URL=postgresql://...  # Neon سے
SECRET_KEY=...                  # Script نے بنائی
REFRESH_TOKEN_SECRET=...        # Script نے بنائی
CORS_ORIGINS=*
SENDGRID_API_KEY=...            # SendGrid سے
EMAIL_FROM_ADDRESS=noreply@yourdomain.com
FRONTEND_URL=http://localhost:3000
OPENAI_API_KEY=...              # Optional
```

### E. Deploy کریں:
```powershell
serverless deploy
```

**✅ Success:** API URL محفوظ کریں!
```
https://xxxxx.execute-api.ap-south-1.amazonaws.com/dev
```

---

## قدم 3: Frontend Setup (10 منٹ)
## Qadam 3: Frontend Setup (10 minutes)

### A. GitHub پر Push کریں:
```powershell
cd "D:\quarterr 4\phaseIII-todoapp"

git init
git add .
git commit -m "feat: Initial deployment"

# GitHub پر repo بنائیں: phaseIII-todoapp
git remote add origin https://github.com/YOUR_USERNAME/phaseIII-todoapp.git
git push -u origin main
```

### B. AWS Amplify Setup:
1. AWS Console میں جائیں
2. **AWS Amplify** تلاش کریں
3. **Create new app > Host web app**
4. **GitHub** منتخب کریں
5. Repository: `phaseIII-todoapp`
6. Branch: `main`

### C. Build Settings:
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
```

### D. Environment Variable:
```
NEXT_PUBLIC_API_URL = https://xxxxx.execute-api.ap-south-1.amazonaws.com/dev
```
(یہ وہی URL ہے جو Backend deploy سے ملا)

### E. Deploy:
**Save and deploy** پر کلک کریں

**✅ Success:** Amplify URL محفوظ کریں!
```
https://main.d1234567890.amplifyapp.com
```

---

## قدم 4: Final Updates (5 منٹ)
## Qadam 4: Final Updates (5 minutes)

### Backend CORS Update:
```powershell
cd backend
notepad .env
```

**Update کریں:**
```env
CORS_ORIGINS=https://main.d1234567890.amplifyapp.com,http://localhost:3000
FRONTEND_URL=https://main.d1234567890.amplifyapp.com
```

**Redeploy:**
```powershell
serverless deploy
```

---

## قدم 5: Test کریں ✅
## Qadam 5: Test karein ✅

Amplify URL پر جائیں اور check کریں:

- [ ] Page load ہو رہا ہے
- [ ] Sign Up کام کر رہا ہے
- [ ] Login کام کر رہا ہے
- [ ] Todo add/complete/delete کام کر رہے ہیں
- [ ] Voice commands کام کر رہے ہیں (optional)

---

## مسائل؟ | Masail?

### Backend کام نہیں کر رہی:
```powershell
serverless logs -f api --tail
```

### Frontend کام نہیں کر رہا:
- Amplify Console > Monitoring > Logs

### CORS Error:
- Backend `.env` میں Amplify URL شامل کریں
- Redeploy: `serverless deploy`

### Database Error:
- Neon dashboard میں database running ہے check کریں
- Connection string صحیح ہے check کریں

---

## اگلے قدمات | Agle Qadmaat

### Custom Domain:
- Amplify Console > Domain management
- اپنا domain add کریں

### Monitoring:
- CloudWatch alarms سیٹ کریں
- Cost alerts لگائیں

### Security:
- .env فائل **کبھی Git میں commit نہ کریں**
- Strong passwords استعمال کریں
- Regular backups لیں

---

## فوری Commands | Fori Commands

```powershell
# Backend deploy
cd backend && serverless deploy

# Backend logs
serverless logs -f api --tail

# Backend remove
serverless remove

# Frontend redeploy
# Amplify Console میں "Redeploy this version" پر کلک

# Secret keys generate
cd backend && .\generate-secrets.ps1
```

---

## مدد چاہیے؟ | Madad Chahiye?

**مکمل رہنمائی:** `DEPLOYMENT_GUIDE_URDU.md`
**Checklist:** `DEPLOYMENT_CHECKLIST.md`

**Documentation:**
- AWS Lambda: https://docs.aws.amazon.com/lambda/
- AWS Amplify: https://docs.amplify.aws/
- Serverless: https://www.serverless.com/framework/docs/

---

## خلاصہ | Khulasa

✅ **Backend:** AWS Lambda پر چل رہی
✅ **Frontend:** AWS Amplify پر چل رہا
✅ **Database:** Neon PostgreSQL سے connected
✅ **Production Ready:** اب استعمال کے لیے تیار

**کل وقت:** ~30 منٹ

---

## URLs یاد رکھیں | URLs Yaad rakhein

```
Backend API: https://_____.execute-api.ap-south-1.amazonaws.com/dev
Frontend:    https://main.d_____.amplifyapp.com
Database:    Neon Console
Logs:        CloudWatch / Amplify Console
```

---

**مبارک ہو! 🎉 آپ کی Todo App live ہے!**
**Mubarak ho! 🎉 Aap ki Todo App live hai!**

اگر کوئی مسئلہ ہو تو مجھ سے پوچھیں۔
Agar koi masla ho to mujh se poochein.

---

**Date:** 2026-06-04
**Created by:** Claude (Anthropic)
