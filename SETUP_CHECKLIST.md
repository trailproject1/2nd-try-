# ✅ Setup Checklist

Use this checklist to ensure everything is configured correctly.

## Prerequisites

- [ ] Python 3.11+ installed
- [ ] pip or poetry installed
- [ ] Git installed
- [ ] Telegram account
- [ ] Administrator access to test group

## Step 1: Create Telegram Bot

- [ ] Start [@BotFather](https://t.me/BotFather) on Telegram
- [ ] Send `/newbot` command
- [ ] Follow prompts to create new bot
- [ ] Copy bot token (keep it secret!)
- [ ] Send `/setcommands` to BotFather
- [ ] Add these commands:
  ```
  clean - Delete all tracked messages
  auto - Enable/disable auto-delete
  time - Set delete timer
  status - Show bot status
  help - Show help message
  start - Show help message
  ```
- [ ] Optional: Set bot description and commands list

## Step 2: Setup Local Environment

- [ ] Clone repository
  ```bash
  git clone https://github.com/yourusername/telegram-chat-cleaner.git
  cd telegram-chat-cleaner
  ```

- [ ] Create virtual environment
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  ```

- [ ] Install dependencies
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Create `.env` file
  ```bash
  cp .env.example .env
  ```

- [ ] Edit `.env` and add:
  ```
  BOT_TOKEN=your_bot_token_from_botfather
  LOG_LEVEL=INFO
  ```

## Step 3: Test Locally

- [ ] Verify bot token is correct
  ```bash
  python main.py
  # Should show: "Bot initialized with token: abc123..."
  ```

- [ ] Create test Telegram group
- [ ] Add bot to group
- [ ] Promote bot to administrator
- [ ] Give bot "Delete Messages" permission
- [ ] Verify bot shows: "✅ Setup Complete"
- [ ] Test commands in group:
  - [ ] `/help` - Should show help message
  - [ ] `/status` - Should show bot status
  - [ ] `/auto on` - Enable auto-delete
  - [ ] `/time 2` - Set timer to 2 minutes
  - [ ] Send test messages - Should be deleted after 2 minutes
  - [ ] `/clean` - Should delete all tracked messages
  - [ ] `/auto off` - Disable auto-delete

## Step 4: Verify Functionality

### Message Tracking

- [ ] Send text message in test group
- [ ] Send photo
- [ ] Send video
- [ ] Send document
- [ ] Send voice message
- [ ] Send sticker/GIF
- [ ] Pin a message - Should NOT be deleted
- [ ] Send message as admin - Should NOT be deleted
- [ ] All non-admin messages deleted after timer

### Admin Commands

- [ ] Only admins can use `/clean`, `/auto`, `/time`
- [ ] Non-admin users get "administrator only" message
- [ ] Disable auto-delete and send messages - Messages remain
- [ ] Enable auto-delete and send messages - Messages scheduled for deletion

### Logging

- [ ] Check `logs/bot.log` exists
  ```bash
  tail -f logs/bot.log
  ```
- [ ] Verify messages appear:
  ```
  Scheduled deletion for message
  Deleted message
  Auto-delete set to
  ```

## Step 5: Multiple Group Testing

- [ ] Create second test group
- [ ] Add bot to second group
- [ ] Configure different settings:
  - Group 1: 5 minute timer, auto-delete ON
  - Group 2: 10 minute timer, auto-delete OFF
- [ ] Verify independent operation
- [ ] Check database settings are separate

## Step 6: Permission Validation

- [ ] Remove "Delete Messages" permission from bot
- [ ] Send message - Should get warning about missing permission
- [ ] Restore permission
- [ ] Test deletion again - Should work

- [ ] Demote bot from admin
- [ ] Send message - Should get permission warning
- [ ] Re-promote as admin
- [ ] Test deletion again - Should work

## Step 7: Error Handling

- [ ] Stop the bot (Ctrl+C)
- [ ] Send messages in group (won't be deleted)
- [ ] Restart bot
- [ ] Verify scheduled deletions still execute
- [ ] Check error logs: `logs/bot_errors.log`

## Step 8: Database Verification

- [ ] Install SQLite browser (optional):
  ```bash
  sudo apt install sqlitebrowser  # Linux
  brew install sqlitebrowser      # macOS
  ```

- [ ] Open `data/bot.db` with SQLite browser
- [ ] Verify tables created:
  - [ ] `group_settings`
  - [ ] `tracked_messages`
  - [ ] `admin_logs`

- [ ] Check group settings:
  ```sql
  SELECT * FROM group_settings;
  ```

- [ ] Check tracked messages:
  ```sql
  SELECT * FROM tracked_messages;
  ```

- [ ] Check admin logs:
  ```sql
  SELECT * FROM admin_logs;
  ```

## Step 9: Production Deployment (Choose One)

### Option A: Railway.app

- [ ] Push code to GitHub
- [ ] Create Railway account
- [ ] Connect GitHub repository
- [ ] Add environment variables
- [ ] Deploy
- [ ] Test bot in production group

### Option B: Render.com

- [ ] Push code to GitHub
- [ ] Create Render account
- [ ] Create Web Service
- [ ] Configure build and start commands
- [ ] Add environment variables
- [ ] Deploy
- [ ] Test bot

### Option C: DigitalOcean VPS

- [ ] Create droplet
- [ ] SSH and setup Python
- [ ] Clone repository
- [ ] Setup systemd service
- [ ] Start service
- [ ] Verify logs: `sudo journalctl -u telegram-bot -f`
- [ ] Test bot

### Option D: Docker

- [ ] Build image: `docker build -t telegram-bot .`
- [ ] Create `.env` file
- [ ] Run: `docker-compose up -d`
- [ ] View logs: `docker-compose logs -f`
- [ ] Test bot

## Step 10: Monitoring Setup

- [ ] Check logs regularly:
  ```bash
  tail -f logs/bot.log
  ```

- [ ] Monitor disk space:
  ```bash
  df -h
  ```

- [ ] Monitor memory:
  ```bash
  free -h
  ```

- [ ] Setup log rotation (if on VPS):
  ```bash
  sudo nano /etc/logrotate.d/telegram-bot
  ```

## Step 11: Documentation

- [ ] Update README with your contact info
- [ ] Document any custom configurations
- [ ] Create backup procedure
- [ ] Document recovery procedure
- [ ] Share setup guide with team

## Step 12: Final Verification

- [ ] Bot is running 24/7
- [ ] Bot responds to all commands
- [ ] Database is persistent
- [ ] Logs are being recorded
- [ ] Errors are handled gracefully
- [ ] No crashes or memory leaks
- [ ] Test in 3+ groups simultaneously
- [ ] Monitor for 24 hours minimum

## Troubleshooting

### Bot not starting?
```bash
python main.py
# Check for Python/dependency errors
```

### Bot not deleting messages?
```bash
# Check bot is admin
# Check "Delete Messages" permission
# View logs: tail -f logs/bot.log
```

### Permission errors?
```bash
# Verify bot token
# Check group exists
# Verify bot is in group
```

### Database errors?
```bash
# Backup database: cp data/bot.db data/bot.db.backup
# Delete and restart: rm data/bot.db
# Check logs for SQL errors
```

## Quick Commands Reference

```bash
# Start bot
python main.py

# View logs
tail -f logs/bot.log

# View errors only
tail -f logs/bot_errors.log

# Reset database (CAREFUL!)
rm data/bot.db

# Check bot is running
pgrep -f "python main.py"

# Kill bot
pkill -f "python main.py"

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Quick Telegram Test

Send these messages to test group to verify everything works:

1. Regular text message → Should delete after timer
2. `/status` → Should show bot status
3. `/time 2` → Set timer to 2 minutes
4. Send message → Should delete after 2 minutes
5. `/auto off` → Disable auto-delete
6. Send message → Should NOT delete
7. `/clean` → Should delete all remaining tracked messages

---

## ✅ All Done!

If you've completed all checkboxes, your bot is ready for production!

**Next Steps:**
- Monitor logs daily
- Setup automated backups
- Create documentation for your team
- Plan for scaling if needed

**Need Help?**
- Check README.md
- Check DEPLOYMENT_GUIDE.md
- Review logs for errors
- Check Telegram Bot API documentation
