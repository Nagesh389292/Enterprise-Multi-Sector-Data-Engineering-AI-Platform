"""
Verification Script for Milestone 8: Selective Deep Learning & NLP.

Verifies:
1. PyTorch LSTM Transaction Sequence Fraud Model Execution & Loss
2. Clinical EHR Notes NLP Keyword & Risk Extractor
3. Insurance Claims NLP Incident Report Fraud Scorer
4. Copilot Grounding on Deep Learning / NLP Outputs
Outputs verify_milestone8_report.json
"""

import os
import sys
import json
import time

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from ml.deep_learning.master_deep_learning_nlp import MasterDeepLearningNLP
from ai.agent.metrics_tool import MetricsTool

REPORT_PATH = os.path.join(os.getcwd(), "verify_milestone8_report.json")


def verify_milestone8():
    print("==========================================================================================")
    print("       MILESTONE 8: SELECTIVE DEEP LEARNING & NLP VERIFICATION SUITE")
    print("==========================================================================================")

    # 1. Run Master Deep Learning & NLP Pipeline
    print("\n[Step 1/3] Executing PyTorch LSTM & Hugging Face NLP Pipeline...")
    res = MasterDeepLearningNLP.run_all()
    assert res["status"] == "SUCCESS", f"Master DL/NLP failed: {res}"
    print("✓ Master Deep Learning & NLP pipeline executed cleanly.")

    # 2. Verify Output Components
    print("\n[Step 2/3] Verifying PyTorch LSTM & NLP Output Metrics...")
    lstm_out = res["pytorch_sequence_lstm"]
    assert lstm_out["status"] == "SUCCESS" and "final_train_loss" in lstm_out, "LSTM output missing"
    print(f"✓ PyTorch Transaction LSTM: Final Loss = {lstm_out['final_train_loss']} | Sequences = {lstm_out['total_sequences_evaluated']}")

    clin_out = res["clinical_notes_nlp"]
    assert clin_out["status"] == "SUCCESS" and clin_out["total_notes_analyzed"] > 0, "Clinical NLP missing"
    print(f"✓ Clinical Notes NLP: Analyzed = {clin_out['total_notes_analyzed']} | Avg Multiplier = {clin_out['avg_risk_multiplier']}")

    claims_out = res["insurance_claims_nlp"]
    assert claims_out["status"] == "SUCCESS" and claims_out["flagged_claims_count"] > 0, "Claims NLP missing"
    print(f"✓ Insurance Claims NLP: Flagged Rate = {claims_out['flagged_rate_pct']}% ({claims_out['flagged_claims_count']}/{claims_out['total_claims_analyzed']})")

    # 3. Verify Copilot Metric Tool Grounding
    print("\n[Step 3/3] Verifying Copilot Grounding on Deep Learning / NLP Outputs...")
    metrics_tool = MetricsTool()
    cop_dl = metrics_tool.get_deep_learning_nlp_results()
    assert cop_dl.get("status") == "SUCCESS", "Copilot failed to load deep learning / nlp results"
    print("✓ Copilot successfully grounded in Deep Learning & NLP outputs.")

    report = {
        "milestone": "Milestone 8: Selective Deep Learning & NLP",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "COMPLETED_AND_VERIFIED",
        "pytorch_sequence_lstm": {
            "model": lstm_out["model_name"],
            "sequence_length": lstm_out["sequence_length"],
            "final_train_loss": lstm_out["final_train_loss"],
            "high_risk_sequences": lstm_out["high_risk_sequences_detected"]
        },
        "clinical_nlp": {
            "model": clin_out["model_name"],
            "notes_analyzed": clin_out["total_notes_analyzed"],
            "avg_risk_multiplier": clin_out["avg_risk_multiplier"]
        },
        "claims_nlp": {
            "model": claims_out["model_name"],
            "claims_analyzed": claims_out["total_claims_analyzed"],
            "flagged_rate_pct": claims_out["flagged_rate_pct"]
        },
        "verification_result": "PASSED"
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n==========================================================================================")
    print(f"   MILESTONE 8 VERIFICATION PASSED (PyTorch LSTM + NLP Verified) | Report: {REPORT_PATH}")
    print("==========================================================================================")
    return report


if __name__ == "__main__":
    verify_milestone8()
