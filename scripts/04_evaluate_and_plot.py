"""Evaluation plots: predicted vs actual, residuals, feature importance."""
import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/traffic_clean.csv", parse_dates=["date_time"])
feature_cols = joblib.load("models/feature_columns.pkl")
model = joblib.load("models/best_model.pkl")

split_idx = int(len(df) * 0.8)
test_df = df.iloc[split_idx:].copy()
X_test = test_df[feature_cols]
y_test = test_df["traffic_volume"]
preds = model.predict(X_test)
test_df["predicted"] = preds

fig, axes = plt.subplots(2, 2, figsize=(13, 9))

# Predicted vs actual scatter
axes[0,0].scatter(y_test, preds, alpha=0.15, s=8)
axes[0,0].plot([0, y_test.max()], [0, y_test.max()], 'r--')
axes[0,0].set_xlabel("Actual"); axes[0,0].set_ylabel("Predicted")
axes[0,0].set_title("Predicted vs Actual Traffic Volume")

# Residuals
residuals = y_test - preds
axes[0,1].hist(residuals, bins=50)
axes[0,1].set_title("Residual Distribution")
axes[0,1].axvline(0, color='r', linestyle='--')

# Time series slice (one week) actual vs predicted
week_slice = test_df.iloc[:168]
axes[1,0].plot(week_slice["date_time"], week_slice["traffic_volume"], label="Actual")
axes[1,0].plot(week_slice["date_time"], week_slice["predicted"], label="Predicted", alpha=0.8)
axes[1,0].set_title("One Week: Actual vs Predicted")
axes[1,0].legend()
axes[1,0].tick_params(axis='x', rotation=45)

# Feature importance
importances = pd.read_csv("models/feature_importances.csv", index_col=0).iloc[:, 0]
axes[1,1].barh(importances.head(8).index[::-1], importances.head(8).values[::-1])
axes[1,1].set_title("Top 8 Feature Importances (Random Forest)")

plt.tight_layout()
plt.savefig("figures/model_evaluation.png", dpi=120)
print("Saved figures/model_evaluation.png")
