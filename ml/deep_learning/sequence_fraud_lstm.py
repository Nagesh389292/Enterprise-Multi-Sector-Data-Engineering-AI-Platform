"""
PyTorch Transaction Sequence Fraud Detection Model (LSTM).

Evaluates temporal sequence windows of cardholder transactions [t-3, t-2, t-1, t]
to capture velocity escalation and sequential fraud patterns.
"""

import os
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from typing import Dict, Any, List


class TransactionLSTM(nn.Module):
    """PyTorch LSTM for sequential transaction fraud detection."""

    def __init__(self, input_size: int = 4, hidden_size: int = 16, num_layers: int = 1):
        super(TransactionLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len, input_size)
        out, (hn, cn) = self.lstm(x)
        # Take output of last sequence step
        last_out = out[:, -1, :]
        logits = self.fc(last_out)
        probs = self.sigmoid(logits)
        return probs


class TransactionSequenceModeler:
    """Trainer and evaluator for PyTorch Transaction Sequence LSTM."""

    def __init__(self, sequence_length: int = 4):
        self.sequence_length = sequence_length
        self.model = TransactionLSTM(input_size=4, hidden_size=16)
        self.criterion = nn.BCELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)

    def prepare_sequence_data(self, df: pd.DataFrame) -> tuple:
        """Converts tabular transaction features into (batch, seq_len, num_features) tensors."""
        features = ["Amount", "velocity_5m", "amount_zscore", "unusual_location"]
        for col in features:
            if col not in df.columns:
                df[col] = 0.0

        data_matrix = df[features].values.astype(np.float32)
        labels = df["Class"].values.astype(np.float32) if "Class" in df.columns else np.zeros(len(df), dtype=np.float32)

        X_seq, y_seq = [], []
        for i in range(len(data_matrix) - self.sequence_length + 1):
            X_seq.append(data_matrix[i : i + self.sequence_length])
            y_seq.append(labels[i + self.sequence_length - 1])

        if not X_seq:
            # Fallback for short data
            X_seq = [np.zeros((self.sequence_length, 4), dtype=np.float32)]
            y_seq = [0.0]

        X_tensor = torch.tensor(np.array(X_seq), dtype=torch.float32)
        y_tensor = torch.tensor(np.array(y_seq), dtype=torch.float32).unsqueeze(1)
        return X_tensor, y_tensor

    def train_and_evaluate(self, df: pd.DataFrame, epochs: int = 10) -> Dict[str, Any]:
        """Trains the LSTM sequence model and returns evaluation metrics."""
        X_tensor, y_tensor = self.prepare_sequence_data(df)
        
        self.model.train()
        losses = []
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            outputs = self.model(X_tensor)
            loss = self.criterion(outputs, y_tensor)
            loss.backward()
            self.optimizer.step()
            losses.append(float(loss.item()))

        self.model.eval()
        with torch.no_grad():
            final_preds = self.model(X_tensor).numpy().flatten()

        high_risk_sequences = int(np.sum(final_preds > 0.5))

        return {
            "status": "SUCCESS",
            "model_name": "PyTorch Transaction LSTM",
            "sequence_length": self.sequence_length,
            "total_sequences_evaluated": len(final_preds),
            "final_train_loss": round(losses[-1], 4),
            "high_risk_sequences_detected": high_risk_sequences,
            "avg_sequence_fraud_prob": round(float(np.mean(final_preds)), 4),
            "sample_sequence_predictions": [round(float(p), 4) for p in final_preds[:5]]
        }
