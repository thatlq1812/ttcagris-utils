# Mobile App Testing Guide

**Author:** ttcagris  
**Created:** December 21, 2025  
**Last Updated:** December 21, 2025

---

## Overview

This guide provides step-by-step instructions for testing the AgriOS Supplier Demo mobile app with FCM push notifications.

## Prerequisites

Before testing, ensure you have:

- [ ] Android device or emulator (API level 23+)
- [ ] Firebase project created with FCM enabled
- [ ] `google-services.json` file placed in `mobile-app/android/app/`
- [ ] `serviceAccountKey.json` file placed in `noti-service/config/`
- [ ] Docker and Docker Compose installed
- [ ] Node.js 18+ installed

---

## Part 1: Backend Setup

### Step 1: Start Services with Docker Compose

```bash
# From project root
cd d:\ttcagris

# Start all services
docker-compose -f docker-compose.test.yml up -d

# Verify services are running
docker-compose -f docker-compose.test.yml ps

# Check logs
docker-compose -f docker-compose.test.yml logs -f noti-service
```

Expected output:
- postgres: healthy
- redis: healthy
- noti-service: running on port 9012
- api-gateway: running on port 8080 (optional)

### Step 2: Verify Database Initialization

```bash
# Connect to PostgreSQL
docker exec -it agrios-postgres psql -U postgres

# List databases
\l

# Expected output: notification_service, api_gateway, centre_auth_service

# Connect to notification_service
\c notification_service

# List tables
\dt

# Exit
\q
```

### Step 3: Test Notification Service Health

```bash
# Using curl (if REST API enabled)
curl http://localhost:8000/health

# Or check gRPC health
grpcurl -plaintext localhost:9012 grpc.health.v1.Health/Check
```

---

## Part 2: Mobile App Setup

### Step 1: Install Dependencies

```bash
cd mobile-app

# Install npm packages
npm install

# For iOS (macOS only)
cd ios && pod install && cd ..
```

### Step 2: Configure Firebase

1. **Get google-services.json:**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Select your project
   - Go to Project Settings → Your apps
   - Download `google-services.json`
   - Place in `mobile-app/android/app/google-services.json`

2. **Verify package name:**
   - Open `google-services.json`
   - Confirm `package_name` is `com.agriossupplierdemo`

### Step 3: Build and Run the App

```bash
# Start Metro bundler
npm start

# In another terminal, run on Android
npm run android

# Or run on specific device
npx react-native run-android --deviceId=<device-id>

# List devices
adb devices
```

### Step 4: Get FCM Token

When the app launches, check the logs for FCM token:

```bash
# View React Native logs
npx react-native log-android

# Look for:
# === FCM TOKEN ===
# eXaMpLe_ToKeN_hErE...
# =================
```

**Save this token** - you'll need it for sending test notifications.

---

## Part 3: Testing Notifications

### Method 1: Using Postman

#### Test 1: Send Basic Notification

Create a new gRPC request in Postman:

**Service URL:** `localhost:9012`  
**Method:** `api.v1.NotificationService/SendNotification`  
**Request Body:**

```json
{
  "accountId": "test-user-123",
  "deviceToken": "YOUR_FCM_TOKEN_HERE",
  "title": "Test Notification",
  "body": "This is a test notification from Postman",
  "data": {
    "action": "test",
    "timestamp": "2025-12-21T10:00:00Z"
  }
}
```

**Expected Result:**
- Status: OK
- Notification appears on device
- Check notification log in app

#### Test 2: Supplier Update Notification

**Request Body:**

```json
{
  "accountId": "test-user-123",
  "deviceToken": "YOUR_FCM_TOKEN_HERE",
  "title": "Supplier Updated",
  "body": "Green Valley Farms has been updated",
  "data": {
    "action": "update",
    "targetObject": "supplier",
    "objectId": "1"
  }
}
```

**Expected Result:**
- Notification appears
- Tap notification → App opens to SupplierUpdateScreen
- Screen shows supplier ID: 1
- Blue banner indicates "Opened from notification"

#### Test 3: View Supplier Notification

**Request Body:**

```json
{
  "accountId": "test-user-123",
  "deviceToken": "YOUR_FCM_TOKEN_HERE",
  "title": "View Supplier",
  "body": "Check out AgriTech Solutions",
  "data": {
    "action": "view",
    "targetObject": "supplier",
    "objectId": "2"
  }
}
```

**Expected Result:**
- App navigates to SupplierDetailScreen
- Shows details for supplier ID: 2

### Method 2: Using Firebase Console

1. Go to Firebase Console → Cloud Messaging
2. Click "Send your first message"
3. Enter:
   - **Title:** "Supplier Update"
   - **Body:** "A supplier was updated"
4. Click "Send test message"
5. Enter your FCM token
6. Click "Test"
7. Add Additional Options → Custom data:
   - `action`: `update`
   - `targetObject`: `supplier`
   - `objectId`: `1`

### Method 3: Using cURL

```bash
# Get FCM server key from Firebase Console → Project Settings → Cloud Messaging

curl -X POST https://fcm.googleapis.com/fcm/send \
  -H "Authorization: key=YOUR_SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "YOUR_FCM_TOKEN",
    "notification": {
      "title": "Supplier Update",
      "body": "Green Valley Farms updated"
    },
    "data": {
      "action": "update",
      "targetObject": "supplier",
      "objectId": "1"
    }
  }'
```

---

## Part 4: Test Scenarios

### Scenario 1: Foreground Notification

**Setup:**
1. Open mobile app
2. Stay on Home screen

**Action:**
Send notification using Method 1 (Postman)

**Expected Result:**
- Alert dialog appears immediately
- Two options: "Dismiss" and "View"
- Click "View" → Navigate to appropriate screen
- Notification saved to log

### Scenario 2: Background Notification

**Setup:**
1. Open mobile app
2. Minimize app (press Home button)

**Action:**
Send notification

**Expected Result:**
- System notification appears in notification tray
- Tap notification → App comes to foreground
- Navigate to appropriate screen based on action

### Scenario 3: Quit State Notification

**Setup:**
1. Force close the app
2. Swipe away from recent apps

**Action:**
Send notification

**Expected Result:**
- System notification appears
- Tap notification → App launches
- Navigate to appropriate screen
- May take 1-2 seconds to initialize

### Scenario 4: Multiple Notifications

**Setup:**
Open notification log screen

**Action:**
Send 5 different notifications

**Expected Result:**
- All 5 appear in notification log
- Sorted by time (newest first)
- Each shows title, body, timestamp, and data payload
- Scroll to view all

---

## Part 5: Verification Checklist

### Backend Verification

- [ ] PostgreSQL running and accessible
- [ ] Redis running and accessible
- [ ] noti-service responds to health checks
- [ ] noti-service logs show FCM initialization
- [ ] No errors in service logs

### Mobile App Verification

- [ ] App builds without errors
- [ ] FCM token generated successfully
- [ ] Token displayed in app home screen
- [ ] All screens load correctly
- [ ] Navigation works properly

### Notification Verification

- [ ] Foreground notifications display alert
- [ ] Background notifications appear in tray
- [ ] Quit state notifications work
- [ ] Auto-navigation works for all actions
- [ ] Notification log saves history
- [ ] Clear log function works

---

## Part 6: Troubleshooting

### Issue: FCM Token Not Generated

**Symptoms:**
- No token in logs
- "FCM Token: null" in app

**Solutions:**
1. Verify `google-services.json` exists and is valid
2. Rebuild app: `cd android && ./gradlew clean && cd .. && npm run android`
3. Check Firebase project has FCM enabled
4. Check app package name matches Firebase config

### Issue: Notifications Not Received

**Symptoms:**
- API call succeeds but no notification appears

**Solutions:**
1. Verify FCM token is correct (copy from app)
2. Check device has internet connection
3. Verify notification service has correct `serviceAccountKey.json`
4. Check Firebase Console → Cloud Messaging → Delivery reports
5. Check device notification permissions are enabled

### Issue: App Crashes on Notification

**Symptoms:**
- App crashes when notification arrives

**Solutions:**
1. Check logcat: `adb logcat | grep AgriOS`
2. Verify notification data format is correct
3. Check navigation code for null safety
4. Rebuild app with debug symbols

### Issue: Auto-Navigation Not Working

**Symptoms:**
- Notification received but wrong screen opens

**Solutions:**
1. Verify `data` payload contains correct fields:
   - `action`
   - `targetObject`
   - `objectId`
2. Check FCM service navigation logic
3. Test with different action values
4. Check RootNavigation is properly configured

### Issue: Docker Services Not Starting

**Symptoms:**
- Services fail to start
- Port conflicts

**Solutions:**
```bash
# Check what's using ports
netstat -ano | findstr "5432 6379 9012 8080"

# Stop all containers
docker-compose -f docker-compose.test.yml down

# Remove volumes and restart
docker-compose -f docker-compose.test.yml down -v
docker-compose -f docker-compose.test.yml up -d --build
```

---

## Part 7: Performance Testing

### Test 1: Latency

Measure time from notification sent to received:

1. Send notification via Postman
2. Note timestamp in request
3. Note timestamp when notification appears
4. Calculate difference

**Target:** < 2 seconds for foreground notifications

### Test 2: Concurrent Notifications

Send multiple notifications rapidly:

```bash
# Using script (create test-notifications.sh)
for i in {1..10}; do
  grpcurl -d '{"accountId":"user1","deviceToken":"TOKEN","title":"Test '$i'"}' \
    -plaintext localhost:9012 \
    api.v1.NotificationService/SendNotification
done
```

**Expected:** All 10 received within 5 seconds

### Test 3: Battery Impact

1. Open app
2. Receive 50 notifications over 1 hour
3. Check battery usage in device settings

**Target:** < 5% battery usage

---

## Part 8: Building Production APK

### Debug APK (Testing)

```bash
cd android
./gradlew assembleDebug

# APK location:
# android/app/build/outputs/apk/debug/app-debug.apk
```

### Release APK (Production)

```bash
# Generate keystore (first time only)
keytool -genkey -v -keystore agrios-release.keystore \
  -alias agrios-key -keyalg RSA -keysize 2048 -validity 10000

# Build release APK
cd android
./gradlew assembleRelease

# APK location:
# android/app/build/outputs/apk/release/app-release.apk
```

### Install APK on Device

```bash
# Via ADB
adb install android/app/build/outputs/apk/debug/app-debug.apk

# Or copy to device and install manually
```

---

## Part 9: Database Queries for Testing

### View All Notifications

```sql
SELECT 
    id,
    account_id,
    title,
    status,
    created_at,
    sent_at
FROM notifications
ORDER BY created_at DESC
LIMIT 20;
```

### Check Notification Status Distribution

```sql
SELECT 
    status,
    COUNT(*) as count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM notifications) as percentage
FROM notifications
GROUP BY status;
```

### Find Failed Notifications

```sql
SELECT 
    id,
    account_id,
    title,
    created_at,
    data->>'error' as error_message
FROM notifications
WHERE status = 'FAILED'
ORDER BY created_at DESC;
```

### Notifications by User

```sql
SELECT 
    account_id,
    COUNT(*) as total,
    SUM(CASE WHEN status = 'SENT' THEN 1 ELSE 0 END) as sent,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed
FROM notifications
GROUP BY account_id;
```

---

## Conclusion

This testing guide covers all aspects of the mobile app and notification system. Follow the steps in order for best results.

For production deployment, ensure:
- Use production Firebase project
- Secure all credentials
- Enable proper monitoring and logging
- Test on multiple devices and Android versions
- Implement proper error handling and retry logic

---

## Support

For issues or questions, refer to:
- [README.md](../mobile-app/README.md) - Mobile app documentation
- [PORT_ALLOCATION.md](PORT_ALLOCATION.md) - Service ports reference
- [noti-service README](../noti-service/README.md) - Notification service docs
