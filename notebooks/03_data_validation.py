import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed")

orders = pd.read_csv(
    DATA_PATH / "olist_orders_dataset.csv"
)

print("=" * 70)
print("ORDERS DATA VALIDATION")
print("=" * 70)

# 1. Basic information
print("\nShape:")
print(orders.shape)

# 2. Duplicate order IDs
print("\nDuplicate order_id:")
print(orders["order_id"].duplicated().sum())

# 3. Order status distribution
print("\nOrder Status:")
print(orders["order_status"].value_counts())

# 4. Convert date columns
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

# 5. Missing values after date conversion
print("\nMissing Values:")
print(orders[date_columns].isnull().sum())

# 6. Delivery before purchase
invalid_delivery = orders[
    orders["order_delivered_customer_date"]
    < orders["order_purchase_timestamp"]
]

print("\nDelivery before purchase:")
print(len(invalid_delivery))

# 7. Estimated delivery before purchase
invalid_estimate = orders[
    orders["order_estimated_delivery_date"]
    < orders["order_purchase_timestamp"]
]

print("\nEstimated delivery before purchase:")
print(len(invalid_estimate))

print("\nValidation completed.")

# --------------------------------------------------
# ORDER ITEMS VALIDATION
# --------------------------------------------------

order_items = pd.read_csv(
    DATA_PATH / "olist_order_items_dataset.csv"
)

print("\n" + "=" * 70)
print("ORDER ITEMS DATA VALIDATION")
print("=" * 70)

print("\nShape:")
print(order_items.shape)

# Duplicate business key
duplicate_items = order_items.duplicated(
    subset=["order_id", "order_item_id"]
).sum()

print("\nDuplicate order_id + order_item_id:")
print(duplicate_items)

# Price validation
negative_price = (order_items["price"] < 0).sum()
zero_price = (order_items["price"] == 0).sum()

print("\nNegative prices:")
print(negative_price)

print("\nZero prices:")
print(zero_price)

# Freight validation
negative_freight = (
    order_items["freight_value"] < 0
).sum()

print("\nNegative freight values:")
print(negative_freight)

# Missing values
print("\nMissing Values:")
print(order_items.isnull().sum())

print("\nOrder Items validation completed.")

# --------------------------------------------------
# PAYMENTS VALIDATION
# --------------------------------------------------

payments = pd.read_csv(
    DATA_PATH / "olist_order_payments_dataset.csv"
)

print("\n" + "=" * 70)
print("PAYMENTS DATA VALIDATION")
print("=" * 70)

print("\nShape:")
print(payments.shape)

# Duplicate payment records
duplicate_payments = payments.duplicated(
    subset=["order_id", "payment_sequential"]
).sum()

print("\nDuplicate order_id + payment_sequential:")
print(duplicate_payments)

# Payment value validation
negative_payment = (
    payments["payment_value"] < 0
).sum()

zero_payment = (
    payments["payment_value"] == 0
).sum()

print("\nNegative payment values:")
print(negative_payment)

print("\nZero payment values:")
print(zero_payment)

# Payment type distribution
print("\nPayment Types:")
print(payments["payment_type"].value_counts())

# Missing values
print("\nMissing Values:")
print(payments.isnull().sum())

print("\nPayments validation completed.")

# --------------------------------------------------
# REVIEWS VALIDATION
# --------------------------------------------------

reviews = pd.read_csv(
    DATA_PATH / "olist_order_reviews_dataset.csv"
)

print("\n" + "=" * 70)
print("REVIEWS DATA VALIDATION")
print("=" * 70)

print("\nShape:")
print(reviews.shape)

# Duplicate review records
duplicate_reviews = reviews.duplicated(
    subset=["review_id", "order_id"]
).sum()

print("\nDuplicate review_id + order_id:")
print(duplicate_reviews)

# Review score validation
invalid_score = (
    (reviews["review_score"] < 1) |
    (reviews["review_score"] > 5)
).sum()

print("\nInvalid review scores:")
print(invalid_score)

# Review score distribution
print("\nReview Score Distribution:")
print(reviews["review_score"].value_counts().sort_index())

# Missing values
print("\nMissing Values:")
print(reviews.isnull().sum())

print("\nReviews validation completed.")

# --------------------------------------------------
# PRODUCTS VALIDATION
# --------------------------------------------------

products = pd.read_csv(
    DATA_PATH / "olist_products_dataset.csv"
)

print("\n" + "=" * 70)
print("PRODUCTS DATA VALIDATION")
print("=" * 70)

print("\nShape:")
print(products.shape)

# Duplicate product IDs
duplicate_products = products["product_id"].duplicated().sum()

print("\nDuplicate product_id:")
print(duplicate_products)

# Product dimensions validation
dimension_columns = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

print("\nNegative dimension values:")

for column in dimension_columns:
    negative_count = (products[column] < 0).sum()
    print(f"{column}: {negative_count}")

# Missing values
print("\nMissing Values:")
print(products.isnull().sum())

print("\nProducts validation completed.")

# --------------------------------------------------
# CUSTOMERS VALIDATION
# --------------------------------------------------

customers = pd.read_csv(
    DATA_PATH / "olist_customers_dataset.csv"
)

print("\n" + "=" * 70)
print("CUSTOMERS DATA VALIDATION")
print("=" * 70)

print("\nShape:")
print(customers.shape)

# Duplicate customer IDs
duplicate_customer_ids = customers["customer_id"].duplicated().sum()

print("\nDuplicate customer_id:")
print(duplicate_customer_ids)

# Duplicate unique customer IDs
duplicate_unique_ids = customers["customer_unique_id"].duplicated().sum()

print("\nDuplicate customer_unique_id:")
print(duplicate_unique_ids)

# ZIP code validation
negative_zip = (
    customers["customer_zip_code_prefix"] < 0
).sum()

print("\nNegative ZIP code prefixes:")
print(negative_zip)

# Missing values
print("\nMissing Values:")
print(customers.isnull().sum())

print("\nCustomers validation completed.")