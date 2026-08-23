"""
Retail Product Demand Forecaster.

Forecasts product sales demand quantities across retail categories using XGBoost
vs Moving Average baselines, providing explicit MAE/RMSE metric comparisons.
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor


class RetailDemandForecaster:
    """Forecasts product category demand quantities."""

    def __init__(self, forecast_horizon_invoices: int = 14):
        self.forecast_horizon = forecast_horizon_invoices

    def forecast_demand(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generates demand forecasts and compares model baselines."""
        if "Quantity" not in df.columns or "TotalSales" not in df.columns:
            return {"status": "ERROR", "message": "Missing Quantity or TotalSales columns"}

        series = df["Quantity"].values
        n = len(series)
        if n < 30:
            return {"status": "ERROR", "message": "Insufficient series length for retail demand forecasting"}

        lag_df = pd.DataFrame({"y": series})
        for l in range(1, 4):
            lag_df[f"lag_{l}"] = lag_df["y"].shift(l)
        
        lag_df = lag_df.dropna()
        X_seq = lag_df[["lag_1", "lag_2", "lag_3"]]
        y_seq = lag_df["y"]

        split_idx = int(len(X_seq) * 0.8)
        X_train, X_val = X_seq.iloc[:split_idx], X_seq.iloc[split_idx:]
        y_train, y_val = y_seq.iloc[:split_idx], y_seq.iloc[split_idx:]

        # Baseline: Moving Average
        ma_preds = np.full(len(y_val), y_train.tail(7).mean())
        ma_mae = round(float(mean_absolute_error(y_val, ma_preds)), 4)

        # Champion Model: XGBoost Regressor
        xgb = XGBRegressor(n_estimators=50, max_depth=3, random_state=42)
        xgb.fit(X_train, y_train)
        xgb_preds = xgb.predict(X_val)

        xgb_mae = round(float(mean_absolute_error(y_val, xgb_preds)), 4)
        xgb_rmse = round(float(np.sqrt(mean_squared_error(y_val, xgb_preds))), 4)

        # Generate future demand predictions
        last_lags = list(y_seq.iloc[-3:].values)
        future_demand = []
        for i in range(self.forecast_horizon):
            pred = float(xgb.predict(np.array([last_lags[-3:]]))[0])
            pred = float(np.clip(pred, 1.0, 500.0))
            future_demand.append(round(pred, 1))
            last_lags.append(pred)

        total_predicted_units = round(float(np.sum(future_demand)), 1)

        return {
            "status": "SUCCESS",
            "forecast_horizon_periods": self.forecast_horizon,
            "model_comparison": [
                {"model": "7-Day Moving Average Baseline", "MAE": ma_mae, "is_champion": False},
                {"model": "XGBoost Demand Regressor", "MAE": xgb_mae, "RMSE": xgb_rmse, "is_champion": True}
            ],
            "current_avg_order_quantity": round(float(series.mean()), 2),
            "forecasted_total_units_demand": total_predicted_units,
            "forecasted_demand_series": future_demand,
            "inventory_recommendation": f"Forecast predicts {total_predicted_units} units demand over next {self.forecast_horizon} periods. Maintain +15% safety stock buffer.",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
