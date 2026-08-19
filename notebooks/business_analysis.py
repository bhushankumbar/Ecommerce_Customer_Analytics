import pandas as pd
from pathlib import Path


# Path to processed datasets
DATA_PATH = Path("data/processed")


# Load datasets
customers = pd.read_csv(DATA_PATH / "customers.csv")
orders = pd.read_csv(DATA_PATH / "orders.csv")
order_items = pd.read_csv(DATA_PATH / "order_items.csv")
payments = pd.read_csv(DATA_PATH / "payments.csv")
reviews = pd.read_csv(DATA_PATH / "reviews.csv")


# Convert relevant date columns to datetime
date_columns = [
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

orders[date_columns] = orders[date_columns].apply(
    pd.to_datetime,
    errors="coerce"
)


# ---------------------------------------------------------
# 1. Monthly revenue
# ---------------------------------------------------------

orders["order_month"] = (
    orders["order_purchase_timestamp"]
    .dt.to_period("M")
)

order_items = order_items.merge(
    orders[["order_id", "order_month"]],
    on="order_id",
    how="left"
)

monthly_revenue = (
    order_items
    .groupby("order_month")["price"]
    .sum()
    .sort_index()
)

print("\nMonthly revenue:")
print(monthly_revenue)


# ---------------------------------------------------------
# 2. Top products by revenue
# ---------------------------------------------------------

product_revenue = (
    order_items
    .groupby("product_id")["price"]
    .sum()
    .sort_values(ascending=False)
)

print("\nTop 10 products by revenue:")
print(product_revenue.head(10))


# ---------------------------------------------------------
# 3. Payment method usage
# ---------------------------------------------------------

payment_methods = payments["payment_type"].value_counts()

print("\nPayment method usage:")
print(payment_methods)


# ---------------------------------------------------------
# 4. Average order value
# ---------------------------------------------------------

order_revenue = (
    order_items
    .groupby("order_id")["price"]
    .sum()
)

average_order_value = order_revenue.mean()

print("\nAverage order value:")
print(round(average_order_value, 2))


# ---------------------------------------------------------
# 5. Average review score
# ---------------------------------------------------------

average_review_score = reviews["review_score"].mean()

print("\nAverage review score:")
print(round(average_review_score, 2))


# ---------------------------------------------------------
# 6. Repeat customer analysis
# ---------------------------------------------------------

orders_with_customer = orders.merge(
    customers[["customer_id", "customer_unique_id"]],
    on="customer_id",
    how="left"
)

customer_orders = (
    orders_with_customer
    .groupby("customer_unique_id")["order_id"]
    .nunique()
)

repeat_customers = (customer_orders > 1).sum()
total_unique_customers = customer_orders.count()

repeat_customer_rate = (
    repeat_customers / total_unique_customers
) * 100

print("\nCustomer analysis:")
print("Total unique customers:", total_unique_customers)
print("Repeat customers:", repeat_customers)
print("Repeat customer rate:", round(repeat_customer_rate, 2), "%")


# ---------------------------------------------------------
# 7. Delivery performance
# ---------------------------------------------------------

delivered_orders = orders.dropna(
    subset=[
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
).copy()

delivered_orders["delivery_days"] = (
    delivered_orders["order_delivered_customer_date"]
    - delivered_orders["order_purchase_timestamp"]
).dt.total_seconds() / 86400

delivered_orders["delivery_delay_days"] = (
    delivered_orders["order_delivered_customer_date"]
    - delivered_orders["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

average_delivery_days = delivered_orders["delivery_days"].mean()

late_orders = (
    delivered_orders["delivery_delay_days"] > 0
).sum()

total_delivered_orders = len(delivered_orders)

late_delivery_rate = (
    late_orders / total_delivered_orders
) * 100

print("\nDelivery performance:")
print("Average delivery time:", round(average_delivery_days, 2), "days")
print("Delivered orders analyzed:", total_delivered_orders)
print("Late deliveries:", late_orders)
print("Late delivery rate:", round(late_delivery_rate, 2), "%")


# ---------------------------------------------------------
# 8. Customer purchase frequency
# ---------------------------------------------------------

purchase_frequency = (
    customer_orders
    .value_counts()
    .sort_index()
)

print("\nCustomer purchase frequency:")
print(purchase_frequency.head(10))


# ---------------------------------------------------------
# 9. Customers by number of orders
# ---------------------------------------------------------

one_time_customers = (customer_orders == 1).sum()
two_time_customers = (customer_orders == 2).sum()
three_or_more_customers = (customer_orders >= 3).sum()

print("\nCustomer purchase behavior:")
print("One-time customers:", one_time_customers)
print("Customers with 2 orders:", two_time_customers)
print("Customers with 3+ orders:", three_or_more_customers)