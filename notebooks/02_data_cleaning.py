import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. FOLDER PATHS
# --------------------------------------------------

RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")

# Processed folder create karo agar exist nahi karta
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. DATASET FILES
# --------------------------------------------------

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


# --------------------------------------------------
# 3. LOAD + BASIC CLEANING
# --------------------------------------------------

for name, filename in datasets.items():

    print("\n" + "=" * 70)
    print(f"CLEANING: {name.upper()}")
    print("=" * 70)

    # Load raw dataset
    df = pd.read_csv(RAW_PATH / filename)

    print(f"Original shape: {df.shape}")

    # --------------------------------------------------
    # Remove exact duplicate rows
    # --------------------------------------------------

    duplicate_count = df.duplicated().sum()

    print(f"Duplicate rows found: {duplicate_count}")

    if duplicate_count > 0:
        df = df.drop_duplicates()

    # --------------------------------------------------
    # Clean column names
    # --------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # --------------------------------------------------
    # Remove leading/trailing spaces from text columns
    # --------------------------------------------------

    text_columns = df.select_dtypes(include="object").columns

    for column in text_columns:
        df[column] = df[column].str.strip()

    # --------------------------------------------------
    # Save cleaned dataset
    # --------------------------------------------------

    output_file = PROCESSED_PATH / filename

    df.to_csv(output_file, index=False)

    print(f"Cleaned shape: {df.shape}")
    print(f"Saved to: {output_file}")