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

# Category Performance Analysis
category_analysis = pd.read_sql_query(
    """
    SELECT
        p.product_category_name AS product_category,
        COUNT(DISTINCT oi.product_id) AS total_products,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        COUNT(oi.order_item_id) AS total_items_sold,
        ROUND(SUM(oi.price), 2) AS total_revenue,
        ROUND(AVG(oi.price), 2) AS average_product_price
    FROM order_items oi
    JOIN products p
        ON oi.product_id = p.product_id
    GROUP BY p.product_category_name
    """,
    connection
)

# Handle missing category names
category_analysis["product_category"] = (
    category_analysis["product_category"]
    .fillna("Unknown")
)

# Sort by revenue
category_analysis = category_analysis.sort_values(
    "total_revenue",
    ascending=False
)

# Display category analysis
print("\nCategory Performance Analysis:")
print(category_analysis.head(10))

# Top 10 categories by revenue
print("\nTop 10 Categories by Revenue:")
print(
    category_analysis[
        [
            "product_category",
            "total_products",
            "total_orders",
            "total_items_sold",
            "total_revenue"
        ]
    ].head(10)
)

# Top 10 categories by quantity sold
print("\nTop 10 Categories by Quantity Sold:")
print(
    category_analysis
    .sort_values("total_items_sold", ascending=False)
    [
        [
            "product_category",
            "total_items_sold",
            "total_revenue"
        ]
    ]
    .head(10)
)

# Top 10 categories by number of orders
print("\nTop 10 Categories by Orders:")
print(
    category_analysis
    .sort_values("total_orders", ascending=False)
    [
        [
            "product_category",
            "total_orders",
            "total_revenue"
        ]
    ]
    .head(10)
)

# Average revenue per product
category_analysis["average_revenue_per_product"] = (
    category_analysis["total_revenue"]
    / category_analysis["total_products"]
)

print("\nTop Categories by Average Revenue per Product:")
print(
    category_analysis
    .sort_values(
        "average_revenue_per_product",
        ascending=False
    )
    [
        [
            "product_category",
            "total_products",
            "total_revenue",
            "average_revenue_per_product"
        ]
    ]
    .head(10)
    .round(2)
)

# Close connection
connection.close()

print("\nStep 21 Category Performance Analysis completed successfully.")