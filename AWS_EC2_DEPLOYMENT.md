# AWS EC2 Deployment Guide
# Complete Todo App Deployment on AWS EC2

This guide will help you deploy both the **backend (FastAPI)** and **frontend (Next.js)** on a single AWS EC2 instance.

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ AWS Account (https://aws.amazon.com/)
- ✅ Neon PostgreSQL Database URL
- ✅ Git installed on your local machine
- ✅ Basic knowledge of AWS Console

---

## 🚀 Step 1: Launch EC2 Instance

### 1.1 Go to AWS EC2 Console
1. Sign in to AWS Console: https://console.aws.amazon.com/ec2/
2. Click **"Launch Instance"**

### 1.2 Configure Instance
**Name:** `todo-app-server`

**Application and OS Images:**
- Choose: **Ubuntu Server 22.04 LTS**
- Architecture: **64-bit (x86)**

**Instance Type:**
- Choose: **t2.medium** (recommended) or **t2.small** (minimum)
- t2.micro may be too slow for both frontend and backend

**Key Pair:**
1. Click **"Create new key pair"**
2. Name: `todo-app-key`
3. Type: **RSA**
4. Format: **.pem** (for Mac/Linux) or **.ppk** (for Windows/PuTTY)
5. Download and **save securely** - you'll need this to connect!

**Network Settings:**
Click **"Edit"** and configure:
- Auto-assign public IP: **Enable**
- Firewall (Security Group): **Create new security group**
  - Security group name: `todo-app-sg`

**Add these Security Group Rules:**

| Type | Port | Source | Description |
|------|------|--------|-------------|
| SSH | 22 | My IP | SSH access |
| HTTP | 80 | 0.0.0.0/0 | HTTP traffic |
| HTTPS | 443 | 0.0.0.0/0 | HTTPS traffic |
| Custom TCP | 3000 | 0.0.0.0/0 | Next.js frontend |
| Custom TCP | 8000 | 0.0.0.0/0 | FastAPI backend |

**Storage:**
- Size: **20 GB** (minimum)
- Type: **gp3** (General Purpose SSD)

### 1.3 Launch Instance
1. Review all settings
2. Click **"Launch Instance"**
3. Wait for instance to be **"Running"** (1-2 minutes)
4. Note down your **Public IPv4 address** (e.g., `3.110.123.45`)

---

## 🔌 Step 2: Connect to EC2 Instance

### 2.1 For Windows Users

**Option A: Using Git Bash (Recommended)**
```bash
# Set key permissions
chmod 400 todo-app-key.pem

# Connect to EC2
ssh -i "todo-app-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

**Option B: Using PuTTY**
1. Open PuTTY
2. Host Name: `ubuntu@YOUR_EC2_PUBLIC_IP`
3. Connection → SSH → Auth → Browse to your `.ppk` key
4. Click **Open**

### 2.2 For Mac/Linux Users
```bash
# Set key permissions
chmod 400 todo-app-key.pem

# Connect to EC2
ssh -i "todo-app-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## 📦 Step 3: Install Required Software

Once connected to EC2, run these commands:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Node.js 20.x (for Next.js frontend)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify Node.js installation
node --version  # Should show v20.x.x
npm --version   # Should show 10.x.x

# Install Python 3.11 (for FastAPI backend)
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Verify Python installation
python3.11 --version  # Should show Python 3.11.x

# Install Git
sudo apt install -y git

# Install Nginx (web server/reverse proxy)
sudo apt install -y nginx

# Install PM2 (process manager for Node.js)
sudo npm install -g pm2

# Install certbot (for SSL certificates - optional)
sudo apt install -y certbot python3-certbot-nginx
```

---

## 📥 Step 4: Clone Your Repository

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/Farhat-Naz/phaseIII-todo.git
cd phaseIII-todo

# Checkout your branch
git checkout 008-mcp-chatbot
```

---

## 🔧 Step 5: Setup Backend (FastAPI)

### 5.1 Create Backend Environment File
```bash
cd ~/phaseIII-todo/backend

# Create .env file
nano .env
```

**Paste this configuration** (update with your values):
```env
# Database Configuration
DATABASE_URL=postgresql+psycopg://neondb_owner:YOUR_PASSWORD@YOUR_HOST.neon.tech/neondb?sslmode=require

# JWT Authentication
SECRET_KEY=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64
REFRESH_TOKEN_SECRET=b45b9856c0edd136fd92777b415428a9609ac01730a0551879ff7b9893fecb88
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Settings (use your EC2 public IP)
CORS_ORIGINS=http://YOUR_EC2_PUBLIC_IP:3000,http://YOUR_EC2_PUBLIC_IP
FRONTEND_URL=http://YOUR_EC2_PUBLIC_IP:3000

# Application Settings
ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Email Configuration (optional)
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your_sendgrid_api_key
EMAIL_FROM_ADDRESS=noreply@yourdomain.com
EMAIL_FROM_NAME=TodoApp

# AI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key
AI_MODEL=gpt-4o
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

### 5.2 Install Backend Dependencies
```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 5.3 Test Backend
```bash
# Start backend temporarily to test
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Test in browser:** `http://YOUR_EC2_PUBLIC_IP:8000/health`

You should see: `{"status":"healthy","version":"1.0.0"}`

Press `Ctrl+C` to stop the test server.

---

## 🎨 Step 6: Setup Frontend (Next.js)

### 6.1 Create Frontend Environment File
```bash
cd ~/phaseIII-todo/frontend

# Create .env.production file
nano .env.production
```

**Paste this configuration** (update with your EC2 IP):
```env
# API URL - Points to local backend
NEXT_PUBLIC_API_URL1=http://YOUR_EC2_PUBLIC_IP:8000

# Application Configuration
NEXT_PUBLIC_APP_NAME=TodoApp
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

### 6.2 Install Frontend Dependencies
```bash
# Install dependencies
npm install

# Build the frontend
npm run build
```

This may take 2-5 minutes. Wait for it to complete.

### 6.3 Test Frontend
```bash
# Start frontend temporarily to test
npm start
```

**Test in browser:** `http://YOUR_EC2_PUBLIC_IP:3000`

You should see your Todo app homepage!

Press `Ctrl+C` to stop the test server.

---

## 🔄 Step 7: Setup Process Management with PM2

PM2 will keep your applications running even after you disconnect from SSH.

### 7.1 Start Backend with PM2
```bash
cd ~/phaseIII-todo/backend

# Start backend
pm2 start "source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000" --name "todo-backend" --interpreter bash
```

### 7.2 Start Frontend with PM2
```bash
cd ~/phaseIII-todo/frontend

# Start frontend
pm2 start npm --name "todo-frontend" -- start
```

### 7.3 Save PM2 Configuration
```bash
# Save current process list
pm2 save

# Setup PM2 to start on system boot
pm2 startup
# Copy and run the command that PM2 outputs
```

### 7.4 Check PM2 Status
```bash
pm2 list
pm2 logs
```

---

## 🌐 Step 8: Configure Nginx Reverse Proxy (Optional but Recommended)

This allows you to:
- Access frontend at `http://YOUR_EC2_PUBLIC_IP` (port 80)
- Access backend at `http://YOUR_EC2_PUBLIC_IP/api`
- Add SSL certificate later

### 8.1 Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/todo-app
```

**Paste this configuration:**
```nginx
server {
    listen 80;
    server_name YOUR_EC2_PUBLIC_IP;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API (FastAPI)
    location /api {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

### 8.2 Enable Nginx Configuration
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/todo-app /etc/nginx/sites-enabled/

# Remove default configuration
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 8.3 Update Frontend Environment
If using Nginx proxy, update frontend to use relative API path:

```bash
cd ~/phaseIII-todo/frontend
nano .env.production
```

Change:
```env
NEXT_PUBLIC_API_URL1=/api
```

Then rebuild:
```bash
npm run build
pm2 restart todo-frontend
```

---

## 🔒 Step 9: Setup SSL Certificate (Optional - For Custom Domain)

If you have a custom domain (e.g., `todoapp.yourdomain.com`):

```bash
# Point your domain A record to EC2 public IP first!

# Install SSL certificate
sudo certbot --nginx -d todoapp.yourdomain.com

# Auto-renewal
sudo systemctl status certbot.timer
```

---

## ✅ Step 10: Verify Deployment

### 10.1 Check Backend
```bash
curl http://YOUR_EC2_PUBLIC_IP:8000/health
# Should return: {"status":"healthy","version":"1.0.0"}
```

### 10.2 Check Frontend
Visit in browser: `http://YOUR_EC2_PUBLIC_IP:3000`

### 10.3 Check PM2 Status
```bash
pm2 status
pm2 logs
```

### 10.4 Test Application Features
1. ✅ Sign up with new account
2. ✅ Login
3. ✅ Create todo
4. ✅ Complete todo
5. ✅ Delete todo

---

## 📊 Useful Commands

### View Logs
```bash
# Backend logs
pm2 logs todo-backend

# Frontend logs
pm2 logs todo-frontend

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
# Restart backend
pm2 restart todo-backend

# Restart frontend
pm2 restart todo-frontend

# Restart Nginx
sudo systemctl restart nginx
```

### Update Code
```bash
cd ~/phaseIII-todo

# Pull latest changes
git pull origin 008-mcp-chatbot

# Update backend
cd backend
source .venv/bin/activate
pip install -r requirements.txt
pm2 restart todo-backend

# Update frontend
cd ../frontend
npm install
npm run build
pm2 restart todo-frontend
```

### Monitor Resources
```bash
# CPU and memory usage
htop

# Disk usage
df -h

# PM2 monitoring
pm2 monit
```

---

## 🛡️ Security Best Practices

1. **Firewall:** Only open required ports (22, 80, 443)
2. **SSH Keys:** Never share your `.pem` key file
3. **Environment Variables:** Keep `.env` files secure, never commit to Git
4. **Updates:** Regularly update system packages
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
5. **Backups:** Regular database backups from Neon dashboard
6. **Monitoring:** Set up CloudWatch alarms for CPU/memory

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check logs
pm2 logs todo-backend

# Check if port 8000 is in use
sudo lsof -i :8000

# Restart backend
pm2 restart todo-backend
```

### Frontend won't start
```bash
# Check logs
pm2 logs todo-frontend

# Check if port 3000 is in use
sudo lsof -i :3000

# Rebuild and restart
cd ~/phaseIII-todo/frontend
npm run build
pm2 restart todo-frontend
```

### Can't connect to EC2
- Check security group allows your IP on port 22
- Verify key file permissions: `chmod 400 todo-app-key.pem`
- Check instance is running in EC2 console

### Database connection issues
- Verify DATABASE_URL in backend `.env`
- Check Neon database is running
- Test connection from EC2

---

## 📝 URLs After Deployment

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | `http://YOUR_EC2_PUBLIC_IP:3000` | Next.js application |
| **Backend API** | `http://YOUR_EC2_PUBLIC_IP:8000` | FastAPI endpoints |
| **Health Check** | `http://YOUR_EC2_PUBLIC_IP:8000/health` | Backend health status |
| **API Docs** | `http://YOUR_EC2_PUBLIC_IP:8000/docs` | Swagger UI documentation |

### With Nginx Proxy:
| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | `http://YOUR_EC2_PUBLIC_IP` | Next.js application (port 80) |
| **Backend API** | `http://YOUR_EC2_PUBLIC_IP/api` | FastAPI endpoints proxied |

---

## 💰 Cost Estimation

**Monthly AWS Costs** (approximate):
- t2.medium EC2: ~$30/month
- t2.small EC2: ~$15/month
- 20 GB EBS Storage: ~$2/month
- Data Transfer: ~$1-5/month (depends on traffic)

**Total:** ~$17-37/month

**Free Tier:** If using AWS Free Tier (first 12 months):
- 750 hours/month of t2.micro (free)
- 30 GB EBS storage (free)

---

## 🎉 Deployment Complete!

Your Todo app is now live on AWS EC2!

**Next Steps:**
1. Configure custom domain (optional)
2. Set up SSL certificate with Let's Encrypt
3. Configure automated backups
4. Set up monitoring and alerts
5. Configure CI/CD for automatic deployments

**Support:**
- AWS Documentation: https://docs.aws.amazon.com/ec2/
- PM2 Documentation: https://pm2.keymetrics.io/
- Nginx Documentation: https://nginx.org/en/docs/

---

**Last Updated:** 2026-06-04
**Version:** 1.0
