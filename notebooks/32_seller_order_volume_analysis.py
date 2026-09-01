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


# Seller Order Volume Analysis
seller_order_volume = pd.read_sql_query(
    """
    SELECT
        seller_id,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(price), 2) AS total_sales,
        ROUND(AVG(price), 2) AS average_order_value
    FROM order_items
    GROUP BY seller_id
    ORDER BY total_orders DESC
    """,
    connection
)

print("\nSeller Order Volume Analysis:")
print(seller_order_volume.head(10))


# Total Orders
total_orders = seller_order_volume["total_orders"].sum()

print("\nTotal Seller Orders:")
print(total_orders)


# Top Seller by Order Volume
top_order_seller = seller_order_volume.iloc[0]

print("\nTop Seller by Order Volume:")
print(top_order_seller)


# Average Orders per Seller
average_orders_per_seller = seller_order_volume["total_orders"].mean()

print("\nAverage Orders per Seller:")
print(round(average_orders_per_seller, 2))


# Top Seller Order Contribution
top_seller_order_percentage = (
    top_order_seller["total_orders"] / total_orders
) * 100

print("\nTop Seller Order Contribution:")
print(round(top_seller_order_percentage, 2), "%")


# Top 10 Sellers Order Contribution
top_10_orders = seller_order_volume.head(10)["total_orders"].sum()

top_10_order_percentage = (
    top_10_orders / total_orders
) * 100

print("\nTop 10 Sellers Order Contribution:")
print(round(top_10_order_percentage, 2), "%")


# Close connection
connection.close()

print("\nStep 32 Seller Order Volume Analysis completed successfully.")