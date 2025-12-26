# Environment-Specific Configuration Guide
## OTP Delivery Configuration for Different Environments

---

## 🎯 Overview

The system supports multiple OTP delivery methods with automatic fallback:
1. **Telegram Bot** (Best for development/testing)
2. **SMS via Notification Service** (Production)
3. **Console Logs** (Fallback when nothing configured)

**Priority:** Telegram → SMS → Console

---

## 📁 Configuration Files

### Development Environment

**File:** `config/config.yaml` or `config/config.development.yaml`

```yaml
server:
  env: "development"
  debug: true

# OTP Settings
otp:
  expire_seconds: 120           # 2 minutes
  verified_grace_seconds: 180   # 3 minutes after verification
  max_per_day: 10               # More relaxed for testing
  cooldown_seconds: 30          # Shorter cooldown for faster testing

# ✅ Telegram: ENABLED (for development)
telegram:
  enabled: true
  bot_token: "YOUR_BOT_TOKEN"   # Get from @BotFather
  chat_id: "YOUR_CHAT_ID"       # Your Telegram chat ID

# ❌ SMS: DISABLED (not needed in dev)
services:
  notification: ""                # Empty = SMS disabled
  # Or point to mock service if testing SMS flow:
  # notification: "localhost:9100"
```

**Benefits:**
- ✅ No SMS costs in development
- ✅ Instant OTP delivery via Telegram
- ✅ Easy to see OTP codes
- ✅ No external dependencies

---

### Production Environment

**File:** `config/config.production.yaml`

```yaml
server:
  env: "production"
  debug: false

# OTP Settings (Stricter)
otp:
  expire_seconds: 120           # 2 minutes
  verified_grace_seconds: 180   # 3 minutes
  max_per_day: 5                # Limit abuse
  cooldown_seconds: 60          # Prevent spam

# ❌ Telegram: DISABLED (not for production)
telegram:
  enabled: false
  bot_token: ""
  chat_id: ""

# ✅ SMS: ENABLED (production-ready)
services:
  notification: "notification-service.internal:9100"  # Internal service address
  # Or external SMS gateway
  # notification: "sms-gateway.company.com:9100"
```

**Benefits:**
- ✅ Professional SMS delivery
- ✅ Multi-user support
- ✅ No single-chat limitation
- ✅ Reliable at scale

---

### Staging/UAT Environment

**File:** `config/config.staging.yaml`

```yaml
server:
  env: "staging"
  debug: false

otp:
  expire_seconds: 120
  verified_grace_seconds: 180
  max_per_day: 8                # Between dev and prod
  cooldown_seconds: 45

# 🔄 BOTH ENABLED (for testing both methods)
telegram:
  enabled: true                 # Keep for QA team
  bot_token: "STAGING_BOT_TOKEN"
  chat_id: "QA_TEAM_CHAT_ID"

services:
  notification: "notification-service.staging:9100"  # Test real SMS
```

**Benefits:**
- ✅ Test both delivery methods
- ✅ QA team can use Telegram
- ✅ Validate SMS integration
- ✅ Catch production issues early

---

## 🔧 How It Works

### Code Logic (Already Implemented)

**File:** `internal/usecase/mobile_auth_usecase.go`

```go
func (u *mobileAuthUsecase) createAndSendOTP(ctx, phoneNumber, purpose string) (*domain.OTPVerification, error) {
    // Generate OTP
    otpCode, err := u.generateOTP()
    
    // Priority 1: Telegram (if enabled and configured)
    if u.telegramClient != nil {
        err := u.telegramClient.SendOTP(ctx, phoneNumber, otpCode, purpose, expireMinutes)
        if err == nil {
            logger.Info("✅ otp sent via telegram")
            // Save to DB and return
        }
    }
    
    // Priority 2: SMS (if notification service available)
    if u.notificationClient != nil {
        courierLogID, err := u.notificationClient.SendOTP(ctx, phoneNumber, otpCode, purpose)
        if err == nil {
            logger.Info("otp sent via sms")
            // Save to DB and return
        }
    }
    
    // Priority 3: Console Log (fallback)
    logger.Warn("⚠️ notification client not configured - otp logged to console")
    logger.Info("OTP Code: " + otpCode)  // Only in dev!
    
    // Save to DB anyway
    return otp, nil
}
```

---

## 🚀 DevOps Setup Instructions

### For Development Team

1. **Get Telegram Bot Token:**
   ```bash
   # Talk to @BotFather on Telegram
   /newbot
   # Follow instructions
   # Save bot token
   ```

2. **Get Your Chat ID:**
   ```bash
   # Talk to @userinfobot
   /start
   # It will show your chat ID
   ```

3. **Update config.yaml:**
   ```yaml
   telegram:
     enabled: true
     bot_token: "YOUR_TOKEN_HERE"
     chat_id: "YOUR_CHAT_ID_HERE"
   
   services:
     notification: ""  # Disable SMS
   ```

4. **Restart Service:**
   ```bash
   ./bin/app
   ```

---

### For DevOps Team (Production)

1. **Deploy Notification Service:**
   ```bash
   # Deploy SMS gateway service
   kubectl apply -f notification-service.yaml
   
   # Verify it's running
   kubectl get svc notification-service
   ```

2. **Update Production Config:**
   ```yaml
   telegram:
     enabled: false       # ⚠️ IMPORTANT: Disable in production
     bot_token: ""
     chat_id: ""
   
   services:
     notification: "notification-service.production.svc.cluster.local:9100"
   ```

3. **Secrets Management:**
   ```bash
   # Store sensitive configs in Vault/K8s Secrets
   kubectl create secret generic auth-service-config \
     --from-literal=notification-url=notification-service:9100 \
     --from-literal=jwt-secret=PRODUCTION_SECRET
   ```

4. **Environment Variables (Optional):**
   ```bash
   export NOTIFICATION_SERVICE_URL="notification-service:9100"
   export TELEGRAM_ENABLED="false"
   ```

5. **Deploy:**
   ```bash
   kubectl apply -f centre-auth-service.yaml
   kubectl rollout status deployment/centre-auth-service
   ```

---

## 📊 Configuration Matrix

| Environment | Telegram | SMS | Use Case |
|-------------|----------|-----|----------|
| **Development** | ✅ Enabled | ❌ Disabled | Local testing, no SMS costs |
| **Staging** | ✅ Enabled | ✅ Enabled | QA testing both methods |
| **Production** | ❌ Disabled | ✅ Enabled | Real users, professional delivery |

---

## 🧪 Testing Each Configuration

### Test Development Config (Telegram)
```bash
# 1. Ensure config has Telegram enabled
grep -A 3 "telegram:" config/config.yaml

# 2. Restart service
./bin/app &

# 3. Send OTP
curl -s http://localhost:8080/api/v1/cas/auth/otp-register \
  -H 'Content-Type: application/json' \
  -d '{"phone_number": "0999888777"}'

# 4. Check Telegram app for OTP message
```

### Test Production Config (SMS)
```bash
# 1. Ensure SMS service is configured
grep "notification:" config/config.yaml

# 2. Ensure Telegram is disabled
grep -A 2 "telegram:" config/config.yaml | grep "enabled: false"

# 3. Restart service
./bin/app &

# 4. Send OTP
curl -s http://localhost:8080/api/v1/cas/auth/otp-register \
  -H 'Content-Type: application/json' \
  -d '{"phone_number": "0999888777"}'

# 5. Check phone for SMS
```

---

## 🔐 Security Considerations

### Development
- ✅ Bot token in config file is OK (not in production)
- ✅ Single chat ID for testing
- ✅ More relaxed rate limits

### Production
- ⚠️ **Never commit bot tokens to git**
- ⚠️ **Never enable Telegram in production** (single-user limitation)
- ✅ Use environment variables or secrets management
- ✅ Strict rate limiting
- ✅ Monitor SMS costs

---

## 📝 Config File Templates

### Create Multiple Configs

```bash
cd centre-auth-service/config

# Development
cp config.yaml config.development.yaml
# Edit: telegram.enabled=true, services.notification=""

# Staging  
cp config.yaml config.staging.yaml
# Edit: both enabled

# Production
cp config.yaml config.production.yaml
# Edit: telegram.enabled=false, services.notification="real-sms-service"
```

### Load Config by Environment

```bash
# Development
ENV=development ./bin/app

# Production
ENV=production ./bin/app
```

### In Code (config/config.go)
```go
func LoadConfig() (*Config, error) {
    env := os.Getenv("ENV")
    if env == "" {
        env = "development"
    }
    
    configFile := fmt.Sprintf("config/config.%s.yaml", env)
    if _, err := os.Stat(configFile); os.IsNotExist(err) {
        configFile = "config/config.yaml" // fallback
    }
    
    // Load configFile...
}
```

---

## 🎯 Summary for Teams

### Developers (Local Development)
```yaml
✅ telegram.enabled = true
❌ services.notification = ""
📱 Get OTP from Telegram
💰 Zero SMS costs
```

### QA Team (Staging)
```yaml
✅ telegram.enabled = true (for quick testing)
✅ services.notification = "staging-sms" (validate real flow)
🧪 Test both delivery methods
```

### DevOps (Production)
```yaml
❌ telegram.enabled = false
✅ services.notification = "production-sms:9100"
🔐 Use secrets management
📊 Monitor delivery rates
```

---

## 🔄 Migration Path

### Phase 1: Development (Current)
- Use Telegram for all developers
- Zero infrastructure needed

### Phase 2: Staging
- Deploy notification service
- Test SMS integration
- Keep Telegram for QA

### Phase 3: Production
- Disable Telegram
- Enable production SMS
- Monitor and scale

---

## 📞 Support

### Issues?

**Telegram not working:**
```bash
# Test bot directly
curl "https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<CHAT_ID>&text=Test"

# Check service logs
tail -f logs/app.log | grep telegram
```

**SMS not working:**
```bash
# Check notification service
curl http://notification-service:9100/health

# Check service logs
tail -f logs/app.log | grep sms
```

---

**Last Updated:** December 17, 2025  
**Maintained By:** @thatlq1812

**Remember:** 
- Development = Telegram (fast & free)
- Production = SMS (professional & scalable)
- DevOps handles production config!
