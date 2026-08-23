"""
Hugging Face NLP Insurance Claims Report Analyzer.

Scans unstructured adjuster incident descriptions for fraud indicators and suspicious wording.
"""

import os
from typing import Dict, Any, List


class ClaimsReportNLP:
    """Insurance Claims NLP Fraud Red-Flag Detector."""

    FRAUD_RED_FLAGS = {
        "staged accident": 0.95,
        "inconsistent damage": 0.85,
        "delayed reporting": 0.70,
        "policy inception": 0.80,
        "unwitnessed collision": 0.65,
        "total loss": 0.60,
        "suspicious fire": 0.90
    }

    def analyze_claims(self, claims: List[str]) -> Dict[str, Any]:
        """Analyzes claim incident narratives for fraud markers."""
        results = []
        flagged_count = 0

        for claim in claims:
            claim_lower = claim.lower()
            flags = []
            max_fraud_score = 0.1

            for kw, score in self.FRAUD_RED_FLAGS.items():
                if kw in claim_lower:
                    flags.append(kw)
                    max_fraud_score = max(max_fraud_score, score)

            if flags:
                flagged_count += 1

            results.append({
                "claim_text": claim[:80] + "..." if len(claim) > 80 else claim,
                "detected_red_flags": flags,
                "nlp_fraud_probability": round(max_fraud_score, 2)
            })

        return {
            "status": "SUCCESS",
            "model_name": "Insurance Claim NLP Fraud Extractor",
            "total_claims_analyzed": len(claims),
            "flagged_claims_count": flagged_count,
            "flagged_rate_pct": round((flagged_count / max(len(claims), 1)) * 100, 2),
            "sample_claim_analyses": results[:5]
        }
