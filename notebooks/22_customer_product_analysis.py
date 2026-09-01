import sqlite3
import pandas as pd
import os

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "customer_intelligence.db")

# Check database exists
print("Database exists:", os.path.exists(DB_PATH))

# Connect to database
connection = sqlite3.connect(DB_PATH)

# Customer Product Analysis
customer_product = pd.read_sql_query(
    """
    SELECT
        o.customer_id,
        oi.product_id,
        p.product_category_name AS product_category,
        COUNT(oi.order_item_id) AS quantity_purchased,
        ROUND(SUM(oi.price), 2) AS total_spent
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    GROUP BY
        o.customer_id,
        oi.product_id,
        p.product_category_name
    """,
    connection
)

# Handle missing categories
customer_product["product_category"] = (
    customer_product["product_category"]
    .fillna("Unknown")
)

# Display results
print("\nCustomer Product Purchase Analysis:")
print(customer_product.head(10))

# Top customers by spending
print("\nTop 10 Customers by Product Spending:")
print(
    customer_product
    .groupby("customer_id")["total_spent"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

# Most purchased categories
print("\nMost Purchased Product Categories:")
print(
    customer_product
    .groupby("product_category")["quantity_purchased"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

# Category spending
print("\nTop Product Categories by Customer Spending:")
print(
    customer_product
    .groupby("product_category")["total_spent"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .round(2)
)

# Average spending per customer
print("\nAverage Customer Spending:")
print(
    customer_product
    .groupby("customer_id")["total_spent"]
    .sum()
    .mean()
    .round(2)
)

# Close connection
connection.close()

print("\nStep 22 Customer Product Analysis completed successfully.")