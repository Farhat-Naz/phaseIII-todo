# AWS Environment Variables Configuration Guide

This document lists all environment variables required for deploying the Todo App to AWS.

## Table of Contents
- [Backend (AWS Lambda)](#backend-aws-lambda)
- [Frontend (AWS Amplify)](#frontend-aws-amplify)
- [How to Set Environment Variables](#how-to-set-environment-variables)

---

## Backend (AWS Lambda)

Set these environment variables in your Lambda function configuration or in your deployment tool (Serverless Framework, SAM, etc.).

### Database Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string (Neon or RDS) | ✅ Yes | `postgresql://user:pass@host.neon.tech/db?sslmode=require` |

### JWT Authentication

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `SECRET_KEY` | JWT token signing secret | ✅ Yes | - | Generate with: `openssl rand -hex 32` |
| `REFRESH_TOKEN_SECRET` | Refresh token signing secret (must differ from SECRET_KEY) | ✅ Yes | - | Generate with: `openssl rand -hex 32` |
| `ALGORITHM` | JWT algorithm | No | `HS256` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration in minutes | No | `30` | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration in days | No | `7` | `7` |

### Email Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `EMAIL_PROVIDER` | Email service provider | No | `sendgrid` | `sendgrid` or `aws_ses` |
| `SENDGRID_API_KEY` | SendGrid API key (if using SendGrid) | ⚠️ Conditional | - | `SG.xxxxxxxxxxxxx` |
| `AWS_SES_REGION` | AWS SES region (if using SES) | ⚠️ Conditional | - | `us-east-1` |
| `AWS_SES_ACCESS_KEY_ID` | AWS SES access key (if using SES) | ⚠️ Conditional | - | `AKIAXXXXXXXXXXXXXXXX` |
| `AWS_SES_SECRET_ACCESS_KEY` | AWS SES secret key (if using SES) | ⚠️ Conditional | - | `xxxxxxxxxxxxx` |
| `EMAIL_FROM_ADDRESS` | Sender email address | ✅ Yes | - | `noreply@yourdomain.com` |
| `EMAIL_FROM_NAME` | Sender name | No | `TodoApp` | `TodoApp` |

### CORS Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `CORS_ORIGINS` | Comma-separated list of allowed origins | ✅ Yes | `*` | `https://yourdomain.amplifyapp.com` |
| `CORS_ALLOW_CREDENTIALS` | Allow credentials in CORS | No | `True` | `True` |

### Application URLs

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `FRONTEND_URL` | Frontend application URL (for email links) | ✅ Yes | `https://yourdomain.amplifyapp.com` |

### AI/Chatbot Configuration

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API key for chatbot | ⚠️ Optional | - | `sk-xxxxxxxxxxxxx` |
| `AI_MODEL` | OpenAI model to use | No | `gpt-4o` | `gpt-4o`, `gpt-4-turbo` |

### Logging

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `LOG_LEVEL` | Logging level | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

---

## Frontend (AWS Amplify)

Set these environment variables in AWS Amplify Console: **App Settings > Environment Variables**

### API Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API Gateway URL | ✅ Yes | `https://xxxxx.execute-api.us-east-1.amazonaws.com/Prod` |

### Better Auth Configuration

| Variable | Description | Required | Notes |
|----------|-------------|----------|-------|
| `BETTER_AUTH_SECRET` | Auth secret (MUST match backend SECRET_KEY) | ✅ Yes | Must be identical to backend `SECRET_KEY` |
| `BETTER_AUTH_URL` | Amplify app URL | ✅ Yes | Get from Amplify Console after deployment |

### Cookie Configuration

| Variable | Description | Required | AWS Value | Notes |
|----------|-------------|----------|-----------|-------|
| `NEXT_PUBLIC_COOKIE_DOMAIN` | Cookie domain | No | `.amplifyapp.com` | Use your custom domain if configured |
| `NEXT_PUBLIC_SECURE_COOKIES` | Enable HTTPS-only cookies | No | `true` | Must be `true` for AWS |
| `NEXT_PUBLIC_COOKIE_SAMESITE` | Cookie SameSite policy | No | `lax` | Use `lax` for cross-domain |
| `NEXT_PUBLIC_COOKIE_PATH` | Cookie path | No | `/` | Default is fine |
| `NEXT_PUBLIC_ACCESS_TOKEN_COOKIE` | Access token cookie name | No | `access_token` | Default is fine |
| `NEXT_PUBLIC_REFRESH_TOKEN_COOKIE` | Refresh token cookie name | No | `refresh_token` | Default is fine |

### Application Configuration

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_APP_NAME` | Application name | No | `TodoApp` |
| `NEXT_PUBLIC_APP_URL` | Application URL | No | Your Amplify URL |

---

## How to Set Environment Variables

### For Backend (Lambda)

#### Option 1: Using Serverless Framework

1. Create a `.env` file in the `backend` directory
2. Add all required variables
3. Deploy with: `serverless deploy`

The `serverless.yml` file automatically reads from `.env` and passes variables to Lambda.

#### Option 2: Using AWS SAM

1. Deploy with parameters:
```bash
sam deploy --guided \
  --parameter-overrides \
    DatabaseURL="postgresql://..." \
    SecretKey="your-secret-key" \
    RefreshTokenSecret="your-refresh-secret" \
    # ... add all other parameters
```

#### Option 3: Using AWS Console

1. Go to AWS Lambda Console
2. Select your function
3. Navigate to **Configuration > Environment variables**
4. Click **Edit** and add each variable

#### Option 4: Using AWS CLI

```bash
aws lambda update-function-configuration \
  --function-name todo-api \
  --environment Variables="{
    DATABASE_URL=postgresql://...,
    SECRET_KEY=your-secret-key,
    REFRESH_TOKEN_SECRET=your-refresh-secret,
    CORS_ORIGINS=https://yourdomain.amplifyapp.com,
    ...
  }"
```

### For Frontend (Amplify)

#### Via Amplify Console (Recommended)

1. Open AWS Amplify Console
2. Select your app
3. Go to **App Settings > Environment variables**
4. Click **Manage variables**
5. Add each variable with its value
6. Click **Save**
7. Redeploy the app

#### Via Amplify CLI

```bash
# Set individual variables
amplify env add \
  NEXT_PUBLIC_API_URL https://xxxxx.execute-api.us-east-1.amazonaws.com/Prod

# Or create .env file and bulk import via console
```

---

## Security Best Practices

### Secret Management

1. **Never commit secrets to Git**
   - Add `.env` to `.gitignore`
   - Use `.env.example` files as templates

2. **Use AWS Secrets Manager** (Optional but Recommended)
   - Store sensitive values (DATABASE_URL, API keys)
   - Update Lambda to fetch from Secrets Manager
   - Rotate secrets regularly

3. **Generate Strong Secrets**
   ```bash
   # Generate SECRET_KEY
   openssl rand -hex 32

   # Generate REFRESH_TOKEN_SECRET (different from SECRET_KEY!)
   openssl rand -hex 32
   ```

4. **Use Different Secrets for Different Environments**
   - Development, staging, and production should use different secrets

### CORS Configuration

- For production, specify exact origins instead of `*`
- Example: `CORS_ORIGINS=https://yourdomain.amplifyapp.com,https://www.yourdomain.com`

### Database Connection

- Always use SSL for database connections (`sslmode=require`)
- Keep Neon PostgreSQL for simplicity, or migrate to AWS RDS
- Configure connection pooling in Lambda

---

## Quick Setup Checklist

### Backend Lambda

- [ ] `DATABASE_URL` - Neon PostgreSQL connection string
- [ ] `SECRET_KEY` - Generated with `openssl rand -hex 32`
- [ ] `REFRESH_TOKEN_SECRET` - Different from SECRET_KEY
- [ ] `CORS_ORIGINS` - Your Amplify URL
- [ ] `EMAIL_FROM_ADDRESS` - Verified email address
- [ ] `SENDGRID_API_KEY` or SES credentials
- [ ] `FRONTEND_URL` - Your Amplify URL
- [ ] `OPENAI_API_KEY` - For chatbot (optional)

### Frontend Amplify

- [ ] `NEXT_PUBLIC_API_URL` - Lambda API Gateway URL
- [ ] `BETTER_AUTH_SECRET` - Same as backend SECRET_KEY
- [ ] `BETTER_AUTH_URL` - Your Amplify URL
- [ ] `NEXT_PUBLIC_COOKIE_DOMAIN` - `.amplifyapp.com` or your domain
- [ ] `NEXT_PUBLIC_SECURE_COOKIES` - Set to `true`
- [ ] `NEXT_PUBLIC_COOKIE_SAMESITE` - Set to `lax`

---

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure `CORS_ORIGINS` in Lambda includes your Amplify URL
   - Check that URLs don't have trailing slashes

2. **Auth Issues**
   - Verify `BETTER_AUTH_SECRET` matches `SECRET_KEY` exactly
   - Ensure cookies are configured correctly (`secure`, `sameSite`)

3. **Database Connection Errors**
   - Verify `DATABASE_URL` format is correct
   - Check Lambda has internet access (VPC configuration)
   - Ensure `sslmode=require` is present for Neon

4. **API Not Found (404)**
   - Verify `NEXT_PUBLIC_API_URL` points to correct API Gateway URL
   - Include `/Prod` stage in URL if using SAM
   - Check Lambda function is deployed successfully

---

## Need Help?

- Check AWS Lambda logs in CloudWatch
- Check Amplify build logs in Amplify Console
- Verify all required environment variables are set
- Test each service independently (backend, frontend, database)
