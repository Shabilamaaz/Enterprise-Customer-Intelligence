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


# Seller Payment Analysis
seller_payment_analysis = pd.read_sql_query(
    """
    SELECT
        oi.seller_id,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        ROUND(SUM(oi.price), 2) AS total_sales,
        ROUND(AVG(oi.price), 2) AS average_order_value
    FROM order_items oi
    GROUP BY oi.seller_id
    ORDER BY total_sales DESC
    """,
    connection
)

print("\nSeller Payment Analysis:")
print(seller_payment_analysis.head(10))


# Top Seller by Sales
top_seller = seller_payment_analysis.iloc[0]

print("\nTop Seller by Sales:")
print(top_seller)


# Average Seller Sales
average_seller_sales = seller_payment_analysis["total_sales"].mean()

print("\nAverage Seller Sales:")
print(round(average_seller_sales, 2))


# Total Seller Sales
total_seller_sales = seller_payment_analysis["total_sales"].sum()

print("\nTotal Seller Sales:")
print(round(total_seller_sales, 2))


# Average Order Value
average_order_value = seller_payment_analysis["average_order_value"].mean()

print("\nAverage Order Value:")
print(round(average_order_value, 2))


# Top 10 Sellers
top_sellers = (
    seller_payment_analysis
    .sort_values("total_sales", ascending=False)
    .head(10)
)

print("\nTop 10 Sellers by Sales:")
print(
    top_sellers[
        [
            "seller_id",
            "total_orders",
            "total_sales",
            "average_order_value"
        ]
    ]
)


# Close connection
connection.close()

print("\nStep 30 Seller Payment Analysis completed successfully.")