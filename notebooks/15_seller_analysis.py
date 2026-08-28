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


# Seller Analysis
seller_analysis = pd.read_sql_query(
    """
    SELECT
        seller_id,
        COUNT(DISTINCT order_id) AS order_count,
        ROUND(SUM(price), 2) AS total_sales,
        ROUND(AVG(price), 2) AS average_order_value
    FROM order_items
    GROUP BY seller_id
    ORDER BY total_sales DESC
    """,
    connection
)

print("\nSeller Analysis:")
print(seller_analysis.head(10))


# Total sellers
total_sellers = pd.read_sql_query(
    """
    SELECT
        COUNT(DISTINCT seller_id) AS total_sellers
    FROM order_items
    """,
    connection
)

print("\nTotal Sellers:")
print(total_sellers)


# Top seller by sales
top_seller = seller_analysis.iloc[0]["seller_id"]

print("\nTop Seller by Sales:")
print(top_seller)


# Close connection
connection.close()

print("\nStep 15 Seller Analysis completed successfully.")