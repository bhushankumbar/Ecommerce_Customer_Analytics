import pandas as pd
from pathlib import Path


# Path to the processed datasets
DATA_PATH = Path("data/processed")


# Load datasets
customers = pd.read_csv(DATA_PATH / "customers.csv")
orders = pd.read_csv(DATA_PATH / "orders.csv")
order_items = pd.read_csv(DATA_PATH / "order_items.csv")
payments = pd.read_csv(DATA_PATH / "payments.csv")
reviews = pd.read_csv(DATA_PATH / "reviews.csv")
products = pd.read_csv(DATA_PATH / "products.csv")


# Convert date columns to datetime
order_date_columns = [
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

orders[order_date_columns] = orders[order_date_columns].apply(
    pd.to_datetime,
    errors="coerce"
)


# ---------------------------------------------------------
# 1. Dataset overview
# ---------------------------------------------------------

datasets = {
    "customers": customers,
    "orders": orders,
    "order_items": order_items,
    "payments": payments,
    "reviews": reviews,
    "products": products,
}

print("Dataset sizes:")

for name, df in datasets.items():
    print(f"{name}: {df.shape}")


# ---------------------------------------------------------
# 2. Order status analysis
# ---------------------------------------------------------

print("\nOrder status distribution:")
print(orders["order_status"].value_counts())


# ---------------------------------------------------------
# 3. Review score analysis
# ---------------------------------------------------------

print("\nReview score distribution:")
print(reviews["review_score"].value_counts().sort_index())


# ---------------------------------------------------------
# 4. Product category analysis
# ---------------------------------------------------------

print("\nTop 10 product categories:")
print(
    products["product_category_name"]
    .value_counts()
    .head(10)
)


# ---------------------------------------------------------
# 5. Order date range
# ---------------------------------------------------------

print("\nOrder date range:")
print("First order:", orders["order_purchase_timestamp"].min())
print("Last order:", orders["order_purchase_timestamp"].max())


# ---------------------------------------------------------
# 6. Basic business metrics
# ---------------------------------------------------------

total_orders = orders["order_id"].nunique()
total_customers = customers["customer_unique_id"].nunique()
total_order_items = len(order_items)
total_revenue = order_items["price"].sum()

print("\nBasic business metrics:")
print("Total orders:", total_orders)
print("Total customers:", total_customers)
print("Total order items:", total_order_items)
print("Total product revenue:", round(total_revenue, 2))


# ---------------------------------------------------------
# 7. Monthly order trends
# ---------------------------------------------------------

orders["order_month"] = (
    orders["order_purchase_timestamp"]
    .dt.to_period("M")
)

monthly_orders = orders.groupby("order_month").size()

print("\nMonthly order counts:")
print(monthly_orders)


# ---------------------------------------------------------
# 8. Monthly revenue trends
# ---------------------------------------------------------

order_items["order_purchase_timestamp"] = pd.to_datetime(
    order_items["order_id"].map(
        orders.set_index("order_id")["order_purchase_timestamp"]
    ),
    errors="coerce"
)

order_items["order_month"] = (
    order_items["order_purchase_timestamp"]
    .dt.to_period("M")
)

monthly_revenue = order_items.groupby("order_month")["price"].sum()

print("\nMonthly revenue:")
print(monthly_revenue)