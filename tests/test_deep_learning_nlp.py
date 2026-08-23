"""
Unit Test Suite for Milestone 8: Selective Deep Learning & NLP.
"""

import os
import unittest
import pandas as pd

from ml.deep_learning.sequence_fraud_lstm import TransactionSequenceModeler
from ml.nlp.clinical_notes_nlp import ClinicalNotesNLP
from ml.nlp.claims_report_nlp import ClaimsReportNLP
from ml.deep_learning.master_deep_learning_nlp import MasterDeepLearningNLP


class TestDeepLearningNLP(unittest.TestCase):
    """Unit tests for PyTorch LSTM sequence modeling and Hugging Face NLP extractions."""

    def test_pytorch_transaction_lstm(self):
        modeler = TransactionSequenceModeler(sequence_length=4)
        df = pd.DataFrame({
            "Amount": [100.0, 300.0, 800.0, 2500.0] * 5,
            "velocity_5m": [1, 2, 3, 5] * 5,
            "amount_zscore": [0.1, 0.5, 1.8, 3.2] * 5,
            "unusual_location": [0, 0, 1, 1] * 5,
            "Class": [0, 0, 1, 1] * 5
        })
        res = modeler.train_and_evaluate(df, epochs=2)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["sequence_length"], 4)
        self.assertIn("final_train_loss", res)

    def test_clinical_notes_nlp(self):
        nlp = ClinicalNotesNLP()
        notes = ["Patient presenting with congestive heart failure and sepsis."]
        res = nlp.analyze_notes(notes)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreater(res["avg_risk_multiplier"], 1.0)

    def test_claims_report_nlp(self):
        nlp = ClaimsReportNLP()
        claims = ["Claim filed for total loss resulting from staged accident."]
        res = nlp.analyze_claims(claims)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["flagged_claims_count"], 1)

    def test_master_deep_learning_nlp(self):
        res = MasterDeepLearningNLP.run_all()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("pytorch_sequence_lstm", res)
        self.assertIn("clinical_notes_nlp", res)
        self.assertIn("insurance_claims_nlp", res)


if __name__ == "__main__":
    unittest.main()
