# AWS Deployment Checklist | تعیناتی کی فہرست
# AWS Deployment Checklist | Tainaati ki Fehrist

---

## Pre-Deployment | تعیناتی سے پہلے

### Accounts Setup | اکاؤنٹس کی تیاری

- [ ] AWS Account بنایا (https://aws.amazon.com/)
- [ ] GitHub Account موجود ہے
- [ ] Neon PostgreSQL Database بنایا (https://neon.tech)
- [ ] SendGrid Account بنایا (optional, https://sendgrid.com)
- [ ] OpenAI API Key حاصل کیا (optional)

### Local Environment | مقامی ماحول

- [ ] Node.js انسٹال ہے (`node --version`)
- [ ] npm انسٹال ہے (`npm --version`)
- [ ] Python 3.11 انسٹال ہے
- [ ] Git انسٹال ہے (`git --version`)
- [ ] AWS CLI انسٹال کیا (`aws --version`)
- [ ] Docker Desktop انسٹال اور چل رہا ہے (`docker --version`)

### AWS Configuration | AWS کی تشکیل

- [ ] AWS credentials کنفیگر کیے (`aws configure`)
  - [ ] Access Key ID
  - [ ] Secret Access Key
  - [ ] Region: `ap-south-1`
  - [ ] Output format: `json`

---

## Backend Deployment | Backend کی تعیناتی

### Installation | تنصیب

- [ ] Serverless Framework انسٹال کیا
  ```powershell
  npm install -g serverless
  ```

- [ ] Serverless plugin انسٹال کی
  ```powershell
  cd "D:\quarterr 4\phaseIII-todoapp"
  npm install --save-dev serverless-python-requirements
  ```

### Environment Setup | ماحول کی تیاری

- [ ] `backend/.env` فائل بنائی
- [ ] Database URL شامل کیا
  ```
  DATABASE_URL=postgresql://...
  ```
- [ ] Secret keys generate کیں
  ```
  SECRET_KEY=...
  REFRESH_TOKEN_SECRET=...
  ```
- [ ] CORS origins سیٹ کیے
  ```
  CORS_ORIGINS=*
  ```
- [ ] Email configuration شامل کی
  ```
  EMAIL_PROVIDER=sendgrid
  SENDGRID_API_KEY=...
  EMAIL_FROM_ADDRESS=...
  ```
- [ ] Frontend URL شامل کیا
  ```
  FRONTEND_URL=http://localhost:3000
  ```
- [ ] OpenAI API key شامل کی (optional)
  ```
  OPENAI_API_KEY=...
  ```

### Deploy | تعیناتی

- [ ] Backend deploy کیا
  ```powershell
  cd backend
  serverless deploy
  ```

- [ ] API Gateway URL محفوظ کیا
  ```
  https://xxxxxxxxxx.execute-api.ap-south-1.amazonaws.com/dev
  ```

- [ ] Health endpoint test کی
  ```powershell
  curl https://your-api-url/dev/health
  ```

---

## Frontend Deployment | Frontend کی تعیناتی

### GitHub Setup | GitHub کی تیاری

- [ ] Code GitHub پر push کیا
  ```powershell
  git init
  git add .
  git commit -m "Initial commit"
  git remote add origin https://github.com/username/repo.git
  git push -u origin main
  ```

### Amplify Setup | Amplify کی تشکیل

- [ ] AWS Amplify Console میں login کیا
- [ ] New app بنایا: "Host web app"
- [ ] GitHub repository connect کی
- [ ] Repository منتخب کی: `phaseIII-todoapp`
- [ ] Branch منتخب کی: `main` یا `008-mcp-chatbot`

### Build Configuration | Build کی تشکیل

- [ ] Build settings edit کیں
- [ ] `amplify.yml` path سیٹ کی: `frontend/amplify.yml`
- [ ] Environment variable add کی:
  ```
  NEXT_PUBLIC_API_URL=https://your-lambda-url.execute-api.ap-south-1.amazonaws.com/dev
  ```

### Deploy | تعیناتی

- [ ] Deploy شروع کی ("Save and deploy")
- [ ] Build مکمل ہونے کا انتظار کیا (5-10 منٹ)
- [ ] Amplify URL محفوظ کیا
  ```
  https://main.d1234567890.amplifyapp.com
  ```

---

## Post-Deployment | تعیناتی کے بعد

### Backend Update | Backend کی تازہ کاری

- [ ] `backend/.env` میں CORS update کیا
  ```
  CORS_ORIGINS=https://main.d1234567890.amplifyapp.com,http://localhost:3000
  ```

- [ ] `backend/.env` میں FRONTEND_URL update کیا
  ```
  FRONTEND_URL=https://main.d1234567890.amplifyapp.com
  ```

- [ ] Backend redeploy کیا
  ```powershell
  cd backend
  serverless deploy
  ```

### Frontend Verification | Frontend کی تصدیق

- [ ] Amplify Console میں environment variables check کیں
- [ ] `NEXT_PUBLIC_API_URL` صحیح ہے تصدیق کی
- [ ] Redeploy کیا (اگر ضرورت ہو)

---

## Testing | جانچ

### Frontend Tests | Frontend کی جانچ

- [ ] Amplify URL پر app open کی
- [ ] Page صحیح طرح load ہوا
- [ ] Sign Up form کام کر رہا ہے
- [ ] New user بنایا اور verify کیا

### Backend Tests | Backend کی جانچ

- [ ] Login کامیاب ہوا
- [ ] Dashboard load ہوا
- [ ] New todo add کیا
- [ ] Todo complete کیا
- [ ] Todo delete کیا
- [ ] Logout کیا

### Optional Features | اختیاری خصوصیات

- [ ] Email verification کام کر رہی ہے
- [ ] Voice commands test کیں (اگر enabled ہے)
- [ ] Chatbot test کیا (اگر OpenAI key ہے)

---

## Monitoring Setup | نگرانی کی تیاری

### CloudWatch | کلاؤڈ واچ

- [ ] Lambda logs access کیں
  ```powershell
  serverless logs -f api --tail
  ```

- [ ] CloudWatch dashboard check کی
  - [ ] Lambda errors
  - [ ] API Gateway requests
  - [ ] Response times

### Amplify Monitoring | Amplify کی نگرانی

- [ ] Amplify Console میں monitoring check کی
  - [ ] Build history
  - [ ] Deployment logs
  - [ ] Access logs

---

## Optional Enhancements | اختیاری بہتریاں

### Custom Domain | اپنا ڈومین

- [ ] Domain خریدا
- [ ] Amplify میں custom domain add کیا
- [ ] SSL certificate verify کیا
- [ ] API Gateway میں custom domain add کیا

### CI/CD | خودکار تعیناتی

- [ ] Amplify auto-deploy verify کیا
- [ ] Branch previews enable کیے
- [ ] PR previews کنفیگر کیے

### Security | سیکیورٹی

- [ ] AWS IAM roles review کیے
- [ ] Lambda permissions check کیے
- [ ] API Gateway authorizers add کیے (اگر ضرورت ہو)
- [ ] Rate limiting کنفیگر کی

### Cost Monitoring | اخراجات کی نگرانی

- [ ] AWS Cost Explorer setup کیا
- [ ] Budget alerts set کیے
- [ ] Free tier limits monitor کیے

---

## Maintenance | دیکھ بھال

### Regular Tasks | باقاعدہ کام

- [ ] ہفتہ وار logs check کریں
- [ ] ماہانہ costs review کریں
- [ ] Dependencies update کریں
- [ ] Security patches لگائیں
- [ ] Database backup verify کریں

### Documentation | دستاویزات

- [ ] API endpoints document کریں
- [ ] Environment variables list بنائیں
- [ ] Deployment process document کریں
- [ ] Troubleshooting guide بنائیں

---

## Rollback Plan | واپسی کا منصوبہ

### If Issues Occur | اگر مسائل آئیں

- [ ] Rollback plan تیار ہے
- [ ] Previous version کا backup ہے
- [ ] Database rollback script ہے
- [ ] Emergency contacts کی list ہے

---

## Completion Status | تکمیل کی حالت

**Overall Progress:** _____ / 100%

**Deployment Date:** _______________

**Deployed By:** _______________

**Production URL:** https://_______________.amplifyapp.com

**API URL:** https://_______________.execute-api.ap-south-1.amazonaws.com/dev

---

## Notes | نوٹس

```
اپنے نوٹس یہاں لکھیں:
Apne notes yahan likhein:






```

---

## Support Resources | مدد کے وسائل

- **AWS Support:** https://console.aws.amazon.com/support/
- **Amplify Docs:** https://docs.amplify.aws/
- **Serverless Docs:** https://www.serverless.com/framework/docs/
- **Community:** https://forums.aws.amazon.com/

---

**Last Updated:** 2026-06-04
**Version:** 1.0
