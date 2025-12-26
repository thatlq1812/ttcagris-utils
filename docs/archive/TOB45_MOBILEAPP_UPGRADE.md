# TOB-45: Mobile App Upgrade - Account System Implementation

**Author:** Le Quang That  
**Created:** December 25, 2025  
**Last Updated:** December 25, 2025  
**Status:** In Progress  
**Jira Ticket:** TOB-45 - [Training] Send deactive supplier event to app

---

## Table of Contents

1. [Overview](#overview)
2. [Current App State](#current-app-state)
3. [Upgrade Requirements](#upgrade-requirements)
4. [Implementation Steps](#implementation-steps)
5. [API Integration](#api-integration)
6. [Account Flow](#account-flow)
7. [FCM Event Handling](#fcm-event-handling)
8. [Testing Guide](#testing-guide)
9. [Configuration](#configuration)

---

## Overview

### Purpose

Upgrade the demo mobile app to support a real account system that integrates with CAS (Centre Auth Service). This enables proper testing of the force logout flow when a supplier is deactivated.

### Goals

1. Replace demo/mock login with real CAS authentication
2. Register device with firebase_token to device_sessions table
3. Handle FCM force logout events properly
4. Support proper account lifecycle (login, logout, session management)

### Current Demo App Location

```
D:\ttcagris\TOB-37\demo-mobile-app\
```

---

## Current App State

### Existing Structure

```
demo-mobile-app/
  src/
    components/           # UI components
    config/              # App configuration
    handlers/            # Event handlers
    screens/
      HomeScreen.js      # Main screen after login
      LoginScreen.js     # Login screen
    services/
      apiService.js      # API calls
      fcmService.js      # FCM handling
```

### Current Login Flow (Demo Mode)

```javascript
// Current demo login in apiService.js
if (__DEV__ && phoneNumber === 'demo') {
  return {
    success: true,
    data: {
      token: 'demo-jwt-token-12345',
      user: { id: '12345', name: 'Demo User', ... }
    }
  };
}
```

**Issue:** Demo mode does not register device with CAS, so firebase_token is not stored in database.

---

## Upgrade Requirements

### 1. Real Authentication with CAS

- Connect to CAS login endpoint
- Store JWT token from response
- Handle authentication errors properly

### 2. Device Registration

- After login, call device registration API
- Send firebase_token + device info to CAS
- Store device_id for session management

### 3. FCM Token Flow

- Get FCM token on app start
- Register token after successful login
- Update token when refreshed

### 4. Force Logout Handling

- Listen for action_code "001" (supplier deactivate)
- Clear local session
- Navigate to login screen
- Show notification to user

---

## Implementation Steps

### Step 1: Update API Configuration

**File:** `src/services/apiService.js`

```javascript
// API Configuration - Update for your environment
const API_CONFIG = {
  // Gateway URL for production
  BASE_URL: __DEV__
    ? Platform.select({
        android: 'http://10.0.2.2:8080',  // Android emulator
        ios: 'http://localhost:8080',      // iOS simulator
        default: 'http://localhost:8080',
      })
    : 'https://api.agrios.vn',

  // Direct CAS URL (for development without gateway)
  CAS_DIRECT_URL: __DEV__
    ? Platform.select({
        android: 'http://10.0.2.2:4000',
        ios: 'http://localhost:4000',
        default: 'http://localhost:4000',
      })
    : 'https://cas.agrios.vn',

  TIMEOUT: 30000,
  
  // Set to true to use direct CAS connection (bypass gateway)
  USE_DIRECT_CAS: true,
};
```

### Step 2: Implement Real Login

**File:** `src/services/apiService.js`

```javascript
/**
 * Login with phone number and password
 * Calls CAS /api/v1/auth/login endpoint
 */
login: async (phoneNumber, password) => {
  console.log('[API] Logging in:', phoneNumber);

  const baseUrl = API_CONFIG.USE_DIRECT_CAS 
    ? API_CONFIG.CAS_DIRECT_URL 
    : API_CONFIG.BASE_URL;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

    const response = await fetch(`${baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        identifier: phoneNumber,
        password: password,
        device_info: await getDeviceInfoForLogin(),
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || `Login failed: ${response.status}`);
    }

    // CAS returns: { code: "000", message: "success", data: { token, user } }
    if (data.code !== "000") {
      throw new Error(data.message || 'Login failed');
    }

    console.log('[API] Login successful');
    return {
      success: true,
      data: data.data,
    };
  } catch (error) {
    console.error('[API] Login error:', error);
    if (error.name === 'AbortError') {
      throw new Error('Connection timeout. Please check your network.');
    }
    throw error;
  }
},

/**
 * Get device info for login request
 */
const getDeviceInfoForLogin = async () => {
  const fcmToken = await fcmService.getToken();
  const deviceInfo = await getDeviceInfo();
  
  return {
    firebase_token: fcmToken || '',
    device_id: deviceInfo.device_id,
    device_type: deviceInfo.device_type,
    device_name: deviceInfo.device_name,
    os_version: deviceInfo.os_version,
    app_version: deviceInfo.app_version,
  };
};
```

### Step 3: Implement Device Registration

**File:** `src/services/apiService.js`

```javascript
/**
 * Register or update device for push notifications
 * Called after login to ensure device is registered with FCM token
 */
registerDevice: async (fcmToken) => {
  console.log('[API] Registering device with FCM token...');

  const deviceInfo = await getDeviceInfo();
  const authToken = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);

  if (!authToken) {
    console.warn('[API] No auth token, skipping device registration');
    return { success: false, error: 'Not authenticated' };
  }

  const baseUrl = API_CONFIG.USE_DIRECT_CAS 
    ? API_CONFIG.CAS_DIRECT_URL 
    : API_CONFIG.BASE_URL;

  const payload = {
    firebase_token: fcmToken,
    device_id: deviceInfo.device_id,
    device_type: deviceInfo.device_type,
    device_name: deviceInfo.device_name,
    os_version: deviceInfo.os_version,
    app_version: deviceInfo.app_version,
  };

  console.log('[API] Device registration payload:', {
    ...payload,
    firebase_token: fcmToken ? `${fcmToken.substring(0, 30)}...` : null,
  });

  try {
    const response = await fetch(`${baseUrl}/api/v1/devices/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok || data.code !== "000") {
      throw new Error(data.message || 'Device registration failed');
    }

    console.log('[API] Device registered successfully');
    return { success: true, data: data.data };
  } catch (error) {
    console.error('[API] Device registration error:', error);
    // Don't throw - device registration failure shouldn't block app usage
    return { success: false, error: error.message };
  }
},
```

### Step 4: Update Login Screen

**File:** `src/screens/LoginScreen.js`

```javascript
const handleLogin = async () => {
  if (!phoneNumber.trim()) {
    Alert.alert('Error', 'Please enter phone number');
    return;
  }

  if (!password.trim()) {
    Alert.alert('Error', 'Please enter password');
    return;
  }

  setLoading(true);

  try {
    // Step 1: Call login API (device_info included in request)
    const loginResult = await api.login(phoneNumber, password);

    if (!loginResult.success || !loginResult.data) {
      throw new Error(loginResult.message || 'Login failed');
    }

    const { token, user } = loginResult.data;

    // Step 2: Save auth data locally
    await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
    await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));
    await AsyncStorage.setItem(STORAGE_KEYS.ACCOUNT_ID, String(user.account_id || user.id));

    // Step 3: Register/update device with FCM token
    const currentFcmToken = await fcmService.getToken();
    if (currentFcmToken) {
      const regResult = await api.registerDevice(currentFcmToken);
      if (!regResult.success) {
        console.warn('[Login] Device registration failed, but continuing...');
      }
    }

    // Step 4: Navigate to home
    console.log('[Login] Login complete, navigating to home');
    onLoginSuccess(user);

  } catch (error) {
    console.error('[Login] Login error:', error);
    Alert.alert(
      'Login Failed',
      error.message || 'Please check your credentials and try again'
    );
  } finally {
    setLoading(false);
  }
};
```

### Step 5: Implement FCM Force Logout Handler

**File:** `src/handlers/notificationHandler.js` (New file)

```javascript
/**
 * Notification Handler
 * Handles FCM events and action codes
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEYS } from '../services/fcmService';
import { Alert } from 'react-native';

// Action code registry - must match backend
const ACTION_CODES = {
  SUPPLIER_DEACTIVATE: '001',
  BUYER_DEACTIVATE: '002',
  SUPPLIER_SUSPEND: '003',
  BUYER_SUSPEND: '004',
  PASSWORD_CHANGED: '005',
  SESSION_REVOKED: '006',
};

// Action codes that require force logout
const FORCE_LOGOUT_CODES = [
  ACTION_CODES.SUPPLIER_DEACTIVATE,
  ACTION_CODES.BUYER_DEACTIVATE,
  ACTION_CODES.SUPPLIER_SUSPEND,
  ACTION_CODES.BUYER_SUSPEND,
  ACTION_CODES.PASSWORD_CHANGED,
  ACTION_CODES.SESSION_REVOKED,
];

/**
 * Handle incoming FCM event
 * @param {Object} data - FCM data payload
 * @param {Function} onForceLogout - Callback when force logout is needed
 */
export const handleFCMEvent = async (data, onForceLogout) => {
  const { action_code, model, action, description } = data;

  console.log('[NotificationHandler] Received FCM event:', {
    action_code,
    model,
    action,
    description,
  });

  // Check if this is a force logout event
  if (FORCE_LOGOUT_CODES.includes(action_code)) {
    console.log('[NotificationHandler] Force logout triggered');
    
    // Show alert to user
    Alert.alert(
      'Session Ended',
      description || 'Your session has been terminated. Please login again.',
      [
        {
          text: 'OK',
          onPress: async () => {
            await performForceLogout(onForceLogout);
          },
        },
      ],
      { cancelable: false }
    );
    
    return;
  }

  // Handle other action codes
  console.log('[NotificationHandler] Unhandled action code:', action_code);
};

/**
 * Perform force logout - clear session and navigate to login
 */
const performForceLogout = async (onForceLogout) => {
  try {
    console.log('[NotificationHandler] Performing force logout...');

    // Clear all auth data
    await AsyncStorage.multiRemove([
      STORAGE_KEYS.AUTH_TOKEN,
      STORAGE_KEYS.USER_DATA,
      STORAGE_KEYS.ACCOUNT_ID,
    ]);

    // Set flag for background handler
    await AsyncStorage.setItem('FORCE_LOGOUT', 'true');

    // Call logout callback
    if (onForceLogout) {
      onForceLogout();
    }

    console.log('[NotificationHandler] Force logout complete');
  } catch (error) {
    console.error('[NotificationHandler] Force logout error:', error);
  }
};

/**
 * Handle background FCM message
 * Called when app is in background/killed
 */
export const handleBackgroundMessage = async (remoteMessage) => {
  const data = remoteMessage.data;
  
  if (!data || !data.action_code) {
    return;
  }

  console.log('[NotificationHandler] Background message:', data.action_code);

  // For force logout, set flag to check on app resume
  if (FORCE_LOGOUT_CODES.includes(data.action_code)) {
    await AsyncStorage.setItem('FORCE_LOGOUT', 'true');
    await AsyncStorage.setItem('FORCE_LOGOUT_REASON', data.description || 'Session terminated');
  }
};

/**
 * Check if force logout is pending (for app resume)
 */
export const checkPendingForceLogout = async () => {
  const forceLogout = await AsyncStorage.getItem('FORCE_LOGOUT');
  
  if (forceLogout === 'true') {
    const reason = await AsyncStorage.getItem('FORCE_LOGOUT_REASON');
    
    // Clear the flags
    await AsyncStorage.multiRemove(['FORCE_LOGOUT', 'FORCE_LOGOUT_REASON']);
    
    return {
      pending: true,
      reason: reason || 'Your session has been terminated',
    };
  }

  return { pending: false };
};

export { ACTION_CODES, FORCE_LOGOUT_CODES };
```

### Step 6: Update App.js to Use Handler

**File:** `App.js`

```javascript
import React, { useState, useEffect } from 'react';
import { StatusBar, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import messaging from '@react-native-firebase/messaging';

import LoginScreen from './src/screens/LoginScreen';
import HomeScreen from './src/screens/HomeScreen';
import { fcmService, STORAGE_KEYS } from './src/services/fcmService';
import { api } from './src/services/apiService';
import { 
  handleFCMEvent, 
  handleBackgroundMessage,
  checkPendingForceLogout 
} from './src/handlers/notificationHandler';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initializeApp();
    setupFCMListeners();
  }, []);

  const initializeApp = async () => {
    try {
      // Request notification permission
      await fcmService.requestPermission();

      // Get FCM token
      await fcmService.getToken();

      // Check for pending force logout
      const { pending, reason } = await checkPendingForceLogout();
      if (pending) {
        Alert.alert('Session Ended', reason);
        setIsLoggedIn(false);
        setLoading(false);
        return;
      }

      // Check existing session
      const token = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      const userData = await AsyncStorage.getItem(STORAGE_KEYS.USER_DATA);

      if (token && userData) {
        setUser(JSON.parse(userData));
        setIsLoggedIn(true);
      }
    } catch (error) {
      console.error('[App] Initialization error:', error);
    } finally {
      setLoading(false);
    }
  };

  const setupFCMListeners = () => {
    // Foreground message handler
    const unsubscribe = messaging().onMessage(async (remoteMessage) => {
      console.log('[App] FCM message received in foreground');
      
      if (remoteMessage.data) {
        await handleFCMEvent(remoteMessage.data, handleForceLogout);
      }
    });

    // Background message handler (set at app level)
    messaging().setBackgroundMessageHandler(handleBackgroundMessage);

    return unsubscribe;
  };

  const handleForceLogout = () => {
    console.log('[App] Force logout callback triggered');
    setUser(null);
    setIsLoggedIn(false);
  };

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setIsLoggedIn(true);
  };

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
    setIsLoggedIn(false);
  };

  if (loading) {
    return null; // Or a loading screen
  }

  return (
    <>
      <StatusBar barStyle="dark-content" />
      {isLoggedIn ? (
        <HomeScreen 
          user={user} 
          onLogout={handleLogout} 
        />
      ) : (
        <LoginScreen 
          onLoginSuccess={handleLoginSuccess} 
        />
      )}
    </>
  );
};

export default App;
```

### Step 7: Update FCM Service for Token Refresh

**File:** `src/services/fcmService.js`

```javascript
// Add token refresh handler
const setupTokenRefreshListener = (onTokenRefresh) => {
  return messaging().onTokenRefresh(async (newToken) => {
    console.log('[FCM] Token refreshed:', newToken.substring(0, 30) + '...');
    
    // Save new token
    await AsyncStorage.setItem(STORAGE_KEYS.FCM_TOKEN, newToken);
    
    // Re-register device with new token if logged in
    const authToken = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    if (authToken) {
      try {
        await api.registerDevice(newToken);
        console.log('[FCM] Device re-registered with new token');
      } catch (error) {
        console.error('[FCM] Failed to re-register device:', error);
      }
    }
    
    if (onTokenRefresh) {
      onTokenRefresh(newToken);
    }
  });
};

// Export updated service
export const fcmService = {
  requestPermission,
  getToken,
  onNotification,
  onTokenRefresh: setupTokenRefreshListener,
};
```

---

## API Integration

### Required CAS Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/v1/auth/login` | POST | No | Login with credentials |
| `/api/v1/devices/register` | POST | Yes | Register device with FCM token |
| `/api/v1/devices/unregister` | POST | Yes | Unregister device on logout |

### Login Request

```json
POST /api/v1/auth/login

{
  "identifier": "0901234567",
  "password": "password123",
  "device_info": {
    "firebase_token": "eAVmjf6OTJ6moEnc9W0s0_:APA91b...",
    "device_id": "abc123-def456",
    "device_type": "android",
    "device_name": "Samsung Galaxy S21",
    "os_version": "13",
    "app_version": "1.0.0 (1)"
  }
}
```

### Login Response

```json
{
  "code": "000",
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 123,
      "account_id": 456,
      "phone": "0901234567",
      "name": "John Doe",
      "is_supplier": true,
      "is_active_supplier": true
    }
  }
}
```

### Device Register Request

```json
POST /api/v1/devices/register
Authorization: Bearer <jwt_token>

{
  "firebase_token": "eAVmjf6OTJ6moEnc9W0s0_:APA91b...",
  "device_id": "abc123-def456",
  "device_type": "android",
  "device_name": "Samsung Galaxy S21",
  "os_version": "13",
  "app_version": "1.0.0 (1)"
}
```

---

## Account Flow

### Complete Login Flow

```
1. User enters phone + password
   |
   v
2. App calls CAS /api/v1/auth/login
   |
   v
3. CAS validates credentials
   - Creates/updates device_session with firebase_token
   - Returns JWT token + user data
   |
   v
4. App saves token + user data locally
   |
   v
5. App calls registerDevice (if needed)
   |
   v
6. App navigates to HomeScreen
   |
   v
7. FCM listener active for force logout events
```

### Force Logout Flow

```
1. Admin deactivates supplier in CAS
   |
   v
2. CAS calls noti-service.SendEventToDevices
   - action_code: "001"
   - model: "suppliers"
   - action: "deactivate"
   |
   v
3. Noti-service sends FCM to device tokens
   |
   v
4. Mobile app receives FCM message
   |
   v
5. handleFCMEvent checks action_code
   - "001" is in FORCE_LOGOUT_CODES
   |
   v
6. App shows alert: "Your supplier account has been deactivated"
   |
   v
7. User taps OK
   |
   v
8. performForceLogout clears session
   |
   v
9. App navigates to LoginScreen
```

---

## Testing Guide

### Prerequisites

1. Physical Android device (FCM requires real device for reliable testing)
2. CAS running at `localhost:4000`
3. Noti-service running at `localhost:9012`
4. Firebase project configured

### Test Scenarios

#### Scenario 1: Normal Login

1. Start CAS and noti-service
2. Build and run mobile app
3. Enter valid phone/password
4. Verify:
   - Login succeeds
   - FCM token shown on HomeScreen
   - Check `device_sessions` table has entry

```sql
SELECT account_id, firebase_token, device_id, is_active
FROM device_sessions
WHERE account_id = YOUR_ACCOUNT_ID;
```

#### Scenario 2: Force Logout

1. Login as supplier on mobile app
2. Note the account_id and supplier_id
3. Call DeactiveSupplier API:

```bash
grpcurl -plaintext -d '{
  "id": YOUR_SUPPLIER_ID
}' localhost:50051 supplier.v1.SupplierService/DeactiveSupplier
```

4. Verify on mobile:
   - Alert appears: "Your supplier account has been deactivated"
   - Tapping OK logs out user
   - App shows LoginScreen

#### Scenario 3: Background Force Logout

1. Login on mobile app
2. Put app in background (press home)
3. Call DeactiveSupplier API
4. Open app again
5. Verify:
   - Alert appears immediately
   - User is logged out

### Debug Commands

**Check device registration:**
```bash
curl http://localhost:4000/api/v1/devices/list \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Test FCM directly:**
```bash
grpcurl -plaintext -d '{
  "deviceTokens": ["YOUR_FCM_TOKEN"],
  "actionCode": "001",
  "model": "suppliers",
  "action": "deactivate",
  "description": "Test force logout"
}' localhost:9012 api.v1.NotificationService/SendEventToDevices
```

---

## Configuration

### Environment Setup

**For Android Emulator (localhost):**
```javascript
// Use 10.0.2.2 for localhost access
CAS_DIRECT_URL: 'http://10.0.2.2:4000'
```

**For Physical Device (same network):**
```javascript
// Use computer's local IP
CAS_DIRECT_URL: 'http://192.168.1.100:4000'
```

**For Production:**
```javascript
CAS_DIRECT_URL: 'https://cas.agrios.vn'
```

### Firebase Configuration

Ensure `google-services.json` (Android) or `GoogleService-Info.plist` (iOS) is properly configured with your Firebase project.

---

## Related Files

| File | Description |
|------|-------------|
| `TOB-37/demo-mobile-app/src/services/apiService.js` | API service |
| `TOB-37/demo-mobile-app/src/services/fcmService.js` | FCM service |
| `TOB-37/demo-mobile-app/src/screens/LoginScreen.js` | Login screen |
| `TOB-37/demo-mobile-app/src/screens/HomeScreen.js` | Home screen |
| `docs/tob45/TOB45_CAS_IMPLEMENTATION.md` | CAS implementation guide |
| `docs/tob37/TOB37_IMPLEMENTATION.md` | FCM event system docs |

---

## Checklist

### Mobile App Upgrade

- [ ] Update API configuration with correct URLs
- [ ] Implement real login with CAS
- [ ] Add device registration after login
- [ ] Create notification handler for force logout
- [ ] Update App.js with FCM listeners
- [ ] Handle token refresh
- [ ] Test on physical device

### CAS Integration

- [ ] Verify login endpoint returns device_info
- [ ] Verify device_sessions table is populated
- [ ] Verify firebase_token is stored correctly
- [ ] Test DeactiveSupplier triggers FCM event

### End-to-End Testing

- [ ] Login flow works
- [ ] FCM token registered in database
- [ ] Force logout notification received
- [ ] App logs out and shows login screen
- [ ] Background force logout works
