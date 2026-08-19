import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Define paths
# ---------------------------------------------------------

DATA_PATH = Path("data/processed")


# ---------------------------------------------------------
# 2. Load analysis datasets
# ---------------------------------------------------------

customer_behaviour = pd.read_csv(
    DATA_PATH / "customer_behaviour.csv"
)

rfm = pd.read_csv(
    DATA_PATH / "rfm_segmentation.csv"
)

clv = pd.read_csv(
    DATA_PATH / "customer_lifetime_value.csv"
)

churn = pd.read_csv(
    DATA_PATH / "customer_churn_analysis.csv"
)


# ---------------------------------------------------------
# 3. Select useful customer-level columns
# ---------------------------------------------------------

customer_data = customer_behaviour[
    [
        "customer_unique_id",
        "order_count",
        "total_spending",
        "average_order_value",
        "first_purchase",
        "last_purchase",
        "customer_type"
    ]
].copy()


# ---------------------------------------------------------
# 4. Add RFM segment
# ---------------------------------------------------------

rfm_data = rfm[
    [
        "customer_unique_id",
        "recency",
        "frequency",
        "monetary",
        "R_score",
        "F_score",
        "M_score",
        "RFM_score",
        "segment"
    ]
].copy()


customer_data = customer_data.merge(
    rfm_data,
    on="customer_unique_id",
    how="left"
)


# ---------------------------------------------------------
# 5. Add CLV
# ---------------------------------------------------------

# Detect the CLV column automatically
clv_columns = [
    column
    for column in clv.columns
    if "clv" in column.lower()
]

if clv_columns:
    clv_column = clv_columns[0]

    customer_data = customer_data.merge(
        clv[
            [
                "customer_unique_id",
                clv_column
            ]
        ],
        on="customer_unique_id",
        how="left"
    )

    customer_data = customer_data.rename(
        columns={
            clv_column: "estimated_clv"
        }
    )


# ---------------------------------------------------------
# 6. Add churn status
# ---------------------------------------------------------

customer_data = customer_data.merge(
    churn[
        [
            "customer_unique_id",
            "days_since_last_purchase",
            "churn_status"
        ]
    ],
    on="customer_unique_id",
    how="left"
)


# ---------------------------------------------------------
# 7. Save Power BI customer dataset
# ---------------------------------------------------------

output_path = (
    DATA_PATH / "powerbi_customer_dataset.csv"
)

customer_data.to_csv(
    output_path,
    index=False
)


# ---------------------------------------------------------
# 8. Verification
# ---------------------------------------------------------

print("Power BI customer dataset created successfully.")

print("\nDataset shape:")
print(customer_data.shape)

print("\nColumns:")
print(list(customer_data.columns))

print("\nChurn status distribution:")
print(
    customer_data["churn_status"]
    .value_counts()
)

print("\nRFM segment distribution:")
print(
    customer_data["segment"]
    .value_counts()
)

print(
    f"\nPower BI dataset saved to: {output_path}"
)