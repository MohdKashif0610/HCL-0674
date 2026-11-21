"""
Synthetic dataset generator for Project 23: Delivery & Logistics Analysis
Produces 23_delivery_performance.csv with ~1,500 rows, missing values, and
a handful of duplicate Shipment_ID rows.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import random

random.seed(42)
np.random.seed(42)

HERE = Path(__file__).resolve().parent

# ── Parameters ────────────────────────────────────────────────────────────────
N = 1500

partners  = ["BlueDart", "FedEx", "Delhivery", "Ecom Express", "DTDC"]
methods   = ["Standard", "Express", "Same-Day", "Economy"]
statuses  = ["Delivered", "Pending", "Cancelled", "Returned", "Failed"]
cities    = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat",
    "Lucknow", "Kochi", "Chandigarh", "Bhopal", "Nagpur"
]

# ── Build base rows ────────────────────────────────────────────────────────────
shipment_ids  = [f"SHP{str(i).zfill(5)}" for i in range(1, N + 1)]

order_dates   = pd.date_range("2024-01-01", periods=N, freq="10h")

# delivery days depend heavily on method
method_days = {"Standard": (4, 10), "Express": (1, 4),
               "Same-Day": (0, 1),  "Economy": (7, 20)}

methods_col  = np.random.choice(methods, N,
                                p=[0.40, 0.25, 0.10, 0.25])
partners_col = np.random.choice(partners, N)
cities_col   = np.random.choice(cities, N)
status_col   = np.random.choice(
    statuses, N, p=[0.70, 0.12, 0.08, 0.06, 0.04]
)

# build delivery dates
delivery_dates = []
for i in range(N):
    lo, hi = method_days[methods_col[i]]
    days   = np.random.randint(lo, hi + 1)
    delivery_dates.append(order_dates[i] + pd.Timedelta(days=days))

delivery_dates = pd.Series(delivery_dates)

# shipping cost
base_cost = {"Standard": 50, "Express": 150,
             "Same-Day": 300, "Economy": 30}
costs = np.array([
    base_cost[m] + np.random.uniform(-10, 40)
    for m in methods_col
])

# ── Inject missing values ─────────────────────────────────────────────────────
# ~8 % of Delivery_Date missing (makes sense: Pending / Cancelled orders)
dd_missing_idx = np.random.choice(N, size=120, replace=False)
delivery_dates.iloc[dd_missing_idx] = pd.NaT

# ~6 % of Shipping_Cost missing
cost_missing_idx = np.random.choice(N, size=90, replace=False)
costs[cost_missing_idx] = np.nan

# ── Inject duplicate Shipment_IDs ─────────────────────────────────────────────
dup_idx = np.random.choice(N, size=30, replace=False)
dup_ids = [shipment_ids[i] for i in dup_idx]
# replace last 30 rows with duplicated IDs
shipment_ids[-30:] = dup_ids

# ── Assemble DataFrame ────────────────────────────────────────────────────────
df = pd.DataFrame({
    "Shipment_ID"      : shipment_ids,
    "Order_Date"       : order_dates.strftime("%Y-%m-%d"),
    "Delivery_Date"    : [
        d.strftime("%Y-%m-%d") if pd.notna(d) else "" for d in delivery_dates
    ],
    "Delivery_Partner" : partners_col,
    "Shipping_Method"  : methods_col,
    "Shipping_Cost"    : np.round(costs, 2),
    "Order_Status"     : status_col,
    "Customer_City"    : cities_col,
})

# replace empty-string with NaN for Delivery_Date column
df["Delivery_Date"] = df["Delivery_Date"].replace("", np.nan)

out = HERE / "23_delivery_performance.csv"
df.to_csv(out, index=False)
print(f"Dataset saved → {out}  ({len(df)} rows, {df.shape[1]} columns)")
print(df.head(3))
