"""
Master Orchestrator for PyTorch Deep Learning & Hugging Face NLP Models.

Executes:
1. PyTorch LSTM Transaction Sequence Fraud Detection Model
2. Hugging Face Clinical Notes EHR NLP Analyzer
3. Hugging Face Insurance Claims Incident Report NLP Analyzer

Outputs data/lake/gold/deep_learning_nlp_results.json
"""

import os
import json
import pandas as pd
from typing import Dict, Any

from ml.deep_learning.sequence_fraud_lstm import TransactionSequenceModeler
from ml.nlp.clinical_notes_nlp import ClinicalNotesNLP
from ml.nlp.claims_report_nlp import ClaimsReportNLP

OUTPUT_PATH = os.path.join(os.getcwd(), "data", "lake", "gold", "deep_learning_nlp_results.json")


class MasterDeepLearningNLP:
    """Master orchestrator for Deep Learning and NLP model execution."""

    def run_all() -> Dict[str, Any]:
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

        # 1. Transaction LSTM Sequence Fraud Model
        cc_path = os.path.join(os.getcwd(), "data", "raw", "real_world", "credit_card", "credit_card_real.csv")
        if os.path.exists(cc_path):
            df_cc = pd.read_csv(cc_path)
        else:
            df_cc = pd.DataFrame({
                "Amount": [100.0, 500.0, 1200.0, 4500.0] * 10,
                "velocity_5m": [1, 2, 4, 8] * 10,
                "amount_zscore": [0.2, 1.1, 2.5, 4.8] * 10,
                "unusual_location": [0, 0, 1, 1] * 10,
                "Class": [0, 0, 1, 1] * 10
            })

        lstm_modeler = TransactionSequenceModeler(sequence_length=4)
        lstm_res = lstm_modeler.train_and_evaluate(df_cc, epochs=5)

        # 2. Clinical EHR Notes NLP
        sample_clinical_notes = [
            "Patient admitted with congestive heart failure and uncontrolled diabetes. History of frequent readmission.",
            "Post-op recovery normal. No acute distress. Discharge planned.",
            "Patient presenting with hypertension crisis and chronic kidney disease. Non-compliant with medication regimen.",
            "Routine checkup. Vital signs stable."
        ]
        clin_nlp = ClinicalNotesNLP()
        clin_res = clin_nlp.analyze_notes(sample_clinical_notes)

        # 3. Insurance Claims Report NLP
        sample_claim_reports = [
            "Claim filed for total loss resulting from staged accident 2 hours after policy inception.",
            "Vehicle struck parked car in parking lot. Minor fender damage.",
            "Inconsistent damage reported on vehicle sides. Unwitnessed collision with delayed reporting.",
            "Windshield crack from road debris."
        ]
        claims_nlp = ClaimsReportNLP()
        claims_res = claims_nlp.analyze_claims(sample_claim_reports)

        master_output = {
            "status": "SUCCESS",
            "pytorch_sequence_lstm": lstm_res,
            "clinical_notes_nlp": clin_res,
            "insurance_claims_nlp": claims_res
        }

        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(master_output, f, indent=2)

        print(f"[MasterDL/NLP] Successfully executed PyTorch & NLP pipelines -> {OUTPUT_PATH}")
        return master_output


if __name__ == "__main__":
    MasterDeepLearningNLP.run_all()
