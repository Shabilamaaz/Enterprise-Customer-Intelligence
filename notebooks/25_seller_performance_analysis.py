import sqlite3
import pandas as pd
import os

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "customer_intelligence.db"
)

# Check database exists
print("Database exists:", os.path.exists(DB_PATH))

# Connect to database
connection = sqlite3.connect(DB_PATH)

# Seller Performance Analysis
seller_performance = pd.read_sql_query(
    """
    SELECT
        oi.seller_id,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        COUNT(oi.order_item_id) AS total_items,
        ROUND(SUM(oi.price), 2) AS total_sales,
        ROUND(AVG(oi.price), 2) AS average_item_price
    FROM order_items oi
    GROUP BY oi.seller_id
    """,
    connection
)

# Calculate average sales per order
seller_performance["average_sales_per_order"] = (
    seller_performance["total_sales"]
    / seller_performance["total_orders"]
).round(2)

# Rank sellers by total sales
top_sellers_by_sales = (
    seller_performance
    .sort_values(
        "total_sales",
        ascending=False
    )
    .head(10)
)

# Rank sellers by number of orders
top_sellers_by_orders = (
    seller_performance
    .sort_values(
        "total_orders",
        ascending=False
    )
    .head(10)
)

# Rank sellers by average order value
top_sellers_by_average = (
    seller_performance
    .sort_values(
        "average_sales_per_order",
        ascending=False
    )
    .head(10)
)

# Display overall seller statistics
print("\nSeller Performance Analysis:")
print(seller_performance.head(10))

print("\nTotal Sellers:")
print(len(seller_performance))

print("\nTotal Seller Sales:")
print(
    round(
        seller_performance["total_sales"].sum(),
        2
    )
)

# Top sellers by sales
print("\nTop 10 Sellers by Total Sales:")
print(
    top_sellers_by_sales[
        [
            "seller_id",
            "total_orders",
            "total_items",
            "total_sales",
            "average_sales_per_order"
        ]
    ]
)

# Top sellers by orders
print("\nTop 10 Sellers by Number of Orders:")
print(
    top_sellers_by_orders[
        [
            "seller_id",
            "total_orders",
            "total_items",
            "total_sales"
        ]
    ]
)

# Top sellers by average order value
print("\nTop 10 Sellers by Average Sales per Order:")
print(
    top_sellers_by_average[
        [
            "seller_id",
            "total_orders",
            "total_sales",
            "average_sales_per_order"
        ]
    ]
)

# Close connection
connection.close()

print(
    "\nStep 25 Seller Performance Analysis completed successfully."
)