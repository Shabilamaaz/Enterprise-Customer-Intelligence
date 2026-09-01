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


# Seller Customer Reach Analysis
seller_customer_reach = pd.read_sql_query(
    """
    SELECT
        oi.seller_id,
        COUNT(DISTINCT o.customer_id) AS unique_customers,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        ROUND(SUM(oi.price), 2) AS total_sales
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    GROUP BY oi.seller_id
    ORDER BY unique_customers DESC
    """,
    connection
)

print("\nSeller Customer Reach Analysis:")
print(seller_customer_reach.head(10))


# Average Customers per Seller
average_customers = pd.read_sql_query(
    """
    SELECT
        ROUND(
            AVG(unique_customers),
            2
        ) AS average_customers_per_seller
    FROM (
        SELECT
            oi.seller_id,
            COUNT(DISTINCT o.customer_id) AS unique_customers
        FROM order_items oi
        JOIN orders o
            ON oi.order_id = o.order_id
        GROUP BY oi.seller_id
    )
    """,
    connection
)

print("\nAverage Customers per Seller:")
print(average_customers)


# Total Unique Customers Served by Sellers
total_unique_customers = pd.read_sql_query(
    """
    SELECT
        COUNT(DISTINCT o.customer_id) AS total_unique_customers
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    """,
    connection
)

print("\nTotal Unique Customers Served:")
print(total_unique_customers)


# Top Seller by Customer Reach
top_seller = seller_customer_reach.loc[
    seller_customer_reach["unique_customers"].idxmax()
]

print("\nTop Seller by Customer Reach:")
print(top_seller)


# Top 10 Sellers by Customer Reach
top_10_sellers = (
    seller_customer_reach
    .sort_values(
        "unique_customers",
        ascending=False
    )
    .head(10)
)

print("\nTop 10 Sellers by Customer Reach:")
print(
    top_10_sellers[
        [
            "seller_id",
            "unique_customers",
            "total_orders",
            "total_sales"
        ]
    ]
)


# Close connection
connection.close()

print("\nStep 33 Seller Customer Reach Analysis completed successfully.")