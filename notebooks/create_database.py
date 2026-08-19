import pandas as pd
import sqlite3
from pathlib import Path


# ---------------------------------------------------------
# 1. Define paths
# ---------------------------------------------------------

DATA_PATH = Path("data/processed")
DATABASE_PATH = Path("data/ecommerce_analytics.db")


# ---------------------------------------------------------
# 2. Load processed datasets
# ---------------------------------------------------------

customers = pd.read_csv(DATA_PATH / "customers.csv")
orders = pd.read_csv(DATA_PATH / "orders.csv")
order_items = pd.read_csv(DATA_PATH / "order_items.csv")
payments = pd.read_csv(DATA_PATH / "payments.csv")
reviews = pd.read_csv(DATA_PATH / "reviews.csv")
products = pd.read_csv(DATA_PATH / "products.csv")
sellers = pd.read_csv(DATA_PATH / "sellers.csv")


# ---------------------------------------------------------
# 3. Create SQLite database connection
# ---------------------------------------------------------

connection = sqlite3.connect(DATABASE_PATH)


# ---------------------------------------------------------
# 4. Load datasets into database tables
# ---------------------------------------------------------

customers.to_sql(
    "customers",
    connection,
    if_exists="replace",
    index=False
)

orders.to_sql(
    "orders",
    connection,
    if_exists="replace",
    index=False
)

order_items.to_sql(
    "order_items",
    connection,
    if_exists="replace",
    index=False
)

payments.to_sql(
    "payments",
    connection,
    if_exists="replace",
    index=False
)

reviews.to_sql(
    "reviews",
    connection,
    if_exists="replace",
    index=False
)

products.to_sql(
    "products",
    connection,
    if_exists="replace",
    index=False
)

sellers.to_sql(
    "sellers",
    connection,
    if_exists="replace",
    index=False
)


# ---------------------------------------------------------
# 5. Verify database tables
# ---------------------------------------------------------

tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
    """,
    connection
)

print("\nDatabase tables created:")
print(tables)


# ---------------------------------------------------------
# 6. Verify row counts
# ---------------------------------------------------------

print("\nRow counts:")

for table_name in [
    "customers",
    "orders",
    "order_items",
    "payments",
    "reviews",
    "products",
    "sellers"
]:

    result = pd.read_sql_query(
        f"SELECT COUNT(*) AS row_count FROM {table_name}",
        connection
    )

    print(
        f"{table_name}: "
        f"{result.loc[0, 'row_count']}"
    )


# ---------------------------------------------------------
# 7. Close connection
# ---------------------------------------------------------

connection.close()


print(
    f"\nSQLite database created successfully: "
    f"{DATABASE_PATH}"
)