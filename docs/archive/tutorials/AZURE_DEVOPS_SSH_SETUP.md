# Azure DevOps SSH Configuration Guide

## Problem Description

When using `go mod tidy` or `make api`, the system tries to download dependencies using HTTPS instead of SSH, causing authentication issues. This happens because:

1. Git may be configured with PAT (Personal Access Token) for HTTPS
2. Go modules default to HTTPS URLs from Azure DevOps
3. Multiple authentication methods conflict with each other

## Solution Overview

Configure Git to automatically rewrite HTTPS URLs to SSH for all Azure DevOps repositories. This ensures consistent use of SSH keys for authentication.

---

## Prerequisites

1. **SSH Key Setup**: Ensure you have SSH keys configured in Azure DevOps
   - Generate SSH key: `ssh-keygen -t rsa -b 4096 -C "your.email@company.com"`
   - Add public key to Azure DevOps: User Settings > SSH public keys
   
2. **Test SSH Connection**:
   ```bash
   ssh -T git@ssh.dev.azure.com
   ```
   Expected output: `remote: Shell access is not supported.` (Exit code 255 is normal)

3. **Go Environment Variables**:
   ```bash
   go env -w GOPRIVATE=dev.azure.com
   ```

---

## Manual Configuration Steps

### 1. Remove Old PAT Configuration

```bash
# List all URL configurations
git config --global --get-regexp url

# Remove PAT-based configuration if exists - replace YOUR_TOKEN with actual token part
git config --global --unset-all url."https://pat:YOUR_TOKEN@dev.azure.com/".insteadof
```

### 2. Configure Git URL Rewriting

```bash
# General Azure DevOps rewrite
git config --global url."git@ssh.dev.azure.com:v3/".insteadOf "https://dev.azure.com/"

# Organization-specific rewrite
git config --global url."git@ssh.dev.azure.com:v3/agris-agriculture/".insteadOf "https://dev.azure.com/agris-agriculture/"

# All below is example for agris-agriculture organization
# Project-specific rewrite (for _git/ paths)
git config --global url."git@ssh.dev.azure.com:v3/agris-agriculture/Core/".insteadOf "https://dev.azure.com/agris-agriculture/Core/_git/"
```

### 3. Configure Go Private Modules

```bash
go env -w GOPRIVATE=dev.azure.com
```

### 4. Clone Repositories Using SSH

```bash
# Move to root directory
cd /path/to/your/workspace 
# Change to your desired directory #

git clone git@ssh.dev.azure.com:v3/agris-agriculture/CAS/centre-auth-service
git clone git@ssh.dev.azure.com:v3/agris-agriculture/Utility/noti-service
git clone git@ssh.dev.azure.com:v3/agris-agriculture/Core/Core
git clone git@ssh.dev.azure.com:v3/agris-agriculture/Core/library
git clone git@ssh.dev.azure.com:v3/agris-agriculture/Gateway/app-api-gateway

# And others as needed
```

```bash
# Move to root directory
cd /path/to/your/workspace 
# Change to your desired directory #

cd centre-auth-service && git remote -v && cd ..
cd noti-service && git remote -v && cd ..
cd Core && git remote -v && cd ..
cd library && git remote -v && cd ..
cd app-api-gateway && git remote -v && cd ..

# And others as needed
```

### 5. Build and Run (per repository)

```bash
cd centre-auth-service
go mod tidy
make api

cd ../noti-service
go mod tidy
make api

cd ../Core
go mod tidy
make api

cd ../library
go mod tidy
make api

cd ../app-api-gateway
go mod tidy
make api

# And others as needed
```
---

## Troubleshooting

### Issue: "fatal: Authentication failed"

**Solution**: Check SSH key configuration
```bash
# Test SSH connection
ssh -T git@ssh.dev.azure.com

# List SSH keys
ls -la ~/.ssh/

# Ensure ssh-agent is running
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
```

### Issue: "git protocol 'git://' is not supported"

**Solution**: This happens when Go tries to use git:// protocol. The URL rewriting should prevent this. Verify:
```bash
git config --global --get-regexp url
```

### Issue: "expected _full or _optimized, not '_git'"

**Solution**: This error occurs when Go tries to access repositories with `_git` in the path. The specific URL rewrite rule handles this:
```bash
git config --global url."git@ssh.dev.azure.com:v3/agris-agriculture/Core/".insteadOf "https://dev.azure.com/agris-agriculture/Core/_git/"
```

### Issue: "Cannot prompt because user interactivity has been disabled"

**Solution**: This means Git is trying to use HTTPS without credentials. Verify SSH configuration is correct and PAT configuration is removed.

### Issue: Go modules not using SSH

**Solution**:
1. Ensure GOPRIVATE is set: `go env -w GOPRIVATE=dev.azure.com`
2. Clear Go module cache: `go clean -modcache`
3. Try download again: `go mod download -x` (verbose mode)

---

## Common Scenarios

### Scenario 1: New Team Member Setup

1. Generate SSH key and add to Azure DevOps
2. Run automatic configuration script
3. Clone repositories using SSH URLs
4. Build projects

### Scenario 2: Existing Developer with HTTPS Setup

1. Backup current configuration: `git config --global --list > git-config-backup.txt`
2. Run automatic configuration script
3. Update existing repository remotes to SSH
4. Test with `go mod tidy`

### Scenario 3: CI/CD Pipeline

1. Configure SSH keys in pipeline secrets
2. Add SSH key to ssh-agent in pipeline script
3. Run configuration script in pipeline
4. Execute build commands

---

## Best Practices

1. **Always use SSH URLs** when cloning Azure DevOps repositories
2. **Document SSH key rotation** process for team
3. **Include SSH setup** in onboarding documentation
4. **Test SSH connection** before running builds
5. **Keep this guide updated** as Azure DevOps configuration changes

---

## Last Updated

Date: December 17, 2025
Version: 1.0
Maintainer: That Le
