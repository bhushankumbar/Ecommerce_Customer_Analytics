import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Define paths
# ---------------------------------------------------------

DATA_PATH = Path("data/processed")


# ---------------------------------------------------------
# 2. Load datasets
# ---------------------------------------------------------

customers = pd.read_csv(DATA_PATH / "customers.csv")
orders = pd.read_csv(DATA_PATH / "orders.csv")
order_items = pd.read_csv(DATA_PATH / "order_items.csv")


# ---------------------------------------------------------
# 3. Convert date columns
# ---------------------------------------------------------

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)


# ---------------------------------------------------------
# 4. Create customer-level order data
# ---------------------------------------------------------

customer_orders = orders.merge(
    customers[["customer_id", "customer_unique_id"]],
    on="customer_id",
    how="left"
)


# ---------------------------------------------------------
# 5. Calculate customer spending
# ---------------------------------------------------------

customer_spending = (
    order_items
    .groupby("order_id")["price"]
    .sum()
    .reset_index(name="order_value")
)

customer_orders = customer_orders.merge(
    customer_spending,
    on="order_id",
    how="left"
)


# ---------------------------------------------------------
# 6. Customer behaviour metrics
# ---------------------------------------------------------

customer_behaviour = (
    customer_orders
    .groupby("customer_unique_id")
    .agg(
        order_count=("order_id", "nunique"),
        total_spending=("order_value", "sum"),
        average_order_value=("order_value", "mean"),
        first_purchase=("order_purchase_timestamp", "min"),
        last_purchase=("order_purchase_timestamp", "max")
    )
    .reset_index()
)


# ---------------------------------------------------------
# 7. Repeat vs one-time customers
# ---------------------------------------------------------

customer_behaviour["customer_type"] = customer_behaviour[
    "order_count"
].apply(
    lambda x: "Repeat Customer" if x > 1 else "One-Time Customer"
)


# ---------------------------------------------------------
# 8. Display results
# ---------------------------------------------------------

print("\nCustomer behaviour sample:")
print(customer_behaviour.head())

print("\nCustomer type distribution:")
print(customer_behaviour["customer_type"].value_counts())

print("\nCustomer behaviour summary:")
print(customer_behaviour[
    [
        "order_count",
        "total_spending",
        "average_order_value"
    ]
].describe())


# ---------------------------------------------------------
# 9. Top customers by spending
# ---------------------------------------------------------

print("\nTop 10 customers by spending:")

print(
    customer_behaviour
    .sort_values("total_spending", ascending=False)
    .head(10)
)


# ---------------------------------------------------------
# 10. Save customer-level dataset
# ---------------------------------------------------------

output_path = DATA_PATH / "customer_behaviour.csv"

customer_behaviour.to_csv(
    output_path,
    index=False
)

print(f"\nCustomer behaviour data saved to: {output_path}")