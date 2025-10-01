# Deployment Checklist - Error Handling Improvements

## Pre-Deployment

### 1. Code Review
- [ ] Review all changes in `utils/helpers.py`
- [ ] Review all changes in `ai/vision_analyzer.py`
- [ ] Review all changes in `bot/handlers.py`
- [ ] Verify syntax with `python3 -m py_compile`
- [ ] Check for any TODO or FIXME comments

### 2. Testing
- [ ] Test with normal food photos
- [ ] Test with large images (>5MB)
- [ ] Test with small images (<100KB)
- [ ] Test with different formats (JPG, PNG)
- [ ] Test with blurry/dark images
- [ ] Run `test_image_processing.py` on sample images
- [ ] Verify all error messages display correctly

### 3. Dependencies
- [ ] Verify all dependencies in `requirements.txt` are installed
- [ ] Check numpy version compatibility
- [ ] Check PIL/Pillow version compatibility
- [ ] Verify python-telegram-bot version

### 4. Configuration
- [ ] Verify `.env` file has all required variables
- [ ] Check API keys are valid
- [ ] Verify database connection
- [ ] Check log file permissions

### 5. Backup
- [ ] Backup current production code
- [ ] Backup database
- [ ] Backup configuration files
- [ ] Document current version number

---

## Deployment Steps

### 1. Stop the Bot
```bash
# Find the bot process
ps aux | grep main.py

# Stop the bot gracefully
kill -SIGTERM <process_id>

# Or if using systemd
sudo systemctl stop mealmetrics-bot
```

### 2. Deploy New Code
```bash
# Navigate to bot directory
cd /var/www/MealMetrics

# Pull latest changes (if using git)
git pull origin master

# Or copy files manually
# cp /path/to/new/files/* .

# Verify files are updated
ls -la utils/helpers.py ai/vision_analyzer.py bot/handlers.py
```

### 3. Install/Update Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Verify installations
pip list | grep -E "numpy|pillow|python-telegram-bot"
```

### 4. Run Syntax Check
```bash
python3 -m py_compile utils/helpers.py
python3 -m py_compile ai/vision_analyzer.py
python3 -m py_compile bot/handlers.py
python3 -m py_compile test_image_processing.py
```

### 5. Test Image Processing
```bash
# Test with a sample image
python test_image_processing.py /path/to/test/image.jpg

# Verify all steps pass
```

### 6. Start the Bot
```bash
# Start the bot
python main.py

# Or if using systemd
sudo systemctl start mealmetrics-bot

# Or run in background
nohup python main.py > bot.log 2>&1 &
```

### 7. Verify Bot is Running
```bash
# Check process
ps aux | grep main.py

# Check logs
tail -f mealmetrics.log

# Or if using systemd
sudo systemctl status mealmetrics-bot
```

---

## Post-Deployment

### 1. Immediate Verification (First 5 minutes)
- [ ] Bot responds to /start command
- [ ] Bot responds to /help command
- [ ] Test photo upload with a simple food image
- [ ] Verify analysis completes successfully
- [ ] Check logs for any errors

### 2. Short-term Monitoring (First Hour)
- [ ] Monitor log file for errors
- [ ] Test with various image types
- [ ] Verify error messages are specific
- [ ] Check that fallback mechanisms work
- [ ] Monitor memory usage
- [ ] Monitor CPU usage

### 3. Extended Monitoring (First 24 Hours)
- [ ] Track success rate of photo processing
- [ ] Monitor for any new error patterns
- [ ] Check user feedback/complaints
- [ ] Review log file for warnings
- [ ] Monitor API usage and costs
- [ ] Check database performance

### 4. Error Testing
Test each error scenario to verify messages:

- [ ] **Timeout Error**: Disconnect network briefly during processing
- [ ] **Network Error**: Block API endpoint temporarily
- [ ] **Image Format Error**: Send corrupted image
- [ ] **Size Error**: Send very large image (>10MB)
- [ ] **Enhancement Error**: (Should be caught by fallback)
- [ ] **API Error**: Use invalid API key temporarily

### 5. Performance Metrics
Track these metrics:

- [ ] Average photo processing time
- [ ] Success rate (before vs after)
- [ ] Error rate by type
- [ ] Fallback usage frequency
- [ ] User retry rate
- [ ] API response times

---

## Rollback Procedure

If critical issues are found:

### 1. Immediate Rollback
```bash
# Stop the bot
kill -SIGTERM <process_id>

# Restore backup
cp /backup/utils/helpers.py utils/helpers.py
cp /backup/ai/vision_analyzer.py ai/vision_analyzer.py
cp /backup/bot/handlers.py bot/handlers.py

# Restart bot
python main.py
```

### 2. Verify Rollback
- [ ] Bot is running
- [ ] Photo processing works
- [ ] No errors in logs
- [ ] Users can use bot normally

### 3. Document Issues
- [ ] Document what went wrong
- [ ] Save error logs
- [ ] Note which changes caused issues
- [ ] Plan fixes for next deployment

---

## Monitoring Commands

### Check Bot Status
```bash
# Process status
ps aux | grep main.py

# System service status (if using systemd)
sudo systemctl status mealmetrics-bot
```

### View Logs
```bash
# Tail logs in real-time
tail -f mealmetrics.log

# View last 100 lines
tail -n 100 mealmetrics.log

# Search for errors
grep -i error mealmetrics.log

# Search for specific error types
grep "Image Format Issue" mealmetrics.log
grep "Request Timeout" mealmetrics.log
```

### Monitor Resources
```bash
# CPU and memory usage
top -p <process_id>

# Disk usage
df -h

# Log file size
du -h mealmetrics.log
```

### Test Endpoints
```bash
# Test image processing
python test_image_processing.py /path/to/test/image.jpg

# Check API connectivity
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"google/gemini-2.0-flash-exp","messages":[{"role":"user","content":"test"}]}'
```

---

## Success Criteria

Deployment is successful if:

- ✅ Bot starts without errors
- ✅ Photo processing works for normal images
- ✅ Error messages are specific and helpful
- ✅ Fallback mechanisms activate when needed
- ✅ Logs show detailed information
- ✅ No increase in error rate
- ✅ Performance is maintained or improved
- ✅ Users receive helpful error messages
- ✅ Test script works correctly
- ✅ No critical bugs in first 24 hours

---

## Communication

### Before Deployment
- [ ] Notify users of planned maintenance (if downtime expected)
- [ ] Inform team of deployment schedule
- [ ] Prepare rollback plan

### During Deployment
- [ ] Update status page (if applicable)
- [ ] Monitor for user reports
- [ ] Keep team informed of progress

### After Deployment
- [ ] Announce successful deployment
- [ ] Share new features/improvements
- [ ] Provide feedback channels
- [ ] Document any issues encountered

---

## Documentation Updates

After successful deployment:

- [ ] Update version number in code
- [ ] Update CHANGELOG.md
- [ ] Update README.md if needed
- [ ] Archive old documentation
- [ ] Share new documentation with team

---

## Long-term Monitoring

### Weekly:
- [ ] Review error logs for patterns
- [ ] Check success rate trends
- [ ] Monitor API costs
- [ ] Review user feedback

### Monthly:
- [ ] Analyze error type distribution
- [ ] Review performance metrics
- [ ] Plan improvements based on data
- [ ] Update documentation as needed

---

## Contact Information

### In Case of Issues:
- **Developer**: [Your contact info]
- **System Admin**: [Admin contact info]
- **Emergency**: [Emergency contact]

### Resources:
- **Documentation**: `/var/www/MealMetrics/docs/`
- **Logs**: `/var/www/MealMetrics/mealmetrics.log`
- **Backup**: `/backup/mealmetrics/`
- **Repository**: `https://github.com/mrx-arafat/MealMetrics`

---

## Notes

- Keep this checklist updated with each deployment
- Document any deviations from the plan
- Share lessons learned with the team
- Update procedures based on experience

---

**Deployment Date**: _____________

**Deployed By**: _____________

**Version**: v2.0

**Status**: [ ] Success [ ] Partial [ ] Rollback

**Notes**: 
_____________________________________________
_____________________________________________
_____________________________________________

