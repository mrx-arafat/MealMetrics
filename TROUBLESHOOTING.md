# MealMetrics Bot - Troubleshooting Guide

## Quick Diagnosis

If you're experiencing photo processing errors, follow this guide to identify and fix the issue.

---

## Common Error Messages and Solutions

### 📸 Image Format Issue

**Error Message:**
```
📸 Image Format Issue

There was a problem reading your photo.

Tips:
• Make sure the image is not corrupted
• Try taking a new photo
• Ensure the photo is in a standard format (JPG/PNG)
```

**Causes:**
- Corrupted image file
- Unsupported image format (e.g., HEIC, WEBP)
- Incomplete download
- Invalid image data

**Solutions:**
1. Take a new photo instead of using an old one
2. Convert image to JPG or PNG format
3. Try a different camera app
4. Ensure the image fully uploaded before sending

---

### ⏱️ Request Timeout

**Error Message:**
```
⏱️ Request Timeout

The analysis took too long to complete.

Please try again in a moment.
```

**Causes:**
- AI service is slow or overloaded
- Very large image taking too long to process
- Network latency issues

**Solutions:**
1. Wait 30-60 seconds and try again
2. Use a smaller/compressed image
3. Check your internet connection speed
4. Try during off-peak hours

---

### 🌐 Connection Issue

**Error Message:**
```
🌐 Connection Issue

There was a network problem connecting to the AI service.

Please check your internet connection and try again.
```

**Causes:**
- No internet connection
- Firewall blocking requests
- DNS issues
- AI service temporarily down

**Solutions:**
1. Check your internet connection
2. Try switching between WiFi and mobile data
3. Restart your router
4. Wait a few minutes and retry
5. Check if other internet services work

---

### 📏 Image Size Issue

**Error Message:**
```
📏 Image Size Issue

Your image is too large or complex to process.

Try:
• Taking a smaller photo
• Compressing the image
• Using your camera's lower resolution setting
```

**Causes:**
- Image file too large (>10MB)
- Very high resolution image (>4K)
- Memory constraints

**Solutions:**
1. Use your camera's lower resolution setting
2. Compress the image before sending
3. Crop the image to show just the food
4. Use a photo compression app

---

### 🔧 Image Processing Issue

**Error Message:**
```
🔧 Image Processing Issue

There was a problem enhancing your photo.

Try:
• Taking a new photo
• Using better lighting
• Ensuring the image is not corrupted
```

**Causes:**
- Image enhancement algorithm failed
- Unusual image properties
- Extreme lighting conditions

**Solutions:**
1. Take photo in better lighting
2. Avoid extreme brightness or darkness
3. Take a new photo from a different angle
4. Ensure food is clearly visible

---

### 🤖 AI Service Issue

**Error Message:**
```
🤖 AI Service Issue

The AI analysis service is temporarily unavailable.

Please try again in a moment.
```

**Causes:**
- AI service is down for maintenance
- Rate limiting (too many requests)
- API key issues
- Service outage

**Solutions:**
1. Wait 5-10 minutes and try again
2. Check bot status announcements
3. Contact bot administrator if persistent
4. Try during different time of day

---

### ⚙️ System Issue

**Error Message:**
```
⚙️ System Issue

There's a temporary system configuration issue.

The bot administrator has been notified. Please try again in a few minutes.
```

**Causes:**
- Missing Python dependencies
- Server configuration problem
- System resource exhaustion

**Solutions:**
1. Wait for administrator to fix
2. Try again in 10-15 minutes
3. Report the issue if it persists
4. This is not a user-side issue

---

## Best Practices for Photo Uploads

### ✅ DO:
- ✅ Take photos in good lighting
- ✅ Use standard formats (JPG, PNG)
- ✅ Keep images under 5MB
- ✅ Show the entire meal clearly
- ✅ Take photos from above (bird's eye view)
- ✅ Ensure food is in focus
- ✅ Use natural lighting when possible

### ❌ DON'T:
- ❌ Use heavily filtered images
- ❌ Send blurry or dark photos
- ❌ Use screenshots of photos
- ❌ Send images with text overlays
- ❌ Use extreme angles
- ❌ Send corrupted files
- ❌ Use unsupported formats (HEIC, WEBP)

---

## Testing Your Image

If you're experiencing repeated issues with a specific image, use the test tool:

```bash
python test_image_processing.py /path/to/your/image.jpg
```

This will show you exactly which step is failing:
1. File existence ✓
2. Image opening ✓
3. RGB conversion ✓
4. Image resizing ✓
5. Image enhancement ✓
6. Base64 conversion ✓
7. AI analysis ✓

---

## Checking Logs

### For Bot Administrators:

View the log file to see detailed error information:

```bash
tail -f mealmetrics.log
```

Look for these patterns:

**Image Enhancement Errors:**
```
ERROR - ❌ Ultra-enhancement failed: [error details]
WARNING - ⚠️ Using fallback basic enhancement
```

**Image Opening Errors:**
```
ERROR - Failed to open or read image file: [error details]
ERROR - Cannot identify or read image file
```

**API Errors:**
```
ERROR - Model [model_name] failed with status [code]
ERROR - All AI models failed. Last error: [error details]
```

**Network Errors:**
```
ERROR - Connection error with model [model_name]
ERROR - Network error when calling AI service
```

---

## Performance Tips

### For Users:
1. **Optimal Image Size**: 1-3 MB
2. **Optimal Resolution**: 1920x1080 or lower
3. **Best Format**: JPG with 80-90% quality
4. **Best Lighting**: Natural daylight or bright indoor lighting
5. **Best Angle**: Directly above the food

### For Administrators:
1. Monitor log file size and rotate regularly
2. Check API rate limits and quotas
3. Monitor server memory and CPU usage
4. Keep dependencies updated
5. Test with various image types regularly

---

## Getting Help

### If Issues Persist:

1. **Check Bot Status**: Verify the bot is running
2. **Test with Different Image**: Try a simple, clear photo
3. **Check Internet**: Ensure stable connection
4. **Review Logs**: Look for specific error patterns
5. **Contact Support**: Provide error message and log excerpt

### Information to Provide When Reporting Issues:

- ✅ Error message received
- ✅ Image size and format
- ✅ Time of error
- ✅ Steps taken before error
- ✅ Whether it's consistent or intermittent
- ✅ Log file excerpt (if administrator)

---

## Quick Fixes Checklist

- [ ] Is the image in JPG or PNG format?
- [ ] Is the image under 5MB?
- [ ] Is the photo clear and well-lit?
- [ ] Is your internet connection stable?
- [ ] Have you waited and retried?
- [ ] Is the food clearly visible in the photo?
- [ ] Have you tried taking a new photo?
- [ ] Have you checked the bot status?

---

## Emergency Fallback

If the bot consistently fails to process your photos:

1. **Manual Entry**: Use text commands to log meals manually
2. **Alternative Bot**: Check if there's a backup bot instance
3. **Report Issue**: Contact administrator with details
4. **Wait for Fix**: Check back after maintenance window

---

## Additional Resources

- **Main Documentation**: `README.md`
- **Error Handling Details**: `ERROR_HANDLING_IMPROVEMENTS.md`
- **Test Tool**: `test_image_processing.py`
- **Configuration**: `.env.example`

---

## Version Information

This troubleshooting guide is for MealMetrics Bot with enhanced error handling (v2.0+).

Last Updated: 2025-10-01

