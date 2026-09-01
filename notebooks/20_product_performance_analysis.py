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

# Product Performance Analysis
product_analysis = pd.read_sql_query(
    """
    SELECT
        oi.product_id,
        p.product_category_name AS product_category,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        COUNT(oi.order_item_id) AS total_items_sold,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(AVG(oi.price), 2) AS average_price
    FROM order_items oi
    JOIN products p
        ON oi.product_id = p.product_id
    GROUP BY
        oi.product_id,
        p.product_category_name
    """,
    connection
)

# Handle missing category names
product_analysis["product_category"] = (
    product_analysis["product_category"]
    .fillna("Unknown")
)

# Display results
print("\nProduct Performance Analysis:")
print(product_analysis.head(10))

# Top products by revenue
print("\nTop 10 Products by Revenue:")
print(
    product_analysis
    .sort_values("total_revenue", ascending=False)
    .head(10)
    [
        [
            "product_id",
            "product_category",
            "total_orders",
            "total_items_sold",
            "total_revenue"
        ]
    ]
)

# Top products by quantity sold
print("\nTop 10 Products by Quantity Sold:")
print(
    product_analysis
    .sort_values("total_items_sold", ascending=False)
    .head(10)
    [
        [
            "product_id",
            "product_category",
            "total_items_sold",
            "total_revenue"
        ]
    ]
)

# Category performance
category_performance = (
    product_analysis
    .groupby("product_category")
    .agg(
        total_products=("product_id", "nunique"),
        total_orders=("total_orders", "sum"),
        total_items_sold=("total_items_sold", "sum"),
        total_revenue=("total_revenue", "sum")
    )
    .sort_values("total_revenue", ascending=False)
)

print("\nCategory Performance:")
print(category_performance.head(10))

# Average revenue per product
print("\nAverage Revenue per Product:")
print(
    category_performance
    .assign(
        average_revenue_per_product=(
            category_performance["total_revenue"]
            / category_performance["total_products"]
        )
    )
    ["average_revenue_per_product"]
    .round(2)
    .head(10)
)

# Close connection
connection.close()

print("\nStep 20 Product Performance Analysis completed successfully.")