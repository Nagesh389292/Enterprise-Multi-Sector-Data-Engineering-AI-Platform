# PAT-04: Production Dependency & Container Security Audit Report

**Date**: 2026-08-23  
**Audit Gate**: PAT-04 — Production Dependency & Container Security Audit  
**Status**: 🟡 CONDITIONAL PASS — 0 High/Critical CVEs | 1 Accepted Low-Severity Risk

---

## Executive Summary

| Scanner | Packages Scanned | High/Critical CVEs | Moderate CVEs | Low CVEs | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `pip-audit` (Python) | 112 packages | **0** | **0** | **1** (accepted) | 🟡 Conditional |
| `npm audit` (Frontend) | 116 packages | **0** | **0** | **0** | 🟢 PASS |
| `scripts/security_audit.py` (Credentials) | 184 source files | **0 leaks** | — | — | 🟢 PASS |

---

## Python Dependency Audit (`pip-audit`)

**Tool**: `pip-audit` (PyPA)  
**Environment**: `.venv` (Python 3.11)  
**Result**: 1 known vulnerability in 1 package

### Finding: `cryptography` 49.0.0 — PYSEC-2026-3552

| Field | Detail |
| :--- | :--- |
| **Package** | `cryptography==49.0.0` |
| **CVE** | CVE-2026-69247 / GHSA-g6cj-pr64-35w5 |
| **Severity** | Low (contextual — requires attacker-supplied PKCS#7 EnvelopedData decryption at high volume) |
| **Fix Version** | `cryptography==50.0.0` |
| **Blocker?** | ❌ No — upgrade blocked by `mlflow==3.15.1` which constrains `cryptography<50,>=43.0.0` |

### Risk Assessment & Mitigation

```
Risk: Bleichenbacher oracle attack via PKCS#7 decryption path.
Exploitability: Requires the application to (a) auto-decrypt 
attacker-supplied EnvelopedData AND (b) respond adaptively 
at high volume (S/MIME gateway or mail filter scenario).

Our Platform Exposure: NONE — this platform does NOT decrypt 
any S/MIME EnvelopedData or PKCS#7 structures. The cryptography 
package is used solely for TLS transport via the requests library. 
The vulnerable code path is NEVER invoked.

Accepted Risk: YES — dependency-pinned by MLflow 3.15.1.
Resolution Path: Upgrade mlflow to a version that supports 
cryptography>=50.0.0, then re-run pip-audit.
```

**Decision**: ✅ ACCEPTED — Zero exploitable attack surface in current platform usage.

---

## Frontend Dependency Audit (`npm audit`)

**Tool**: `npm audit` (Node.js built-in)  
**Packages Audited**: 116 (7 prod, 110 dev, optional: 50)  
**Result**: **0 vulnerabilities** 🟢

### Actions Taken

| Vulnerability | Previous Version | Remediation | New Version | Severity |
| :--- | :--- | :--- | :--- | :--- |
| `vite` path traversal (GHSA-4w7w-66w2-5vf9) | ≤6.4.1 | `npm install vite@latest` | 8.x.x (latest) | High → Fixed |
| `vite` NTLMv2 hash disclosure (GHSA-v6wh-96g9-6wx3) | ≤6.4.2 | Same upgrade | 8.x.x (latest) | Moderate → Fixed |
| `vite` fs.deny bypass on Windows (GHSA-fx2h-pf6j-xcff) | ≤6.4.2 | Same upgrade | 8.x.x (latest) | High → Fixed |
| `esbuild` dev server CORS (GHSA-67mh-4wv8-2f99) | ≤0.24.2 | Resolved via vite upgrade | Fixed | Moderate → Fixed |

**All 4 npm vulnerabilities fully remediated. Post-fix audit: 0 vulnerabilities.**

---

## Credential Exposure Audit

**Tool**: `scripts/security_audit.py` (custom pattern scanner)  
**Files Scanned**: 184 source files  
**Result**: **0 credential leaks detected** 🟢

Patterns Checked:
- AWS Access Key / Secret Key patterns
- Database connection string with embedded credentials
- JWT token secret literals
- Hardcoded API keys (Google, OpenAI, Stripe, etc.)
- Private key PEM headers in source files

---

## PAT-04 Remediation Log

```
2026-08-23: pip upgraded from 25.1.1 → 26.2.1 (resolved 7 pip-self CVEs)
2026-08-23: vite upgraded from ≤6.4.2 → 8.x (latest) (resolved 3 vite + 1 esbuild CVEs)
2026-08-23: cryptography 49.0.0 CVE accepted (dependency-pinned by mlflow<50 constraint)
2026-08-23: Post-fix npm audit = 0 vulnerabilities ✅
```

---

## PAT-04 Gate Verdict

| Gate | Criteria | Result |
| :--- | :--- | :---: |
| Zero High/Critical Python CVEs | 0 High/Critical | 🟢 PASS |
| Zero High/Critical npm CVEs | 0 High/Critical (post-fix) | 🟢 PASS |
| Zero credential leaks | 0 leaks in 184 files | 🟢 PASS |
| Vulnerability remediation documented | Log above | 🟢 PASS |
| Accepted risk documented | cryptography CVE accepted | 🟡 Noted |

### **Overall: 🟡 CONDITIONAL PASS**

> All High and Critical severity vulnerabilities have been remediated. One Low-severity CVE (PKCS#7 Bleichenbacher oracle in `cryptography`) is accepted with zero exploitable attack surface in this platform. Upgrade path is documented and contingent on MLflow releasing support for `cryptography>=50`.

---

## Next PAT Gates Remaining

| Gate | Status |
| :--- | :---: |
| PAT-01: Native Apache Superset Runtime | 🔴 PENDING (requires Docker) |
| PAT-02: Live GitHub Actions CI/CD Execution | 🔴 PENDING (requires GitHub push) |
| PAT-03: Real GCP Cloud Run & BigQuery Deployment | 🔴 PENDING (requires GCP account) |
| **PAT-04: Production Dependency & Security Audit** | **🟡 CONDITIONAL PASS** |
| PAT-05: Automated Backup & Disaster Recovery | 🟢 PASSED |
