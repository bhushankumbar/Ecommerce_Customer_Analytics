import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Define input and output paths
# ---------------------------------------------------------

RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")

# Create the processed-data folder if it does not exist.
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# 2. Load raw datasets
# ---------------------------------------------------------

customers = pd.read_csv(RAW_PATH / "olist_customers_dataset.csv")
orders = pd.read_csv(RAW_PATH / "olist_orders_dataset.csv")
order_items = pd.read_csv(RAW_PATH / "olist_order_items_dataset.csv")
payments = pd.read_csv(RAW_PATH / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(RAW_PATH / "olist_order_reviews_dataset.csv")
products = pd.read_csv(RAW_PATH / "olist_products_dataset.csv")
sellers = pd.read_csv(RAW_PATH / "olist_sellers_dataset.csv")
geolocation = pd.read_csv(RAW_PATH / "olist_geolocation_dataset.csv")
category_translation = pd.read_csv(
    RAW_PATH / "product_category_name_translation.csv"
)


# ---------------------------------------------------------
# 3. Convert date columns to datetime
# ---------------------------------------------------------

order_date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

orders[order_date_columns] = orders[order_date_columns].apply(
    pd.to_datetime,
    errors="coerce"
)

order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"],
    errors="coerce"
)

review_date_columns = [
    "review_creation_date",
    "review_answer_timestamp",
]

reviews[review_date_columns] = reviews[review_date_columns].apply(
    pd.to_datetime,
    errors="coerce"
)


# ---------------------------------------------------------
# 4. Store datasets in a dictionary
# ---------------------------------------------------------

datasets = {
    "customers": customers,
    "orders": orders,
    "order_items": order_items,
    "payments": payments,
    "reviews": reviews,
    "products": products,
    "sellers": sellers,
    "geolocation": geolocation,
    "category_translation": category_translation,
}


# ---------------------------------------------------------
# 5. Missing-value decisions
# ---------------------------------------------------------

# Missing order dates are preserved because they represent
# different stages of the order lifecycle.
#
# Missing review comments are preserved because customers
# can provide a rating without writing a comment.
#
# Missing product information is preserved because the
# correct values cannot be reliably inferred from the data.
#
# No artificial values are inserted into these fields.


# ---------------------------------------------------------
# 6. Duplicate-row decisions
# ---------------------------------------------------------

# No duplicate rows were found in the main datasets.
#
# Geolocation contains duplicate rows. These are retained
# because multiple geographic records can exist for the
# same ZIP-code prefix.


# ---------------------------------------------------------
# 7. Save processed datasets
# ---------------------------------------------------------

for name, df in datasets.items():
    output_file = PROCESSED_PATH / f"{name}.csv"
    df.to_csv(output_file, index=False)


# ---------------------------------------------------------
# 8. Verification
# ---------------------------------------------------------

print("Data cleaning completed successfully.")
print(f"Processed datasets saved to: {PROCESSED_PATH}")

print("\nSaved datasets:")

for name in datasets:
    print(f"- {name}.csv")