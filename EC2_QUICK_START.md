# AWS EC2 Quick Start Guide

This is a condensed guide for quickly deploying your Todo App on AWS EC2.

For detailed instructions, see [AWS_EC2_DEPLOYMENT.md](./AWS_EC2_DEPLOYMENT.md)

---

## 🚀 Quick Deployment (5 Steps)

### Step 1: Launch EC2 Instance

1. Go to: https://console.aws.amazon.com/ec2/
2. Click **Launch Instance**
3. Configure:
   - **Name:** `todo-app-server`
   - **OS:** Ubuntu Server 22.04 LTS
   - **Instance Type:** t2.medium (or t2.small minimum)
   - **Key Pair:** Create new → Download `.pem` file
   - **Security Group:** Allow ports 22, 80, 443, 3000, 8000
   - **Storage:** 20 GB
4. Launch and note your **Public IP**

---

### Step 2: Connect to EC2

**Windows (Git Bash):**
```bash
chmod 400 todo-app-key.pem
ssh -i "todo-app-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

**Mac/Linux:**
```bash
chmod 400 todo-app-key.pem
ssh -i "todo-app-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

---

### Step 3: Install Software

Run these commands on EC2:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install other tools
sudo apt install -y git nginx
sudo npm install -g pm2

# Verify installations
node --version    # Should show v20.x.x
python3.11 --version  # Should show Python 3.11.x
```

---

### Step 4: Clone and Configure

```bash
# Clone repository
cd ~
git clone https://github.com/Farhat-Naz/phaseIII-todo.git
cd phaseIII-todo
git checkout 008-mcp-chatbot

# Setup backend environment
cd backend
cp .env.ec2.example .env
nano .env
# Update DATABASE_URL and YOUR_EC2_PUBLIC_IP in CORS_ORIGINS

# Setup frontend environment
cd ../frontend
cp .env.ec2.example .env.production
nano .env.production
# Update YOUR_EC2_PUBLIC_IP to your actual IP address
```

---

### Step 5: Deploy with Script

```bash
# Make script executable
chmod +x ~/phaseIII-todo/deploy-ec2.sh

# Run deployment script
cd ~/phaseIII-todo
bash deploy-ec2.sh
```

**The script will:**
- Install all dependencies
- Build the frontend
- Start both backend and frontend with PM2

---

## ✅ Verify Deployment

Check your app is running:

**Backend Health:**
```bash
curl http://YOUR_EC2_PUBLIC_IP:8000/health
```

**Frontend:**
Open browser: `http://YOUR_EC2_PUBLIC_IP:3000`

**PM2 Status:**
```bash
pm2 list
pm2 logs
```

---

## 📋 Important URLs

| Service | URL |
|---------|-----|
| Frontend | `http://YOUR_EC2_PUBLIC_IP:3000` |
| Backend | `http://YOUR_EC2_PUBLIC_IP:8000` |
| API Docs | `http://YOUR_EC2_PUBLIC_IP:8000/docs` |
| Health Check | `http://YOUR_EC2_PUBLIC_IP:8000/health` |

---

## 🔧 Useful Commands

```bash
# View logs
pm2 logs

# Restart services
pm2 restart todo-backend
pm2 restart todo-frontend

# Stop services
pm2 stop todo-backend
pm2 stop todo-frontend

# Update code
cd ~/phaseIII-todo
git pull
bash deploy-ec2.sh

# Monitor resources
pm2 monit
htop
```

---

## 🛡️ Security Checklist

- [ ] Security group only allows required ports
- [ ] SSH key stored securely
- [ ] `.env` files never committed to Git
- [ ] Regular system updates: `sudo apt update && sudo apt upgrade -y`
- [ ] Database backups configured
- [ ] Consider setting up Nginx reverse proxy
- [ ] Consider adding SSL certificate with Certbot

---

## 📞 Need Help?

See detailed guide: [AWS_EC2_DEPLOYMENT.md](./AWS_EC2_DEPLOYMENT.md)

Common issues:
- **Can't connect:** Check security group allows your IP on port 22
- **Port in use:** Check with `sudo lsof -i :8000` or `sudo lsof -i :3000`
- **App won't start:** Check logs with `pm2 logs`
- **Database error:** Verify DATABASE_URL in backend/.env

---

**Deployment Time:** ~15-20 minutes
**Cost:** ~$15-30/month (t2.small to t2.medium)

Good luck! 🚀
