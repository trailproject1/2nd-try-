# 🚀 Deployment Guide

Comprehensive guide for deploying the Telegram Chat Cleaner Bot to various platforms.

## Table of Contents

1. [Local Development](#local-development)
2. [Railway.app](#railwayapp)
3. [Render.com](#rendercom)
4. [DigitalOcean VPS](#digitalocean-vps)
5. [AWS](#aws-ec2)
6. [Docker](#docker)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development

### Requirements
- Python 3.11+
- pip or poetry
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/telegram-chat-cleaner.git
cd telegram-chat-cleaner

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add your BOT_TOKEN

# Run
python main.py
```

### Testing Locally

1. Create test group on Telegram
2. Add bot to test group
3. Promote bot to admin
4. Grant "Delete Messages" permission
5. Send test messages and verify deletion

---

## Railway.app

**Best for:** Beginners, free tier available, easy setup

### Prerequisites
- GitHub account
- Railway account

### Step-by-Step

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/telegram-chat-cleaner.git
   git push -u origin main
   ```

2. **Create Railway Project**
   - Go to [Railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub
   - Select your repository

3. **Configure Environment Variables**
   - Go to "Variables" tab
   - Click "Add Variable"
   - Add from `.env` file:
     ```
     BOT_TOKEN=your_bot_token_here
     LOG_LEVEL=INFO
     DATABASE_PATH=data/bot.db
     DEFAULT_DELETE_TIME_MINUTES=10
     ENABLE_AUTO_DELETE_BY_DEFAULT=true
     ```

4. **Deploy**
   - Railway auto-detects Python
   - Builds and deploys automatically
   - View logs in "Logs" tab

5. **Monitor**
   ```bash
   # View real-time logs
   # In Railway dashboard: Logs tab
   
   # Or use Railway CLI
   railway login
   railway logs --follow
   ```

### Railway Useful Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link <project-id>

# View logs
railway logs --follow

# Monitor status
railway status
```

---

## Render.com

**Best for:** Reliability, free tier, PostgreSQL integration possible

### Step-by-Step

1. **Push to GitHub** (same as Railway)

2. **Create Render Service**
   - Go to [Render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Choose your repository

3. **Configure Build**
   - **Name:** telegram-chat-cleaner
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Instance Type:** Free (if available)
   - **Auto-deploy:** Enable

4. **Add Environment Variables**
   - In dashboard, go to "Environment"
   - Add variables:
     ```
     BOT_TOKEN=your_bot_token
     LOG_LEVEL=INFO
     DATABASE_PATH=data/bot.db
     ```

5. **Deploy**
   - Click "Create Web Service"
   - Render deploys automatically
   - Check "Logs" tab for output

### Persistent Storage on Render

For persistent database:

1. Create Render Disk
2. Mount at `/data` directory
3. Update `.env`:
   ```
   DATABASE_PATH=/data/bot.db
   LOG_DIR=/data/logs
   ```

---

## DigitalOcean VPS

**Best for:** Control, cost-effective, production-grade

### Prerequisites
- DigitalOcean account
- SSH client

### Step-by-Step

1. **Create Droplet**
   - **Image:** Ubuntu 22.04 LTS
   - **Size:** $5/month basic (sufficient)
   - **Region:** Choose closest to you
   - **Authentication:** SSH key recommended

2. **Initial Setup**
   ```bash
   ssh root@your_droplet_ip
   
   # Update system
   apt update && apt upgrade -y
   
   # Install dependencies
   apt install -y python3.11 python3.11-venv python3-pip git curl
   
   # Create app directory
   mkdir -p /opt/telegram-bot
   cd /opt/telegram-bot
   ```

3. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/telegram-chat-cleaner.git .
   ```

4. **Setup Virtual Environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Add BOT_TOKEN
   ```

6. **Create Systemd Service**
   ```bash
   sudo tee /etc/systemd/system/telegram-bot.service > /dev/null << EOF
   [Unit]
   Description=Telegram Chat Cleaner Bot
   After=network.target
   Wants=network-online.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/opt/telegram-bot
   Environment="PATH=/opt/telegram-bot/venv/bin"
   ExecStart=/opt/telegram-bot/venv/bin/python main.py
   Restart=always
   RestartSec=10
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   EOF
   ```

7. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable telegram-bot
   sudo systemctl start telegram-bot
   sudo systemctl status telegram-bot
   ```

8. **View Logs**
   ```bash
   # Real-time logs
   sudo journalctl -u telegram-bot -f
   
   # Last 100 lines
   sudo journalctl -u telegram-bot -n 100
   ```

### Firewall Setup (UFW)

```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTPS (if needed for webhooks)
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### Automated Backups

Create backup script (`/opt/telegram-bot/backup.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/opt/telegram-bot/backups"
mkdir -p $BACKUP_DIR

# Backup database
cp /opt/telegram-bot/data/bot.db "$BACKUP_DIR/bot.db.$(date +%Y%m%d_%H%M%S).bak"

# Keep only last 7 days
find $BACKUP_DIR -name "*.bak" -mtime +7 -delete

echo "Backup completed"
```

Add to crontab:
```bash
sudo crontab -e
# Add: 0 2 * * * /opt/telegram-bot/backup.sh
```

---

## AWS EC2

**Best for:** Scalability, production enterprise

### Step-by-Step

1. **Launch EC2 Instance**
   - AMI: Ubuntu Server 22.04 LTS
   - Type: t3.micro (free tier eligible)
   - Security Group: Allow SSH (22), HTTP (80), HTTPS (443)

2. **Connect & Setup**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   
   # Update
   sudo apt update && sudo apt upgrade -y
   
   # Install Python
   sudo apt install -y python3.11 python3.11-venv git
   ```

3. **Install Bot**
   ```bash
   git clone https://github.com/yourusername/telegram-chat-cleaner.git
   cd telegram-chat-cleaner
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Setup with Systemd** (same as DigitalOcean)

5. **CloudWatch Monitoring**
   ```bash
   # Install CloudWatch agent
   wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
   sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
   ```

6. **S3 Backups**
   ```bash
   sudo apt install awscli
   aws configure  # Add credentials
   
   # Create backup script
   aws s3 cp /opt/telegram-bot/data/bot.db s3://your-bucket/backups/
   ```

---

## Docker

**Best for:** Containerization, consistency across environments

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Run bot
CMD ["python", "main.py"]
```

### Build & Run

```bash
# Build image
docker build -t telegram-chat-cleaner .

# Run container
docker run -d \
  --name telegram-bot \
  -e BOT_TOKEN=your_token \
  -e LOG_LEVEL=INFO \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  telegram-chat-cleaner

# View logs
docker logs -f telegram-bot

# Stop container
docker stop telegram-bot
```

### Docker Compose

```yaml
version: '3.8'

services:
  telegram-bot:
    build: .
    container_name: telegram-chat-cleaner
    restart: always
    environment:
      BOT_TOKEN: ${BOT_TOKEN}
      LOG_LEVEL: INFO
      DATABASE_PATH: /app/data/bot.db
      LOG_DIR: /app/logs
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Run with Docker Compose:
```bash
docker-compose up -d
docker-compose logs -f
```

---

## Monitoring & Maintenance

### Health Checks

Create health check script:

```bash
#!/bin/bash
# Check if process is running
if pgrep -f "python main.py" > /dev/null; then
    echo "Bot is running"
    exit 0
else
    echo "Bot crashed - restarting"
    systemctl restart telegram-bot
    exit 1
fi
```

Schedule with cron:
```bash
# Every 5 minutes
*/5 * * * * /opt/telegram-bot/health-check.sh
```

### Log Rotation

Configure with logrotate (`/etc/logrotate.d/telegram-bot`):

```
/opt/telegram-bot/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload telegram-bot > /dev/null 2>&1 || true
    endscript
}
```

### Database Maintenance

```bash
# Optimize database
sqlite3 /opt/telegram-bot/data/bot.db "VACUUM;"

# Check database integrity
sqlite3 /opt/telegram-bot/data/bot.db "PRAGMA integrity_check;"
```

### Performance Monitoring

```bash
# Monitor resource usage
watch -n 1 'ps aux | grep python'

# Check memory usage
free -h

# Disk space
df -h
```

---

## Troubleshooting Deployments

### Bot not starting

```bash
# Check logs
sudo journalctl -u telegram-bot -n 50

# Verify Python installation
python3 --version

# Check virtual environment
source /opt/telegram-bot/venv/bin/activate
python -c "import telegram"
```

### Database errors

```bash
# Check database
sqlite3 /path/to/bot.db ".tables"

# Backup and reset
cp bot.db bot.db.backup
rm bot.db
# Restart bot to recreate
```

### Memory leaks

```bash
# Monitor memory usage
watch -n 1 'ps aux | grep python | grep -v grep'

# Restart service weekly (cron)
0 2 * * 0 systemctl restart telegram-bot
```

---

## Cost Comparison

| Platform | Free Tier | Min Cost | Best For |
|----------|-----------|----------|----------|
| Railway | 5$/month credit | $5/month | Beginners |
| Render | Limited | $7/month | Reliability |
| DigitalOcean | None | $5/month | Full control |
| AWS | EC2 1yr free | $0-10/month | Enterprise |
| Docker | Free (self-hosted) | Cost varies | Dev/Prod parity |

---

**Need help?** Check logs and review configuration. Most issues are permission-related.
