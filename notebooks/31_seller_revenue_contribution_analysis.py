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


# Seller Revenue Analysis
seller_revenue = pd.read_sql_query(
    """
    SELECT
        seller_id,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(price), 2) AS total_revenue
    FROM order_items
    GROUP BY seller_id
    ORDER BY total_revenue DESC
    """,
    connection
)

print("\nSeller Revenue Analysis:")
print(seller_revenue.head(10))


# Total Revenue
total_revenue = seller_revenue["total_revenue"].sum()

print("\nTotal Seller Revenue:")
print(round(total_revenue, 2))


# Top Seller Revenue
top_seller_revenue = seller_revenue.iloc[0]

print("\nTop Seller by Revenue:")
print(top_seller_revenue)


# Top Seller Revenue Contribution
top_seller_percentage = (
    top_seller_revenue["total_revenue"] / total_revenue
) * 100

print("\nTop Seller Revenue Contribution:")
print(round(top_seller_percentage, 2), "%")


# Average Revenue per Seller
average_revenue_per_seller = seller_revenue["total_revenue"].mean()

print("\nAverage Revenue per Seller:")
print(round(average_revenue_per_seller, 2))


# Top 10 Sellers Revenue Contribution
top_10_revenue = seller_revenue.head(10)["total_revenue"].sum()

top_10_percentage = (
    top_10_revenue / total_revenue
) * 100

print("\nTop 10 Sellers Revenue Contribution:")
print(round(top_10_percentage, 2), "%")


# Close connection
connection.close()

print("\nStep 31 Seller Revenue Contribution Analysis completed successfully.")