# AWS Deployment Guide - Todo App

Complete step-by-step guide to deploy your Todo App to AWS using Amplify (frontend) and Lambda (backend).

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Database Setup](#database-setup)
4. [Backend Deployment (AWS Lambda)](#backend-deployment-aws-lambda)
5. [Frontend Deployment (AWS Amplify)](#frontend-deployment-aws-amplify)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Testing Your Deployment](#testing-your-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Cost Estimation](#cost-estimation)

---

## Prerequisites

### Required Accounts
- [ ] AWS Account (with billing enabled)
- [ ] Neon PostgreSQL account (or AWS RDS if preferred)
- [ ] SendGrid account (or AWS SES for emails)
- [ ] OpenAI account (optional, for chatbot feature)

### Required Tools
```bash
# Install AWS CLI
# Windows: https://aws.amazon.com/cli/
# Mac: brew install awscli
# Linux: apt-get install awscli

# Verify installation
aws --version

# Configure AWS CLI
aws configure
# Enter: AWS Access Key ID, Secret Access Key, Default region (us-east-1), Default output format (json)

# Optional: Install Serverless Framework (easiest deployment method)
npm install -g serverless

# Optional: Install AWS SAM CLI (alternative deployment method)
# https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Users/Browsers                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────┐
│              AWS Amplify (Frontend)                      │
│              - Next.js 15 Application                    │
│              - Static Assets (HTML, CSS, JS)             │
│              - Automatic HTTPS                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ API Calls
                     ▼
┌─────────────────────────────────────────────────────────┐
│         AWS API Gateway + Lambda (Backend)               │
│         - FastAPI Application                            │
│         - JWT Authentication                             │
│         - Business Logic                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ SQL Queries
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Neon PostgreSQL (Database)                       │
│         - Serverless PostgreSQL                          │
│         - Automatic Scaling                              │
└─────────────────────────────────────────────────────────┘

External Services:
- SendGrid/AWS SES (Email delivery)
- OpenAI API (Chatbot - optional)
```

---

## Database Setup

### Option 1: Continue Using Neon PostgreSQL (Recommended for Easy Setup)

Neon is already configured in your project. No changes needed!

1. Keep your existing `DATABASE_URL` from `.env`
2. Neon works great with AWS Lambda (serverless-friendly)
3. Free tier includes 0.5 GB storage and 3 GB data transfer/month

### Option 2: Migrate to AWS RDS PostgreSQL (For AWS-Native Setup)

If you prefer AWS-native database:

```bash
# 1. Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier todo-app-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username admin \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxx \
  --db-subnet-group-name default \
  --backup-retention-period 7 \
  --publicly-accessible

# 2. Wait for instance to be available (5-10 minutes)
aws rds describe-db-instances --db-instance-identifier todo-app-db

# 3. Get connection endpoint
# Use format: postgresql://admin:PASSWORD@endpoint:5432/postgres
```

**For this guide, we'll continue using Neon PostgreSQL.**

---

## Backend Deployment (AWS Lambda)

We'll use **Serverless Framework** for the easiest deployment experience.

### Step 1: Install Dependencies

```bash
cd backend

# Install Serverless Framework globally
npm install -g serverless

# Install Serverless plugins
npm init -y  # If package.json doesn't exist
npm install --save-dev serverless-python-requirements
```

### Step 2: Prepare Environment Variables

Create `.env` file in `backend` directory:

```bash
# backend/.env
DATABASE_URL=postgresql://your_neon_url_here?sslmode=require
SECRET_KEY=generate_with_openssl_rand_hex_32
REFRESH_TOKEN_SECRET=different_secret_than_above
CORS_ORIGINS=*  # Will update after Amplify deployment
EMAIL_FROM_ADDRESS=noreply@yourdomain.com
SENDGRID_API_KEY=your_sendgrid_key_here
FRONTEND_URL=https://localhost:3000  # Will update after Amplify deployment
OPENAI_API_KEY=your_openai_key_here  # Optional
```

### Step 3: Deploy Backend to AWS Lambda

```bash
# From backend directory
cd backend

# Deploy to AWS (creates Lambda function + API Gateway)
serverless deploy

# Expected output:
# ✓ Service deployed to stack todo-api-dev
# endpoints:
#   ANY - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/{proxy+}
# functions:
#   api: todo-api-dev-api
```

**Save the API endpoint URL!** You'll need it for frontend configuration.

Example: `https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev`

### Step 4: Update CORS in Lambda

Now that we have the Lambda URL, we need to prepare for Amplify deployment:

```bash
# We'll update CORS after getting Amplify URL
# For now, keep CORS_ORIGINS=* for testing
```

### Step 5: Test Backend Deployment

```bash
# Test health endpoint
curl https://YOUR_API_GATEWAY_URL/dev/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}

# Test API docs
# Open in browser: https://YOUR_API_GATEWAY_URL/dev/docs
```

### Alternative Deployment Methods

<details>
<summary><b>Option 2: Deploy with AWS SAM</b></summary>

```bash
# From backend directory
cd backend

# Build and deploy
sam build
sam deploy --guided

# Follow the prompts:
# Stack Name: todo-api
# AWS Region: us-east-1
# Parameter DatabaseURL: your_neon_url
# Parameter SecretKey: your_secret_key
# ... (provide all parameters)
```
</details>

<details>
<summary><b>Option 3: Deploy via AWS Console</b></summary>

1. **Create Lambda Function**
   - Go to AWS Lambda Console
   - Click "Create function"
   - Choose "Author from scratch"
   - Function name: `todo-api`
   - Runtime: Python 3.11
   - Click "Create function"

2. **Upload Code**
   ```bash
   # Create deployment package
   cd backend
   pip install -r requirements.txt -t package/
   cp -r app package/
   cp lambda_handler.py package/
   cp index.py package/
   cd package
   zip -r ../deployment.zip .
   cd ..
   ```
   - In Lambda Console, upload `deployment.zip`

3. **Configure Environment Variables**
   - Configuration > Environment variables
   - Add all variables from `.env.example`

4. **Create API Gateway**
   - Add trigger: API Gateway
   - Create new REST API
   - Security: Open
   - Click "Add"
</details>

---

## Frontend Deployment (AWS Amplify)

### Step 1: Push Code to GitHub (if not already)

Amplify deploys from Git repositories.

```bash
# From project root
git init  # If not a git repo
git add .
git commit -m "Prepare for AWS deployment"
git branch -M main

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Create Amplify App

#### Via AWS Console (Recommended):

1. **Open AWS Amplify Console**
   - Go to: https://console.aws.amazon.com/amplify/
   - Click "Get Started" under "Amplify Hosting"

2. **Connect Repository**
   - Select "GitHub"
   - Authorize AWS Amplify to access your GitHub
   - Select repository: `YOUR_REPO`
   - Select branch: `main`
   - Click "Next"

3. **Configure Build Settings**
   - App name: `todo-app-frontend`
   - Build and test settings will be auto-detected from `amplify.yml`
   - Click "Next"

4. **Set Environment Variables** (IMPORTANT!)
   - Click "Advanced settings"
   - Add environment variables:
     ```
     NEXT_PUBLIC_API_URL=https://YOUR_API_GATEWAY_URL/dev
     BETTER_AUTH_SECRET=same_as_backend_SECRET_KEY
     BETTER_AUTH_URL=https://main.xxxxxx.amplifyapp.com  # Placeholder, will update
     NEXT_PUBLIC_COOKIE_DOMAIN=.amplifyapp.com
     NEXT_PUBLIC_SECURE_COOKIES=true
     NEXT_PUBLIC_COOKIE_SAMESITE=lax
     ```
   - **Note**: We'll update `BETTER_AUTH_URL` after first deployment

5. **Review and Deploy**
   - Review settings
   - Click "Save and deploy"
   - Wait 5-10 minutes for build and deployment

6. **Get Your Amplify URL**
   - After deployment, you'll see: `https://main.xxxxxx.amplifyapp.com`
   - **Save this URL!**

### Step 3: Update Environment Variables

Now update with the actual Amplify URL:

1. Go to Amplify Console > Your App
2. Navigate to: **App settings > Environment variables**
3. Click "Manage variables"
4. Update `BETTER_AUTH_URL` with your Amplify URL
5. Click "Save"
6. Redeploy: **App settings > General > Redeploy this version**

### Step 4: Update Backend CORS

Update Lambda to allow your Amplify domain:

```bash
# Update backend/.env
CORS_ORIGINS=https://main.xxxxxx.amplifyapp.com
FRONTEND_URL=https://main.xxxxxx.amplifyapp.com

# Redeploy backend
cd backend
serverless deploy
```

---

## Post-Deployment Configuration

### 1. Configure Custom Domain (Optional but Recommended)

#### For Frontend (Amplify):
1. Amplify Console > Your App > **Domain management**
2. Click "Add domain"
3. Enter your domain: `yourdomain.com`
4. Follow DNS configuration instructions
5. Wait for SSL certificate provisioning (5-10 minutes)

#### For Backend (API Gateway):
1. API Gateway Console > Your API > **Custom domain names**
2. Click "Create"
3. Enter: `api.yourdomain.com`
4. Select ACM certificate (or create new)
5. Add mapping to your API stage
6. Update DNS with CloudFront distribution URL

### 2. Update Environment Variables with Custom Domains

If using custom domains, update all environment variables:

**Backend Lambda:**
```bash
CORS_ORIGINS=https://yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

**Frontend Amplify:**
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
BETTER_AUTH_URL=https://yourdomain.com
NEXT_PUBLIC_COOKIE_DOMAIN=.yourdomain.com
```

### 3. Configure Email Service

#### Option A: SendGrid (Easier)
1. Create SendGrid account: https://signup.sendgrid.com/
2. Verify sender email: Settings > Sender Authentication
3. Create API key: Settings > API Keys
4. Update Lambda: `SENDGRID_API_KEY=your_key_here`

#### Option B: AWS SES (AWS-Native)
```bash
# 1. Verify email address
aws ses verify-email-identity --email-address noreply@yourdomain.com

# 2. Create IAM user with SES permissions
aws iam create-user --user-name ses-sender

# 3. Attach SES policy
aws iam attach-user-policy \
  --user-name ses-sender \
  --policy-arn arn:aws:iam::aws:policy/AmazonSESFullAccess

# 4. Create access keys
aws iam create-access-key --user-name ses-sender

# 5. Update Lambda environment variables
EMAIL_PROVIDER=aws_ses
AWS_SES_REGION=us-east-1
AWS_SES_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SES_SECRET_ACCESS_KEY=your_secret_key
```

### 4. Set Up Monitoring (Recommended)

#### CloudWatch Alarms:
```bash
# Lambda error alarm
aws cloudwatch put-metric-alarm \
  --alarm-name todo-api-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

#### Amplify Notifications:
1. Amplify Console > Your App > **Notifications**
2. Connect to SNS topic or email
3. Enable build notifications

---

## Testing Your Deployment

### 1. Health Checks

```bash
# Test backend health
curl https://YOUR_API_URL/health

# Expected: {"status":"healthy","version":"1.0.0"}
```

### 2. API Documentation

Open in browser: `https://YOUR_API_URL/docs`

### 3. Frontend Access

Open in browser: `https://YOUR_AMPLIFY_URL`

### 4. Full User Flow Test

1. **Register a new user**
   - Go to: `https://YOUR_AMPLIFY_URL/register`
   - Create account with email/password
   - Check email for verification (if configured)

2. **Login**
   - Go to: `https://YOUR_AMPLIFY_URL/login`
   - Login with credentials
   - Verify redirect to dashboard

3. **Create a Todo**
   - Click "New Todo"
   - Enter title and description
   - Save and verify it appears

4. **Test Chatbot** (if OpenAI configured)
   - Navigate to Chat section
   - Send a message
   - Verify response

---

## Troubleshooting

### Common Issues and Solutions

#### 1. CORS Errors in Browser

**Symptoms:**
```
Access to fetch at 'https://api...' from origin 'https://frontend...' has been blocked by CORS policy
```

**Solutions:**
- Verify `CORS_ORIGINS` in Lambda includes your Amplify URL
- Ensure no trailing slashes in URLs
- Check CloudWatch logs for actual CORS configuration
- Redeploy Lambda after changing CORS settings

```bash
# Check Lambda environment variables
aws lambda get-function-configuration --function-name todo-api-dev-api
```

#### 2. 502 Bad Gateway from API Gateway

**Symptoms:** API Gateway returns 502 error

**Solutions:**
- Check Lambda function logs in CloudWatch
- Verify Lambda has correct handler: `lambda_handler.handler`
- Ensure all dependencies are included in deployment package
- Check Lambda timeout settings (should be at least 30 seconds)

```bash
# View Lambda logs
aws logs tail /aws/lambda/todo-api-dev-api --follow
```

#### 3. Database Connection Errors

**Symptoms:**
```
could not connect to server
```

**Solutions:**
- Verify `DATABASE_URL` format is correct
- Ensure `sslmode=require` is present for Neon
- Check Lambda has internet access (not in VPC or VPC has NAT Gateway)
- Test connection manually:

```python
import psycopg
conn = psycopg.connect("your_database_url")
conn.close()
print("Connection successful!")
```

#### 4. Authentication Not Working

**Symptoms:** Login succeeds but user isn't authenticated

**Solutions:**
- Verify `BETTER_AUTH_SECRET` in Amplify matches `SECRET_KEY` in Lambda
- Check cookie settings:
  - `NEXT_PUBLIC_SECURE_COOKIES=true`
  - `NEXT_PUBLIC_COOKIE_SAMESITE=lax`
- Verify cookies are being set (browser DevTools > Application > Cookies)
- Ensure domains are configured correctly

#### 5. Amplify Build Failing

**Symptoms:** Build fails during npm install or build step

**Solutions:**
- Check Amplify build logs in console
- Verify `amplify.yml` is in frontend root
- Ensure all dependencies in `package.json`
- Try locally: `npm ci && npm run build`

```bash
# Test build locally
cd frontend
npm ci
npm run build
```

#### 6. Environment Variables Not Loading

**Symptoms:** API returns undefined or default values

**Solutions:**
- Verify variables are set in correct location:
  - Lambda: Configuration > Environment variables
  - Amplify: App Settings > Environment variables
- Redeploy after changing variables
- Check variable names (case-sensitive!)
- For Amplify: Variables must start with `NEXT_PUBLIC_` to be available in browser

---

## Cost Estimation

### Monthly Cost Breakdown (Estimated)

#### Free Tier Eligible (First 12 Months):
```
AWS Lambda:
  - 1M requests/month FREE
  - 400,000 GB-seconds compute FREE
  - Estimated: $0/month (typical usage)

API Gateway:
  - 1M API calls/month FREE
  - Estimated: $0/month (typical usage)

AWS Amplify:
  - 1,000 build minutes/month FREE
  - 15 GB served/month FREE
  - Estimated: $0/month (typical usage)
```

#### After Free Tier:
```
AWS Lambda:
  - 10M requests/month: ~$2.00
  - Compute time: ~$5.00

API Gateway:
  - 10M requests/month: ~$35.00

AWS Amplify:
  - 1,000 build minutes: $0.01/min = $10.00
  - 100 GB data transfer: ~$15.00

Neon PostgreSQL:
  - Free tier: 0.5 GB storage, 3 GB transfer
  - Paid: ~$24/month for production workload

SendGrid:
  - Free tier: 100 emails/day
  - Essentials: $19.95/month for 50k emails

OpenAI API (Optional):
  - GPT-4o: ~$5-20/month depending on usage

Total (Low Usage): ~$5-10/month
Total (Medium Usage): ~$50-80/month
Total (High Usage): ~$150-200/month
```

### Cost Optimization Tips:

1. **Use Neon Free Tier** for development
2. **Enable Lambda Reserved Concurrency** for predictable costs
3. **Set up CloudWatch Alarms** for unexpected spend
4. **Use Amplify SSG** where possible to reduce compute
5. **Implement API caching** to reduce Lambda invocations
6. **Monitor with AWS Cost Explorer** regularly

---

## Next Steps

### 1. Production Readiness Checklist

- [ ] Configure custom domain
- [ ] Set up CloudWatch alarms
- [ ] Enable AWS WAF on API Gateway
- [ ] Set up automated backups (Neon or RDS)
- [ ] Configure proper IAM roles with least privilege
- [ ] Enable CloudTrail for audit logging
- [ ] Set up automated database migrations (Alembic)
- [ ] Configure rate limiting in API Gateway
- [ ] Set up error tracking (Sentry or CloudWatch Insights)
- [ ] Create staging environment
- [ ] Set up CI/CD pipeline (GitHub Actions + AWS)

### 2. Security Hardening

```bash
# 1. Enable AWS WAF
aws wafv2 create-web-acl \
  --name todo-api-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules ...

# 2. Enable API Gateway throttling
aws apigateway update-stage \
  --rest-api-id YOUR_API_ID \
  --stage-name dev \
  --patch-operations \
    op=replace,path=/throttle/rateLimit,value=1000 \
    op=replace,path=/throttle/burstLimit,value=2000

# 3. Rotate secrets regularly
aws secretsmanager rotate-secret \
  --secret-id todo-app/SECRET_KEY
```

### 3. Performance Optimization

- **Enable Lambda Provisioned Concurrency** for consistent performance
- **Use CloudFront** in front of API Gateway for caching
- **Implement database connection pooling** (already configured)
- **Enable Amplify SSR caching**
- **Add Redis cache** for frequently accessed data

### 4. Monitoring and Observability

- Set up **CloudWatch Dashboards**
- Enable **X-Ray tracing** for Lambda
- Configure **CloudWatch Logs Insights** queries
- Set up **SNS alerts** for critical errors

---

## Additional Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS Amplify Documentation](https://docs.amplify.aws/)
- [Serverless Framework Documentation](https://www.serverless.com/framework/docs)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Neon PostgreSQL Docs](https://neon.tech/docs/introduction)

---

## Support

If you encounter issues:

1. **Check CloudWatch Logs**
   - Lambda: `/aws/lambda/YOUR_FUNCTION_NAME`
   - API Gateway: Enable access logging

2. **Amplify Build Logs**
   - Amplify Console > Your App > Build details

3. **Community Support**
   - AWS Forums
   - Stack Overflow
   - GitHub Issues

---

**Deployment Complete!** 🎉

Your Todo App is now running on AWS with:
- ✅ Scalable serverless backend (Lambda)
- ✅ High-performance frontend (Amplify)
- ✅ Secure authentication (JWT)
- ✅ Managed PostgreSQL database (Neon)
- ✅ Production-ready infrastructure

**Next:** Test your app, configure custom domain, and set up monitoring!
