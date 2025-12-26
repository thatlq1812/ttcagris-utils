# Centre Auth Service (CAS)

***បាន​បង្កើត:*** 2025-12-26

***ធ្វើ​បច្ចុប្បន្នភាព​ចុងក្រោយ:*** 2025-12-26

***Version:*** 1.0.0

***Status:*** សកម្ម

---

## ទិដ្ឋភាពទូទៅ

**Centre Auth Service (CAS)** គឺជា microservice ផ្ទៀងផ្ទាត់ភាពត្រឹមត្រូវ និងការអនុញ្ញាតកណ្តាលសម្រាប់ AgriOS Platform។ វាគ្រប់គ្រងអត្តសញ្ញាណអ្នកប្រើប្រាស់ លំហូរផ្ទៀងផ្ទាត់ភាពត្រឹមត្រូវ ការគ្រប់គ្រងសិទ្ធិចូលប្រើប្រាស់ផ្អែកលើតួនាទី (RBAC) និងធ្វើសមាហរណកម្មជាមួយសេវាកម្មខាងក្រៅសម្រាប់ការផ្ទៀងផ្ទាត់ eKYC ។

**ទំនួលខុសត្រូវចម្បង៖**

- ការផ្ទៀងផ្ទាត់ភាពត្រឹមត្រូវរបស់ User (អ៊ីមែល, ទូរស័ព្ទ, SSO)
- ការគ្រប់គ្រងគណនី និងអត្តសញ្ញាណ
- ការគ្រប់គ្រងសិទ្ធិចូលប្រើប្រាស់ផ្អែកលើតួនាទី (RBAC)
- ការគ្រប់គ្រង `JWT` token
- ការផ្ទៀងផ្ទាត់អត្តសញ្ញាណ eKYC
- ការគ្រប់គ្រងទម្រង់កសិករ និងអ្នកផ្គត់ផ្គង់

---

## ឯកសារយោងរហ័ស

| Item | Value |
| --- | --- |
| **gRPC Port** | 50051 |
| **HTTP Port** | 4000 |
| **Database** | PostgreSQL 17+ |
| **Cache** | Redis 7+ |
| **Language** | Go 1.25+ |

---

## លក្ខណៈ​ពិសេស​សំខាន់ៗ

### ការផ្ទៀងផ្ទាត់

- ការផ្ទៀងផ្ទាត់ភាពត្រឹមត្រូវតាមរយៈអ៊ីមែល/ពាក្យសម្ងាត់
- ការផ្ទៀងផ្ទាត់ភាពត្រឹមត្រូវតាមទូរស័ព្ទ/OTP
- ការរួមបញ្ចូល Azure SSO
- ការចូលប្រើ JWT និង refresh tokens
- ការគ្រប់គ្រង​សession​ឧបករណ៍

### ការគ្រប់គ្រង User

- ប្រតិបត្តិការ CRUD គណនី
- ការគ្រប់គ្រងទម្រង់ User
- ការចុះឈ្មោះ និងការគ្រប់គ្រងកសិករ
- ការចុះឈ្មោះ និងការគ្រប់គ្រងអ្នកផ្គត់ផ្គង់

### ការអនុញ្ញាត

- ការគ្រប់គ្រង​សិទ្ធិ​ចូល​ប្រើ​ផ្អែក​លើ​តួនាទី (RBAC) តាមរយៈ Casbin
- ការគ្រប់គ្រង​សិទ្ធិ
- ការអនុញ្ញាតកម្រិត API

### ការដាក់បញ្ចូល eKYC

- OCR សម្រាប់ ការអាន អត្តសញ្ញាណប័ណ្ណ
- ការរកឃើញភាពរស់រវើកនៃផ្ទៃមុខ
- ការប្រៀបធៀបផ្ទៃមុខ
- លំហូរការងារផ្ទៀងផ្ទាត់អត្តសញ្ញាណ

---

## ស្ថាបត្យកម្ម

```
┌─────────────────┐      ┌─────────────────┐
│   API Gateway   │─────▶│       CAS       │
│   (REST/JSON)   │      │   (gRPC:50051)  │
└─────────────────┘      └────────┬────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
   │  PostgreSQL │         │    Redis    │         │   Azure     │
   │  (Database) │         │   (Cache)   │         │   Blob      │
   └─────────────┘         └─────────────┘         └─────────────┘
```

---

## អង្គភាពដែន

| Entity | Description |
| --- | --- |
| **Account** | Authentication identity (email/phone/SSO) |
| **User** | Personal profile ដែលភ្ជាប់ទៅ account |
| **Farmer** | Agricultural producer profile |
| **Supplier** | Service provider profile |
| **Ekyc** | Identity verification data |
| **Role** | Access control role |
| **Permission** | API endpoint access rights |

---

## សេវាកម្ម gRPC

| Service | Description |
| --- | --- |
| `AuthService` | Login, logout, ការគ្រប់គ្រង token |
| `MobileAuthService` | authentication ជាក់លាក់សម្រាប់ Mobile |
| `AccountService` | ប្រតិបត្តិការ Account CRUD |
| `UserService` | ការគ្រប់គ្រង profile User |
| `FarmerService` | ការគ្រប់គ្រង Farmer |
| `SupplierService` | ការគ្រប់គ្រង Supplier |
| `RoleService` | ការគ្រប់គ្រង Role |
| `PermissionService` | ការគ្រប់គ្រង Permission |
| `EkycService` | ប្រតិបត្តិការ eKYC |
| `DeviceService` | ការគ្រប់គ្រង session Device |

---

## ឯកសារ​ពាក់ព័ន្ធ

| Document | Description | Audience |
| --- | --- | --- |
| [SRS_centre_auth_service.md](SRS_centre_auth_service.md) | លក្ខណៈ​ពិសេស​នៃ​តម្រូវការ​កម្មវិធី | PO, QA, Dev |
| [TDD_centre_auth_service.md](TDD_centre_auth_service.md) | ឯកសារ​រចនា​បច្ចេកទេស | Dev, DevOps |
| [PROC_development_workflow.md](PROC_development_workflow.md) | ដំណើរការ​អភិវឌ្ឍន៍ | Dev |
| [centre-auth-service/README.md](../../../centre-auth-service/README.md) | README បច្ចេកទេស | Dev |

---

## ទំនាក់ទំនង

- **ក្រុម**: ក្រុម Backend
- **ឃ្លាំងផ្ទុកទិន្នន័យ**: `dev.azure.com/agris-agriculture/Core/_git/centre-auth-service`
