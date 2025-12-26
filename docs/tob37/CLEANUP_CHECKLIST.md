# TOB-37 Cleanup Checklist

**Purpose:** Prerequisites to delete TOB-37 folder after production migration  
**Created:** 2025-12-23

---

## Folder Contents

```
TOB-37/
├── MASTER_GUIDE.md           # Documentation
├── MIGRATION_PLAN.md         # Migration planning
├── UPGRADE_GUIDE.md          # Upgrade documentation
├── demo-mobile-app/          # React Native POC app
│   ├── MOBILE_SDK_GUIDE.md   # SDK guide for mobile devs
│   ├── src/
│   │   ├── config/eventConfig.js
│   │   ├── handlers/eventHandlers.js
│   │   ├── services/fcmService.js
│   │   └── components/DebugOverlay.js
│   └── [other RN files]
└── test-fcm/                 # Go test script
    └── main.go
```

---

## Cleanup Prerequisites

### Documentation Migration

- [ ] Move `MASTER_GUIDE.md` → `docs/services/FCM_EVENT_SYSTEM.md`
- [ ] Move `MOBILE_SDK_GUIDE.md` → `docs/mobile/FCM_INTEGRATION.md`
- [ ] Archive or delete `UPGRADE_GUIDE.md` (internal only)
- [ ] Archive or delete `MIGRATION_PLAN.md` (internal only)

### Code Migration to Noti-service

- [ ] `EventPayload` struct defined in Core proto
- [ ] Action code registry implemented
- [ ] `SendEvent` gRPC handler implemented
- [ ] Unit tests passing
- [ ] Deployed to production

### Code Migration to CAS

- [ ] Updated notification client using new proto
- [ ] All `SendForceLogoutNotification` calls updated
- [ ] Unit tests passing
- [ ] Deployed to production

### Mobile App Migration

- [ ] `eventConfig.js` integrated into real app
- [ ] `eventHandlers.js` integrated into real app
- [ ] `fcmService.js` integrated into real app
- [ ] `DebugOverlay.js` integrated (if needed)
- [ ] All action codes tested end-to-end
- [ ] App deployed to production

### Verification Tests

- [ ] CAS → Noti-service → FCM → Mobile works
- [ ] Force logout (001, 101) tested
- [ ] Profile update (002, 102) tested
- [ ] Navigation events (003, 301) tested
- [ ] Idempotency working (no duplicate processing)

### Cleanup Confirmation

- [ ] All team members notified
- [ ] No active branches referencing TOB-37
- [ ] Git history preserved (files moved, not deleted without trace)
- [ ] Backup created (optional)

---

## Delete Command

Once ALL checkboxes above are checked:

```bash
# From workspace root
rm -rf TOB-37/

# Or on Windows
rmdir /s /q TOB-37
```

---

## Post-Cleanup

- [ ] Update any references to TOB-37 in:
  - README.md files
  - CI/CD pipelines
  - Documentation links
- [ ] Close related Jira/Azure DevOps tickets
- [ ] Remove TOB-37 from workspace structure docs

---

## Rollback Plan

If issues found after deletion:

1. Git restore: `git checkout HEAD~1 -- TOB-37/`
2. Or restore from backup
3. Or recreate from this documentation

---

**Note:** This checklist is intentionally comprehensive. Some items may be skipped if deemed unnecessary by the team lead.

