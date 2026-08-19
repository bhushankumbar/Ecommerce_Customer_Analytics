import sqlite3
from pathlib import Path


# ---------------------------------------------------------
# 1. Define paths
# ---------------------------------------------------------

DATABASE_PATH = Path("data/ecommerce_analytics.db")
SQL_PATH = Path("SQL/business_analysis.sql")


# ---------------------------------------------------------
# 2. Connect to database
# ---------------------------------------------------------

connection = sqlite3.connect(DATABASE_PATH)


# ---------------------------------------------------------
# 3. Read SQL file
# ---------------------------------------------------------

with open(SQL_PATH, "r", encoding="utf-8") as file:
    sql_script = file.read()


# ---------------------------------------------------------
# 4. Split SQL queries
# ---------------------------------------------------------

queries = [
    query.strip()
    for query in sql_script.split(";")
    if query.strip()
]


# ---------------------------------------------------------
# 5. Execute each query
# ---------------------------------------------------------

print("=" * 70)
print("SQL BUSINESS ANALYSIS")
print("=" * 70)

for number, query in enumerate(queries, start=1):

    try:
        cursor = connection.execute(query)
        results = cursor.fetchall()

        column_names = [
            description[0]
            for description in cursor.description
        ]

        print(f"\n{'-' * 70}")
        print(f"QUERY {number}")
        print(f"{'-' * 70}")

        print("Columns:", column_names)

        for row in results[:20]:
            print(row)

        if len(results) > 20:
            print(
                f"... {len(results) - 20} additional rows not displayed"
            )

    except Exception as error:

        print(f"\nQUERY {number} FAILED")
        print("Error:", error)


# ---------------------------------------------------------
# 6. Close database connection
# ---------------------------------------------------------

connection.close()

print("\n" + "=" * 70)
print("SQL ANALYSIS COMPLETED")
print("=" * 70)