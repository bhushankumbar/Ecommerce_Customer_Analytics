import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Paths
# ---------------------------------------------------------

DATA_PATH = Path("data/processed")
OUTPUT_PATH = DATA_PATH / "retention_cohort_analysis.csv"


# ---------------------------------------------------------
# 2. Load customer behaviour data
# ---------------------------------------------------------

df = pd.read_csv(
    DATA_PATH / "customer_behaviour.csv"
)

df["first_purchase"] = pd.to_datetime(
    df["first_purchase"],
    errors="coerce"
)

df["last_purchase"] = pd.to_datetime(
    df["last_purchase"],
    errors="coerce"
)


# ---------------------------------------------------------
# 3. Create purchase month
# ---------------------------------------------------------

df["purchase_month"] = (
    df["last_purchase"]
    .dt.to_period("M")
)


# ---------------------------------------------------------
# 4. Create customer cohort month
# ---------------------------------------------------------

df["cohort_month"] = (
    df["first_purchase"]
    .dt.to_period("M")
)


# ---------------------------------------------------------
# 5. Calculate cohort index
# ---------------------------------------------------------

df["cohort_index"] = (
    (df["purchase_month"].dt.year - df["cohort_month"].dt.year) * 12
    + (df["purchase_month"].dt.month - df["cohort_month"].dt.month)
    + 1
)


# ---------------------------------------------------------
# 6. Count customers by cohort and month
# ---------------------------------------------------------

cohort_data = (
    df.groupby(
        ["cohort_month", "cohort_index"]
    )["customer_unique_id"]
    .nunique()
    .reset_index(name="customer_count")
)


# ---------------------------------------------------------
# 7. Calculate original cohort size
# ---------------------------------------------------------

cohort_sizes = (
    cohort_data[
        cohort_data["cohort_index"] == 1
    ][
        ["cohort_month", "customer_count"]
    ]
    .rename(
        columns={
            "customer_count": "cohort_size"
        }
    )
)


# ---------------------------------------------------------
# 8. Calculate retention rate
# ---------------------------------------------------------

cohort_data = cohort_data.merge(
    cohort_sizes,
    on="cohort_month",
    how="left"
)

# Store retention as a decimal:
# 1.00 = 100%
# 0.50 = 50%
# 0.10 = 10%

cohort_data["retention_rate"] = (
    cohort_data["customer_count"]
    / cohort_data["cohort_size"]
)


# ---------------------------------------------------------
# 9. Clean output
# ---------------------------------------------------------

cohort_data["cohort_month"] = (
    cohort_data["cohort_month"]
    .astype(str)
)

cohort_data = cohort_data[
    [
        "cohort_month",
        "cohort_index",
        "customer_count",
        "retention_rate"
    ]
].sort_values(
    ["cohort_month", "cohort_index"]
)


# ---------------------------------------------------------
# 10. Display sample
# ---------------------------------------------------------

print("\nSample:")
print(cohort_data.head(10))


# ---------------------------------------------------------
# 11. Save retention analysis
# ---------------------------------------------------------

cohort_data.to_csv(
    OUTPUT_PATH,
    index=False
)

print(
    f"\nRetention analysis saved to: {OUTPUT_PATH}"
)