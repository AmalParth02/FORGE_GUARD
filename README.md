# 🛡️ ForgeGuard (SIH PS-188)

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![XGBoost](https://img.shields.io/badge/Risk_Engine-XGBoost-EB6440.svg?style=flat-square)](https://xgboost.readthedocs.io/)
[![Architecture](https://img.shields.io/badge/Pattern-Modular_Monolith-brightgreen.svg?style=flat-square)](#architecture)
[![Privacy](https://img.shields.io/badge/Compliance-DPDP_%2F_GDPR_Zero--Disk-informational.svg?style=flat-square)](#privacy--compliance)

> **High-concurrency, privacy-first automated identity and travel document verification engine designed for automated border control (e-Gates).**


---

##  Architecture Pipeline

```text
[ Document Scan + Live Selfie ]
               │
               ▼  (In-Memory Stream)
      FastAPI API Boundary
               │
       [ asyncio.gather ]
  ┌────────────┼────────────┐
  ▼            ▼            ▼
[ OCR / MRZ ] [ ELA Check ] [ DeepFace ]
(PaddleOCR)   (Forensics)   (Biometrics)
  │            │            │
  └────────────┼────────────┘
               ▼
   Feature Vector [x₁, x₂, ..., x₅]
               │
               ▼
     XGBoost Risk Classifier
               │
    ┌──────────┴──────────┐
    ▼                     ▼
[Risk Probability]   [Audit Flags]
    │                     │
    └──────────┬──────────┘
               ▼
 Strict JSON Schema (Pydantic v2)
               │
       [ Passenger Verdict ]                                                {With proper pointing and logic display}
   LOW (<0.30)  │ MEDIUM (0.30-0.69) │ HIGH (>=0.70)
   (Auto-Clear) │ (Step-Up Bio Check) │ (Interception)
