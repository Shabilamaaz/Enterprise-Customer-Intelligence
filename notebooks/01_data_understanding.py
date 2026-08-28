import pandas as pd
from pathlib import Path

# Raw data folder
DATA_PATH = Path("data/raw")

# Saare datasets ke file names
datasets = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}

print("=" * 70)
print("ENTERPRISE CUSTOMER INTELLIGENCE - DATA PROFILING")
print("=" * 70)

for name, filename in datasets.items():

    print(f"\n{'-' * 70}")
    print(f"DATASET: {name.upper()}")
    print(f"{'-' * 70}")

    # Load dataset
    df = pd.read_csv(DATA_PATH / filename)

    # Basic information
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nMissing Values:")
    print(df.isnull().sum().to_dict())

    print(f"\nDuplicate Rows: {df.duplicated().sum()}")

    print("\nData Types:")
    print(df.dtypes.to_dict())