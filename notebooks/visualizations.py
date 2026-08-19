import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

# Processed datasets are used because the data has already
# gone through the cleaning stage.
DATA_PATH = Path("data/processed")

# All generated charts will be saved here so that reports
# and visual outputs are kept separate from the source code.
CHARTS_PATH = Path("Reports/Charts")

# Create the Charts folder automatically if it does not exist.
CHARTS_PATH.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------

orders = pd.read_csv(DATA_PATH / "orders.csv")
order_items = pd.read_csv(DATA_PATH / "order_items.csv")
reviews = pd.read_csv(DATA_PATH / "reviews.csv")


# ---------------------------------------------------------
# Convert date columns
# ---------------------------------------------------------

# Converting these columns to datetime allows us to perform
# date-based calculations and analysis reliably.

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"],
    errors="coerce"
)

orders["order_estimated_delivery_date"] = pd.to_datetime(
    orders["order_estimated_delivery_date"],
    errors="coerce"
)


# ---------------------------------------------------------
# 1. Monthly Revenue Trend
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
)

monthly_revenue.index = monthly_revenue.index.astype(str)

plt.figure(figsize=(12, 6))
plt.plot(monthly_revenue.index, monthly_revenue.values)
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()

# Save the chart for use in the project report.
plt.savefig(CHARTS_PATH / "monthly_revenue_trend.png", dpi=300)

plt.show()
plt.close()


# ---------------------------------------------------------
# 2. Order Status Distribution
# ---------------------------------------------------------

order_status = orders["order_status"].value_counts()

plt.figure(figsize=(10, 6))
order_status.plot(kind="bar")
plt.title("Order Status Distribution")
plt.xlabel("Order Status")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.tight_layout()

# Save the chart for the final project report.
plt.savefig(CHARTS_PATH / "order_status_distribution.png", dpi=300)

plt.show()
plt.close()


# ---------------------------------------------------------
# 3. Review Score Distribution
# ---------------------------------------------------------

review_scores = (
    reviews["review_score"]
    .value_counts()
    .sort_index()
)

plt.figure(figsize=(8, 5))
review_scores.plot(kind="bar")
plt.title("Review Score Distribution")
plt.xlabel("Review Score")
plt.ylabel("Number of Reviews")
plt.xticks(rotation=0)
plt.tight_layout()

# Save the chart for the final project report.
plt.savefig(CHARTS_PATH / "review_score_distribution.png", dpi=300)

plt.show()
plt.close()


# ---------------------------------------------------------
# 4. Delivery Delay Distribution
# ---------------------------------------------------------

delivery_data = orders.dropna(
    subset=[
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
).copy()

delivery_data["delivery_delay_days"] = (
    delivery_data["order_delivered_customer_date"]
    - delivery_data["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

plt.figure(figsize=(10, 6))
plt.hist(delivery_data["delivery_delay_days"], bins=50)
plt.title("Delivery Delay Distribution")
plt.xlabel("Delay Compared With Estimated Delivery (Days)")
plt.ylabel("Number of Orders")
plt.tight_layout()

# Save the chart for the final project report.
plt.savefig(CHARTS_PATH / "delivery_delay_distribution.png", dpi=300)

plt.show()
plt.close()


print("All 4 charts have been saved to Reports/Charts/")