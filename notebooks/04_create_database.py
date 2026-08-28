import pandas as pd
import sqlite3
from pathlib import Path


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_ROOT / "data" / "raw"
DATABASE_PATH = PROJECT_ROOT / "database" / "customer_intelligence.db"


# --------------------------------------------------
# CREATE DATABASE FOLDER
# --------------------------------------------------

DATABASE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# CONNECT TO SQLITE DATABASE
# --------------------------------------------------

connection = sqlite3.connect(DATABASE_PATH)

print("=" * 70)
print("ENTERPRISE CUSTOMER INTELLIGENCE DATABASE")
print("=" * 70)

print(f"\nDatabase created at:")
print(DATABASE_PATH)


# --------------------------------------------------
# DATASETS TO LOAD
# --------------------------------------------------

datasets = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}


# --------------------------------------------------
# LOAD CSV → SQLITE TABLES
# --------------------------------------------------

for table_name, filename in datasets.items():

    file_path = DATA_PATH / filename

    df = pd.read_csv(file_path)

    df.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False
    )

    print(
        f"\nLoaded: {table_name}"
        f" | Rows: {df.shape[0]}"
        f" | Columns: {df.shape[1]}"
    )


# --------------------------------------------------
# VERIFY TABLES
# --------------------------------------------------

tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name;
    """,
    connection
)

print("\n" + "=" * 70)
print("TABLES CREATED")
print("=" * 70)

print(tables)


# --------------------------------------------------
# CLOSE DATABASE
# --------------------------------------------------

connection.close()

print("\nDatabase setup completed successfully.")