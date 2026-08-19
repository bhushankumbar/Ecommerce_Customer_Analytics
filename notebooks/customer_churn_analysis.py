import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Define paths
# ---------------------------------------------------------

DATA_PATH = Path("data/processed")


# ---------------------------------------------------------
# 2. Load customer behaviour and RFM data
# ---------------------------------------------------------

customer_behaviour = pd.read_csv(
    DATA_PATH / "customer_behaviour.csv"
)

rfm = pd.read_csv(
    DATA_PATH / "rfm_segmentation.csv"
)


# ---------------------------------------------------------
# 3. Convert purchase dates
# ---------------------------------------------------------

customer_behaviour["last_purchase"] = pd.to_datetime(
    customer_behaviour["last_purchase"],
    errors="coerce"
)


# ---------------------------------------------------------
# 4. Define analysis date
# ---------------------------------------------------------

analysis_date = customer_behaviour["last_purchase"].max()


# ---------------------------------------------------------
# 5. Calculate days since last purchase
# ---------------------------------------------------------

churn = customer_behaviour[
    [
        "customer_unique_id",
        "order_count",
        "total_spending",
        "first_purchase",
        "last_purchase",
        "customer_type"
    ]
].copy()

churn["days_since_last_purchase"] = (
    analysis_date - churn["last_purchase"]
).dt.days


# ---------------------------------------------------------
# 6. Define churn status
# ---------------------------------------------------------
#
# Customers with no purchase for 180+ days are considered
# churned for this analysis.
#
# Customers inactive for 90-179 days are considered
# at risk of churn.
#
# Customers active within the last 90 days are considered
# active.
# ---------------------------------------------------------

def classify_customer(days):

    if days >= 180:
        return "Churned"

    elif days >= 90:
        return "At Risk"

    else:
        return "Active"


churn["churn_status"] = (
    churn["days_since_last_purchase"]
    .apply(classify_customer)
)


# ---------------------------------------------------------
# 7. Add RFM segment
# ---------------------------------------------------------

churn = churn.merge(
    rfm[
        [
            "customer_unique_id",
            "segment"
        ]
    ],
    on="customer_unique_id",
    how="left"
)


# ---------------------------------------------------------
# 8. Calculate churn distribution
# ---------------------------------------------------------

status_distribution = (
    churn["churn_status"]
    .value_counts()
)


print("\nCustomer churn distribution:")
print(status_distribution)


# ---------------------------------------------------------
# 9. Calculate churn percentages
# ---------------------------------------------------------

status_percentage = (
    churn["churn_status"]
    .value_counts(normalize=True)
    * 100
)


print("\nCustomer churn percentage:")
print(status_percentage.round(2))


# ---------------------------------------------------------
# 10. Calculate overall churn rate
# ---------------------------------------------------------

churn_rate = (
    (
        churn["churn_status"] == "Churned"
    ).mean()
    * 100
)


print(
    "\nOverall churn rate:",
    round(churn_rate, 2),
    "%"
)


# ---------------------------------------------------------
# 11. Revenue associated with churn status
# ---------------------------------------------------------

print("\nRevenue by churn status:")

revenue_by_status = (
    churn
    .groupby("churn_status")["total_spending"]
    .agg(
        ["count", "sum", "mean"]
    )
    .sort_values(
        "sum",
        ascending=False
    )
)

print(
    revenue_by_status.round(2)
)


# ---------------------------------------------------------
# 12. Churn by customer segment
# ---------------------------------------------------------

print("\nChurn distribution by customer segment:")

segment_churn = pd.crosstab(
    churn["segment"],
    churn["churn_status"],
    normalize="index"
) * 100

print(
    segment_churn.round(2)
)


# ---------------------------------------------------------
# 13. Highest-value churned customers
# ---------------------------------------------------------

print(
    "\nTop 10 churned customers by spending:"
)

top_churned = (
    churn[
        churn["churn_status"] == "Churned"
    ]
    [
        [
            "customer_unique_id",
            "order_count",
            "total_spending",
            "days_since_last_purchase",
            "segment"
        ]
    ]
    .sort_values(
        "total_spending",
        ascending=False
    )
    .head(10)
)

print(top_churned)


# ---------------------------------------------------------
# 14. Save churn analysis
# ---------------------------------------------------------

output_path = (
    DATA_PATH / "customer_churn_analysis.csv"
)

churn.to_csv(
    output_path,
    index=False
)


print(
    f"\nCustomer churn analysis saved to: "
    f"{output_path}"
)