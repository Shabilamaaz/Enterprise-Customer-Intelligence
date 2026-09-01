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


# Seller Repeat Customer Analysis
seller_repeat_customers = pd.read_sql_query(
    """
    SELECT
        seller_id,
        COUNT(*) AS total_customers,
        SUM(
            CASE
                WHEN order_count > 1 THEN 1
                ELSE 0
            END
        ) AS repeat_customers,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN order_count > 1 THEN 1
                    ELSE 0
                END
            ) / COUNT(*),
            2
        ) AS repeat_customer_percentage
    FROM (
        SELECT
            oi.seller_id,
            o.customer_id,
            COUNT(DISTINCT oi.order_id) AS order_count
        FROM order_items oi
        JOIN orders o
            ON oi.order_id = o.order_id
        GROUP BY
            oi.seller_id,
            o.customer_id
    )
    GROUP BY seller_id
    ORDER BY repeat_customers DESC
    """,
    connection
)

print("\nSeller Repeat Customer Analysis:")
print(seller_repeat_customers.head(10))


# Average Repeat Customers per Seller
average_repeat_customers = pd.read_sql_query(
    """
    SELECT
        ROUND(AVG(repeat_customers), 2)
        AS average_repeat_customers_per_seller
    FROM (
        SELECT
            seller_id,
            SUM(
                CASE
                    WHEN order_count > 1 THEN 1
                    ELSE 0
                END
            ) AS repeat_customers
        FROM (
            SELECT
                oi.seller_id,
                o.customer_id,
                COUNT(DISTINCT oi.order_id) AS order_count
            FROM order_items oi
            JOIN orders o
                ON oi.order_id = o.order_id
            GROUP BY
                oi.seller_id,
                o.customer_id
        )
        GROUP BY seller_id
    )
    """,
    connection
)

print("\nAverage Repeat Customers per Seller:")
print(average_repeat_customers)


# Overall Repeat Customers
overall_repeat_customers = pd.read_sql_query(
    """
    SELECT
        COUNT(*) AS repeat_customers
    FROM (
        SELECT
            customer_id
        FROM orders
        GROUP BY customer_id
        HAVING COUNT(DISTINCT order_id) > 1
    )
    """,
    connection
)

print("\nOverall Repeat Customers:")
print(overall_repeat_customers)


# Top Seller by Repeat Customers
top_repeat_seller = seller_repeat_customers.loc[
    seller_repeat_customers["repeat_customers"].idxmax()
]

print("\nTop Seller by Repeat Customers:")
print(top_repeat_seller)


# Top 10 Sellers by Repeat Customer Percentage
top_10_repeat_sellers = (
    seller_repeat_customers
    .sort_values(
        "repeat_customer_percentage",
        ascending=False
    )
    .head(10)
)

print("\nTop 10 Sellers by Repeat Customer Percentage:")
print(
    top_10_repeat_sellers[
        [
            "seller_id",
            "total_customers",
            "repeat_customers",
            "repeat_customer_percentage"
        ]
    ]
)


# Close connection
connection.close()

print("\nStep 34 Seller Repeat Customer Analysis completed successfully.")