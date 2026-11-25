import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Define paths
# ---------------------------------------------------------

DATA_PATH = Path("data/processed")


# ---------------------------------------------------------
# 2. Load customer behaviour data
# ---------------------------------------------------------

customer_behaviour = pd.read_csv(
    DATA_PATH / "customer_behaviour.csv"
)


# ---------------------------------------------------------
# 3. Convert date columns
# ---------------------------------------------------------

customer_behaviour["last_purchase"] = pd.to_datetime(
    customer_behaviour["last_purchase"],
    errors="coerce"
)

customer_behaviour["first_purchase"] = pd.to_datetime(
    customer_behaviour["first_purchase"],
    errors="coerce"
)


# ---------------------------------------------------------
# 4. Define analysis date
# ---------------------------------------------------------

analysis_date = customer_behaviour["last_purchase"].max()


# ---------------------------------------------------------
# 5. Calculate RFM metrics
# ---------------------------------------------------------

rfm = customer_behaviour[
    [
        "customer_unique_id",
        "order_count",
        "total_spending",
        "last_purchase",
    ]
].copy()

rfm["recency"] = (
    analysis_date - rfm["last_purchase"]
).dt.days

rfm["frequency"] = rfm["order_count"]

rfm["monetary"] = rfm["total_spending"]


# ---------------------------------------------------------
# 6. Create RFM scores
# ---------------------------------------------------------

rfm["R_score"] = pd.qcut(
    rfm["recency"],
    q=5,
    labels=[5, 4, 3, 2, 1],
    duplicates="drop"
).astype(int)

# Frequency is almost always 1 in this dataset (about 97% of customers
# bought once), so quintiles cannot separate customers. Use fixed bands:
# 1 = one order, 2 = two orders, 3 = three or more orders.
rfm["F_score"] = rfm["frequency"].apply(
    lambda x: 1 if x == 1 else (2 if x == 2 else 3)
)

rfm["M_score"] = pd.qcut(
    rfm["monetary"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5]
).astype(int)


# ---------------------------------------------------------
# 7. Overall RFM score
# ---------------------------------------------------------

rfm["RFM_score"] = (
    rfm["R_score"].astype(str)
    + rfm["F_score"].astype(str)
    + rfm["M_score"].astype(str)
)


# ---------------------------------------------------------
# 8. Customer segmentation
# ---------------------------------------------------------

def assign_segment(row):

    # Repeat buyers (F >= 2) who bought recently and spent a lot
    if (
        row["R_score"] >= 4
        and row["F_score"] >= 2
        and row["M_score"] >= 4
    ):
        return "Champions"

    # Repeat buyers with decent recency and spend
    elif (
        row["R_score"] >= 3
        and row["F_score"] >= 2
        and row["M_score"] >= 3
    ):
        return "Loyal Customers"

    # Recent one-time buyers with decent spend
    elif (
        row["R_score"] >= 4
        and row["F_score"] == 1
        and row["M_score"] >= 3
    ):
        return "Potential Loyalists"

    # Repeat buyers who have gone quiet
    elif (
        row["R_score"] <= 2
        and row["F_score"] >= 2
        and row["M_score"] >= 3
    ):
        return "At Risk"

    # Old, one-time, low-spend buyers
    elif (
        row["R_score"] <= 2
        and row["F_score"] == 1
        and row["M_score"] <= 2
    ):
        return "Lost Customers"

    elif row["R_score"] >= 3:
        return "Promising Customers"

    else:
        return "Needs Attention"

    
rfm["segment"] = rfm.apply(
    assign_segment,
    axis=1
)


# ---------------------------------------------------------
# 9. Display results
# ---------------------------------------------------------

print("\nRFM sample:")
print(rfm.head())

print("\nRFM summary:")
print(
    rfm[
        [
            "recency",
            "frequency",
            "monetary"
        ]
    ].describe()
)

print("\nCustomer segment distribution:")
print(
    rfm["segment"].value_counts()
)


# ---------------------------------------------------------
# 10. Segment revenue analysis
# ---------------------------------------------------------

print("\nRevenue by customer segment:")

segment_revenue = (
    rfm.groupby("segment")["monetary"]
    .agg(["count", "sum", "mean"])
    .sort_values("sum", ascending=False)
)

print(segment_revenue)


# ---------------------------------------------------------
# 11. Save RFM dataset
# ---------------------------------------------------------

output_path = DATA_PATH / "rfm_segmentation.csv"

rfm.to_csv(
    output_path,
    index=False
)

print(
    f"\nRFM segmentation data saved to: {output_path}"
)