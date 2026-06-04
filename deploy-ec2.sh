#!/bin/bash

# ============================================
# AWS EC2 Deployment Script for Todo App
# ============================================
# Run this script on your EC2 instance after cloning the repo
# Usage: bash deploy-ec2.sh

set -e  # Exit on error

echo "=========================================="
echo "   Todo App EC2 Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Ubuntu
if [ ! -f /etc/os-release ]; then
    print_error "Cannot determine OS. This script is designed for Ubuntu."
    exit 1
fi

source /etc/os-release
if [ "$ID" != "ubuntu" ]; then
    print_error "This script is designed for Ubuntu. Detected: $ID"
    exit 1
fi

print_info "Detected Ubuntu $VERSION_ID"

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
print_info "Project root: $PROJECT_ROOT"

# ============================================
# Step 1: Check if .env files exist
# ============================================
echo ""
print_info "Checking environment files..."

if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
    print_warning "Backend .env file not found!"
    print_info "Please create backend/.env file using backend/.env.ec2.example as template"
    read -p "Press Enter to continue after creating the file, or Ctrl+C to exit..."
fi

if [ ! -f "$PROJECT_ROOT/frontend/.env.production" ]; then
    print_warning "Frontend .env.production file not found!"
    print_info "Please create frontend/.env.production using frontend/.env.ec2.example as template"
    read -p "Press Enter to continue after creating the file, or Ctrl+C to exit..."
fi

# ============================================
# Step 2: Install Backend Dependencies
# ============================================
echo ""
print_info "Setting up backend..."

cd "$PROJECT_ROOT/backend"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_info "Creating Python virtual environment..."
    python3.11 -m venv .venv
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
print_info "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_info "Backend setup complete!"

# ============================================
# Step 3: Install Frontend Dependencies
# ============================================
echo ""
print_info "Setting up frontend..."

cd "$PROJECT_ROOT/frontend"

# Install dependencies
print_info "Installing frontend dependencies..."
npm install

# Build frontend
print_info "Building frontend (this may take a few minutes)..."
npm run build

print_info "Frontend setup complete!"

# ============================================
# Step 4: Setup PM2 Processes
# ============================================
echo ""
print_info "Setting up PM2 processes..."

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    print_error "PM2 is not installed. Please install it with: sudo npm install -g pm2"
    exit 1
fi

# Stop existing processes if they exist
pm2 delete todo-backend 2>/dev/null || true
pm2 delete todo-frontend 2>/dev/null || true

# Start backend
print_info "Starting backend with PM2..."
cd "$PROJECT_ROOT/backend"
pm2 start "source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000" \
    --name "todo-backend" \
    --interpreter bash \
    --cwd "$PROJECT_ROOT/backend"

# Start frontend
print_info "Starting frontend with PM2..."
cd "$PROJECT_ROOT/frontend"
pm2 start npm --name "todo-frontend" -- start

# Save PM2 configuration
print_info "Saving PM2 configuration..."
pm2 save

print_info "PM2 setup complete!"

# ============================================
# Step 5: Display Status
# ============================================
echo ""
echo "=========================================="
echo "   Deployment Complete!"
echo "=========================================="
echo ""

pm2 list

echo ""
print_info "Your Todo App is now running!"
echo ""
echo "Backend API: http://$(curl -s http://checkip.amazonaws.com):8000"
echo "Frontend:    http://$(curl -s http://checkip.amazonaws.com):3000"
echo "Health:      http://$(curl -s http://checkip.amazonaws.com):8000/health"
echo ""
print_info "Useful commands:"
echo "  - View logs:        pm2 logs"
echo "  - Restart backend:  pm2 restart todo-backend"
echo "  - Restart frontend: pm2 restart todo-frontend"
echo "  - Monitor:          pm2 monit"
echo ""
print_warning "Don't forget to update your security group to allow traffic on ports 3000 and 8000!"
echo ""
