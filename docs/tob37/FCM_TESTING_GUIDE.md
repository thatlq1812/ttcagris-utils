# FCM Force Logout Testing Guide

**Author:** System  
**Created:** 2024-12-24  
**Last Updated:** 2024-12-24

This guide explains how to test the Force Logout feature via FCM (Firebase Cloud Messaging) push notifications.

---

## Prerequisites

1. **Docker** and **Docker Compose** installed
2. **Android device** or emulator with Google Play Services
3. **FCM credentials** file (`fcm-dev-sdk.json`) in the noti-service directory

---

## Quick Start

### Step 1: Start Infrastructure Services

Navigate to the TOB-37 directory and start the required services:

```bash
cd TOB-37
docker compose up -d
```

This starts:
- PostgreSQL 17 (port 5432)
- Redis 7 (port 6379)

### Step 2: Start Notification Service

Option A - Run locally with Go:
```bash
cd noti-service
make api
```

Option B - Run with Docker Compose:
```bash
cd noti-service
docker compose -f docker-compose.local.yml up -d
```

The notification service will be available at:
- gRPC: port 9012
- HTTP: port 8000

### Step 3: Install Mobile App

Install the demo mobile app on your Android device:

1. Build the APK (see APK Build section below)
2. Transfer to device and install
3. Allow notification permissions when prompted

### Step 4: Login to App

1. Open the app
2. Click **"Quick Login (Demo)"** button for instant login
3. Or enter any credentials manually

### Step 5: Copy FCM Token

1. After login, find the **Device Token** section
2. Click **"Copy Full Token"** button
3. The token is now in your clipboard

### Step 6: Send Force Logout Notification

Use the test script in the `test-fcm` directory:

```bash
cd TOB-37/test-fcm
go run main.go -token "YOUR_FCM_TOKEN"
```

Or with account ID:
```bash
go run main.go -token "YOUR_FCM_TOKEN" -account "12345"
```

### Step 7: Observe Force Logout

- The app will receive the notification
- A modal will appear informing about the force logout
- The user will be logged out automatically

---

## APK Build Instructions

### Prerequisites for Building

1. **Node.js** 18+ installed
2. **JDK 17** installed
3. **Android SDK** with Build Tools

### Build Steps

1. Install dependencies:
```bash
cd TOB-37/demo-mobile-app
npm install
```

2. Bundle the JavaScript:
```bash
npx react-native bundle --platform android --dev false --entry-file index.js --bundle-output android/app/src/main/assets/index.android.bundle --assets-dest android/app/src/main/res
```

3. Build the APK:
```bash
cd android
./gradlew assembleDebug
```

4. Find the APK at:
```
android/app/build/outputs/apk/debug/app-debug.apk
```

### Install on Device

Via ADB:
```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

Or transfer the APK file to device and install manually.

---

## Troubleshooting

### FCM Token Not Available

- Ensure Google Play Services is installed on device
- Check that notifications are enabled for the app
- Try restarting the app

### Notification Not Received

- Verify the FCM token is correct and not expired
- Check noti-service logs for errors
- Ensure device has internet connection

### App Not Force Logging Out

- Check that the notification payload contains `event_type: "FORCE_LOGOUT"`
- Verify the app is handling background messages correctly

---

## Service Ports Summary

| Service | Port | Protocol |
|---------|------|----------|
| PostgreSQL | 5432 | TCP |
| Redis | 6379 | TCP |
| Noti Service (gRPC) | 9012 | gRPC |
| Noti Service (HTTP) | 8000 | HTTP |
| API Gateway | 8080 | HTTP |
| CAS Service (HTTP) | 4000 | HTTP |
| CAS Service (gRPC) | 50051 | gRPC |

---

## Related Documentation

- [Mobile SDK Guide](../demo-mobile-app/MOBILE_SDK_GUIDE.md)
- [Noti Service README](../../noti-service/README.md)
