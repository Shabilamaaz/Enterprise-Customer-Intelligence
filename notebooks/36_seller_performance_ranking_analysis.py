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


# Seller Performance Ranking Analysis
seller_performance = pd.read_sql_query(
    """
    SELECT
        oi.seller_id,

        COUNT(DISTINCT oi.order_id) AS total_orders,

        COUNT(DISTINCT o.customer_id) AS unique_customers,

        ROUND(SUM(oi.price), 2) AS total_sales,

        ROUND(
            AVG(oi.price),
            2
        ) AS average_order_value

    FROM order_items oi

    JOIN orders o
        ON oi.order_id = o.order_id

    GROUP BY oi.seller_id
    """,
    connection
)

print("\nSeller Performance Analysis:")
print(seller_performance.head(10))


# Create Performance Score
seller_performance["performance_score"] = (
    seller_performance["total_sales"] * 0.50
    + seller_performance["total_orders"] * 0.20
    + seller_performance["unique_customers"] * 0.30
)


# Rank Sellers
seller_performance["performance_rank"] = (
    seller_performance["performance_score"]
    .rank(
        method="dense",
        ascending=False
    )
    .astype(int)
)


# Sort by Rank
seller_performance = seller_performance.sort_values(
    "performance_rank"
)


print("\nSeller Performance Ranking:")
print(
    seller_performance[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "average_order_value",
            "performance_score",
            "performance_rank"
        ]
    ].head(10)
)


# Top Performing Seller
top_seller = seller_performance.iloc[0]

print("\nTop Performing Seller:")
print(top_seller)


# Average Performance Score
average_performance_score = (
    seller_performance["performance_score"].mean()
)

print("\nAverage Seller Performance Score:")
print(round(average_performance_score, 2))


# Top 10 Sellers
top_10_sellers = seller_performance.head(10)

print("\nTop 10 Sellers by Performance:")
print(
    top_10_sellers[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "performance_score",
            "performance_rank"
        ]
    ]
)


# Close connection
connection.close()

print("\nStep 36 Seller Performance Ranking Analysis completed successfully.")