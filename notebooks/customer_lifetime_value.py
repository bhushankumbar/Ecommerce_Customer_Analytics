import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Define paths
# ---------------------------------------------------------

DATA_PATH = Path("data/processed")


# ---------------------------------------------------------
# 2. Load processed datasets
# ---------------------------------------------------------

customers = pd.read_csv(
    DATA_PATH / "customers.csv"
)

orders = pd.read_csv(
    DATA_PATH / "orders.csv"
)

order_items = pd.read_csv(
    DATA_PATH / "order_items.csv"
)


# ---------------------------------------------------------
# 3. Convert order date
# ---------------------------------------------------------

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)


# ---------------------------------------------------------
# 4. Connect customers to orders
# ---------------------------------------------------------

customer_orders = orders.merge(
    customers[["customer_id", "customer_unique_id"]],
    on="customer_id",
    how="left"
)


# ---------------------------------------------------------
# 5. Connect orders to revenue
# ---------------------------------------------------------

customer_orders = customer_orders.merge(
    order_items[
        ["order_id", "price"]
    ],
    on="order_id",
    how="left"
)


# ---------------------------------------------------------
# 6. Calculate customer-level metrics
# ---------------------------------------------------------

clv = (
    customer_orders
    .groupby("customer_unique_id")
    .agg(
        total_orders=("order_id", "nunique"),
        total_revenue=("price", "sum"),
        first_purchase=("order_purchase_timestamp", "min"),
        last_purchase=("order_purchase_timestamp", "max")
    )
    .reset_index()
)


# ---------------------------------------------------------
# 7. Calculate customer lifetime
# ---------------------------------------------------------

clv["customer_lifetime_days"] = (
    clv["last_purchase"] - clv["first_purchase"]
).dt.days


# ---------------------------------------------------------
# 8. Calculate average order value
# ---------------------------------------------------------

clv["average_order_value"] = (
    clv["total_revenue"]
    / clv["total_orders"]
)


# ---------------------------------------------------------
# 9. Calculate purchase frequency
# ---------------------------------------------------------

total_days = (
    orders["order_purchase_timestamp"].max()
    - orders["order_purchase_timestamp"].min()
).days

total_months = max(total_days / 30.44, 1)

clv["purchase_frequency"] = (
    clv["total_orders"] / total_months
)


# ---------------------------------------------------------
# 10. Estimate customer lifetime
# ---------------------------------------------------------

clv["estimated_lifetime_months"] = (
    clv["customer_lifetime_days"] / 30.44
)

# Customers with only one purchase have a lifetime of
# zero days, so use a minimum estimated lifetime of one month.

clv["estimated_lifetime_months"] = (
    clv["estimated_lifetime_months"]
    .clip(lower=1)
)


# ---------------------------------------------------------
# 11. Calculate estimated CLV
# ---------------------------------------------------------

# Historical CLV: average order value x number of orders
# (the revenue each customer has actually generated).
# The earlier version divided frequency by the dataset's ~25 months,
# which made one-time buyers worth less than what they already paid.
clv["estimated_clv"] = (
    clv["average_order_value"]
    * clv["total_orders"]
)

# ---------------------------------------------------------
# 12. Handle invalid values
# ---------------------------------------------------------

clv["estimated_clv"] = (
    clv["estimated_clv"]
    .replace([float("inf"), -float("inf")], 0)
    .fillna(0)
)


# ---------------------------------------------------------
# 13. Display sample
# ---------------------------------------------------------

print("\nCustomer Lifetime Value sample:")
print(
    clv[
        [
            "customer_unique_id",
            "total_orders",
            "total_revenue",
            "average_order_value",
            "estimated_lifetime_months",
            "estimated_clv"
        ]
    ].head()
)


# ---------------------------------------------------------
# 14. CLV summary
# ---------------------------------------------------------

print("\nCLV summary:")

print(
    clv[
        [
            "total_orders",
            "total_revenue",
            "average_order_value",
            "estimated_lifetime_months",
            "estimated_clv"
        ]
    ].describe()
)


# ---------------------------------------------------------
# 15. Top customers by CLV
# ---------------------------------------------------------

print("\nTop 10 customers by estimated CLV:")

print(
    clv[
        [
            "customer_unique_id",
            "total_orders",
            "total_revenue",
            "estimated_clv"
        ]
    ]
    .sort_values(
        "estimated_clv",
        ascending=False
    )
    .head(10)
)


# ---------------------------------------------------------
# 16. Overall CLV metrics
# ---------------------------------------------------------

print("\nOverall CLV metrics:")

print(
    "Average estimated CLV:",
    round(clv["estimated_clv"].mean(), 2)
)

print(
    "Median estimated CLV:",
    round(clv["estimated_clv"].median(), 2)
)

print(
    "Total estimated customer value:",
    round(clv["estimated_clv"].sum(), 2)
)


# ---------------------------------------------------------
# 17. Save CLV dataset
# ---------------------------------------------------------

output_path = (
    DATA_PATH / "customer_lifetime_value.csv"
)

clv.to_csv(
    output_path,
    index=False
)

print(
    f"\nCustomer Lifetime Value data saved to: "
    f"{output_path}"
)