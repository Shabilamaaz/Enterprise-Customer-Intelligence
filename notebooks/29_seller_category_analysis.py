import os
import sqlite3
import pandas as pd


# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "customer_intelligence.db")

print("Database path:")
print(DB_PATH)

# Connect to database
connection = sqlite3.connect(DB_PATH)

print("\nDatabase exists:")
print(os.path.exists(DB_PATH))


# Seller Category Analysis
seller_category = pd.read_sql_query(
    """
    SELECT
        oi.seller_id,
        p.product_category_name,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        SUM(oi.price) AS total_sales,
        ROUND(AVG(oi.price), 2) AS average_order_value
    FROM order_items oi
    JOIN products p
        ON oi.product_id = p.product_id
    GROUP BY
        oi.seller_id,
        p.product_category_name
    ORDER BY total_sales DESC
    """,
    connection
)

print("\nSeller Category Performance:")
print(seller_category.head(10))


# Top Categories by Sales
top_categories = (
    seller_category
    .groupby("product_category_name")["total_sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\nTop Categories by Sales:")
print(top_categories)


# Average Sales per Category
average_category_sales = (
    seller_category
    .groupby("product_category_name")["total_sales"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

print("\nAverage Seller Sales by Category:")
print(average_category_sales.round(2))


# Total Orders by Category
category_orders = (
    seller_category
    .groupby("product_category_name")["total_orders"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\nTop Categories by Number of Orders:")
print(category_orders)


# Close connection
connection.close()

print("\nStep 29 Seller Category Analysis completed successfully.")