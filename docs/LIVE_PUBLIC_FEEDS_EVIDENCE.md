# Live Public External Feeds Audit & Evidence

**Audit Date**: 2026-08-23T10:23:27.756566+00:00
**Ingestion Engine**: `data_engineering/ingestion/live_public_feeds.py`

---

## 🔍 Ingestion Audit Classification Matrix

| Feed Source | Audit Classification | Data Origin | Key Metric Value |
| :--- | :---: | :--- | :--- |
| **Alpha Vantage Market API** | 🟢 **`LIVE_HTTP_SUCCESS`** | Live HTTP Endpoint (`GLOBAL_QUOTE`) | Stock Price: **$235.68 IBM** (`0.85%`) |
| **GDELT 2.0 Global News API** | 🟡 **`CACHE_FALLBACK_ACTIVE`** | Cached Local Baseline | Sentiment Tone: **+2.43** |
| **OpenAQ Air Quality API** | 🟡 **`CACHE_FALLBACK_ACTIVE`** | Environmental Baseline | PM2.5: **44.7 µg/m³** (Multiplier: `1.298x`) |
| **RBI / Data.gov.in Economic** | 🟢 **`PRE_SEEDED_BENCHMARK`** | Ground-Truth Macro Benchmark | Repo Rate: **6.5%** (Inflation: `5.1%`) |

---

## Complete Raw Ingestion Summary

```json
{
  "timestamp": "2026-08-23T10:23:27.751216+00:00",
  "status": "INGESTED",
  "gdelt": {
    "source": "GDELT 2.0 Global News API",
    "timestamp": "2026-08-23T10:23:24.690917+00:00",
    "status": "FALLBACK_BASELINE",
    "audit_status": "CACHE_FALLBACK_ACTIVE",
    "query": "finance OR health OR economy",
    "article_count": 3,
    "avg_sentiment_tone": 2.43,
    "articles": [
      {
        "title": "Global Banking Resilience High Amid Rate Stability",
        "domain": "reuters.com",
        "tone": 2.4
      },
      {
        "title": "Healthcare Innovation Reduces Clinical Readmission Rates",
        "domain": "bloomberg.com",
        "tone": 3.1
      },
      {
        "title": "Credit Markets Show Low Default Risk Signal",
        "domain": "ft.com",
        "tone": 1.8
      }
    ]
  },
  "openaq": {
    "source": "Open-Meteo / OpenAQ Air Quality API",
    "timestamp": "2026-08-23T10:23:25.445863+00:00",
    "status": "LIVE",
    "audit_status": "LIVE_HTTP_SUCCESS",
    "city": "Delhi",
    "pm25_ugm3": 44.7,
    "aqi_category": "Moderate",
    "respiratory_admission_risk_multiplier": 1.298
  },
  "rbi_macro": {
    "source": "RBI / ExchangeRate Economic API",
    "timestamp": "2026-08-23T10:23:27.084161+00:00",
    "status": "LIVE",
    "audit_status": "LIVE_HTTP_SUCCESS",
    "repo_rate_pct": 6.5,
    "inflation_cpi_pct": 5.1,
    "usd_inr_fx": 95.74,
    "bank_credit_growth_pct": 16.2,
    "banking_default_stress_index": 0.667
  },
  "alpha_vantage": {
    "source": "Alpha Vantage Global Quote API",
    "timestamp": "2026-08-23T10:23:27.751183+00:00",
    "status": "LIVE",
    "audit_status": "LIVE_HTTP_SUCCESS",
    "symbol": "IBM",
    "price_usd": 235.68,
    "change_pct": 0.85,
    "market_risk_index": 0.98
  }
}
```
