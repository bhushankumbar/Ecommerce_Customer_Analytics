import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed")
OUTPUT_PATH = DATA_PATH / "retention_cohort_analysis.csv"

# 1. Load ORDERS (one row per order) and customers
orders = pd.read_csv(DATA_PATH / "orders.csv")
customers = pd.read_csv(DATA_PATH / "customers.csv")

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"], errors="coerce"
)

# 2. Attach the real person to every order
df = orders.merge(
    customers[["customer_id", "customer_unique_id"]],
    on="customer_id", how="left"
).dropna(subset=["order_purchase_timestamp"])

# 3. Month of EVERY order, and month of each person's FIRST order (cohort)
df["order_month"] = df["order_purchase_timestamp"].dt.to_period("M")
first_order = df.groupby("customer_unique_id")["order_purchase_timestamp"].transform("min")
df["cohort_month"] = first_order.dt.to_period("M")

# 4. Months since the first order (1 = first month)
df["cohort_index"] = (
    (df["order_month"].dt.year - df["cohort_month"].dt.year) * 12
    + (df["order_month"].dt.month - df["cohort_month"].dt.month)
    + 1
)

# 5. Unique customers who ordered in each (cohort, month)
cohort_data = (
    df.groupby(["cohort_month", "cohort_index"])["customer_unique_id"]
    .nunique().reset_index(name="customer_count")
)

# 6. True cohort size = everyone whose first order was that month
cohort_sizes = (
    cohort_data[cohort_data["cohort_index"] == 1][["cohort_month", "customer_count"]]
    .rename(columns={"customer_count": "cohort_size"})
)

cohort_data = cohort_data.merge(cohort_sizes, on="cohort_month", how="left")
cohort_data["retention_rate"] = cohort_data["customer_count"] / cohort_data["cohort_size"]

cohort_data["cohort_month"] = cohort_data["cohort_month"].astype(str)
cohort_data = cohort_data[
    ["cohort_month", "cohort_index", "customer_count", "retention_rate"]
].sort_values(["cohort_month", "cohort_index"])

print(cohort_data)
cohort_data.to_csv(OUTPUT_PATH, index=False)