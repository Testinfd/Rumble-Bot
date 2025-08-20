# Rumble Bot Testing Guide

This guide will help you test the Rumble upload functionality to ensure everything is working correctly.

## 🚀 Quick Test Setup

### 1. Install Dependencies

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Credentials

Edit the `.env` file with your actual Rumble credentials:

```env
# Required for testing
RUMBLE_EMAIL=your_actual_email@example.com
RUMBLE_PASSWORD=your_actual_password
RUMBLE_CHANNEL=your_channel_name

# Test settings
HEADLESS_MODE=false
LOG_LEVEL=DEBUG
```

**Important Notes:**
- Use your real Rumble account credentials
- `RUMBLE_CHANNEL` should be the exact name of your channel as it appears in Rumble
- Set `HEADLESS_MODE=false` to see the browser during testing
- Set `LOG_LEVEL=DEBUG` for detailed logging

### 3. Run the Test

**Windows:**
```cmd
scripts\test_rumble.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/test_rumble.sh
./scripts/test_rumble.sh
```

**Or run directly:**
```bash
python test_rumble_upload.py
```

## 🧪 What the Test Does

The test script will:

1. **✅ Configuration Check**
   - Verify credentials are set
   - Display current settings

2. **🔐 Login Test**
   - Attempt to login to Rumble
   - Verify authentication works

3. **📺 Channel Selection Test**
   - Test channel dropdown/selection
   - Verify your specified channel can be selected

4. **📝 Form Filling Test**
   - Test title, description, and tags fields
   - Generate sample metadata

5. **🚀 Full Upload Test (Optional)**
   - Upload a small test file
   - Complete end-to-end test

## 📊 Expected Results

### ✅ Successful Test Output

```
🧪 Rumble Upload Test Suite
==================================================

⚙️ Configuration Check...
   - Rumble Email: your_email@example.com
   - Rumble Channel: YourChannelName
   - Headless Mode: False

🔐 Testing Rumble Login...
==================================================
✅ Login successful!
   - Email: your_email@example.com
   - Status: Logged in

📺 Testing Channel Selection...
==================================================
✅ Channel selection successful!
   - Channel: YourChannelName

📝 Testing Upload Form...
==================================================
   - Title: Amazing Video #1234
   - Description: This is an amazing video that you definitely...
   - Tags: video, content, awesome, amazing, cool
✅ Form filling successful!
   - All fields populated correctly

🎉 Test Suite Completed!
==================================================
✅ Basic functionality appears to be working
📝 Check the logs for detailed information
```

### ❌ Common Issues and Solutions

**1. Login Failed**
```
❌ Login failed!
   - Check your credentials in .env file
   - Ensure Rumble account is valid
```
**Solution:** Verify your email and password are correct in `.env`

**2. Channel Not Found**
```
⚠️ Channel selection failed or not found
   - Channel: YourChannelName
```
**Solution:** 
- Check the exact channel name in your Rumble account
- Channel names are case-sensitive
- Make sure you have upload permissions for that channel

**3. Form Fields Not Found**
```
❌ Form filling failed!
   - Check if upload page structure has changed
```
**Solution:** Rumble may have updated their UI. Check the logs for specific errors.

**4. ChromeDriver Issues**
```
❌ Error setting up WebDriver
```
**Solution:** 
```bash
pip install --upgrade webdriver-manager
```

## 🔍 Debugging

### View Detailed Logs
```bash
tail -f logs/rumble_bot.log
```

### Test with Browser Visible
Set in `.env`:
```env
HEADLESS_MODE=false
LOG_LEVEL=DEBUG
```

### Manual Testing Steps

1. **Check Rumble Login Manually:**
   - Go to https://rumble.com/login.php
   - Try logging in with your credentials

2. **Check Channel Access:**
   - Go to https://rumble.com/upload.php
   - Verify you can see your channel in the dropdown

3. **Check Upload Form:**
   - Ensure all fields (title, description, tags) are visible
   - Try uploading a small test video manually

## 🎯 Testing Different Scenarios

### Test Without Channel Selection
```env
RUMBLE_CHANNEL=
```
This will test default channel behavior.

### Test with Different Metadata
Modify the test script to use custom titles, descriptions, and tags.

### Test File Size Limits
```env
MAX_FILE_SIZE_MB=100
```
Test with different file size limits.

## 📝 Test Results Checklist

- [ ] Configuration loads correctly
- [ ] Login succeeds with your credentials
- [ ] Channel selection works (if specified)
- [ ] Form fields can be filled
- [ ] Browser automation works smoothly
- [ ] No critical errors in logs

## 🚨 Important Notes

- **Don't test with important content** - use test videos only
- **Monitor your Rumble account** for any test uploads
- **Delete test videos** after successful testing
- **Check Rumble's terms of service** regarding automated uploads
- **Use rate limiting** to avoid being blocked

## 🔄 Next Steps After Successful Testing

1. **Set up Telegram Bot Token** for full functionality
2. **Configure production settings** (HEADLESS_MODE=true)
3. **Deploy to cloud platform** using provided configs
4. **Set up monitoring** and alerts
5. **Test with real video content**

## 📞 Getting Help

If tests fail:
1. Check the detailed logs in `logs/rumble_bot.log`
2. Verify your Rumble account has upload permissions
3. Ensure Chrome/Chromium is installed and updated
4. Try running with `HEADLESS_MODE=false` to see what's happening
5. Check if Rumble has updated their upload page structure
