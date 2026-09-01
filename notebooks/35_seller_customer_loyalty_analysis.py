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


# Seller Customer Loyalty Analysis
seller_loyalty = pd.read_sql_query(
    """
    SELECT
        seller_id,
        COUNT(*) AS total_customers,

        SUM(
            CASE
                WHEN order_count = 1 THEN 1
                ELSE 0
            END
        ) AS one_time_customers,

        SUM(
            CASE
                WHEN order_count > 1 THEN 1
                ELSE 0
            END
        ) AS repeat_customers,

        ROUND(
            100.0 *
            SUM(
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
    ORDER BY repeat_customer_percentage DESC
    """,
    connection
)

print("\nSeller Customer Loyalty Analysis:")
print(seller_loyalty.head(10))


# Assign Loyalty Level
def loyalty_level(percentage):
    if percentage >= 30:
        return "Highly Loyal"
    elif percentage >= 15:
        return "Loyal"
    elif percentage >= 5:
        return "Moderate"
    else:
        return "Low Loyalty"


seller_loyalty["loyalty_level"] = (
    seller_loyalty["repeat_customer_percentage"]
    .apply(loyalty_level)
)


print("\nSeller Loyalty Levels:")
print(
    seller_loyalty[
        [
            "seller_id",
            "total_customers",
            "one_time_customers",
            "repeat_customers",
            "repeat_customer_percentage",
            "loyalty_level"
        ]
    ].head(10)
)


# Average Repeat Customer Percentage
average_loyalty = seller_loyalty[
    "repeat_customer_percentage"
].mean()

print("\nAverage Seller Repeat Customer Percentage:")
print(round(average_loyalty, 2), "%")


# Top Seller by Loyalty
top_loyal_seller = seller_loyalty.loc[
    seller_loyalty["repeat_customer_percentage"].idxmax()
]

print("\nTop Seller by Customer Loyalty:")
print(top_loyal_seller)


# Loyalty Level Distribution
loyalty_distribution = (
    seller_loyalty["loyalty_level"]
    .value_counts()
)

print("\nSeller Loyalty Level Distribution:")
print(loyalty_distribution)


# Top 10 Sellers by Loyalty
top_10_loyal_sellers = (
    seller_loyalty
    .sort_values(
        "repeat_customer_percentage",
        ascending=False
    )
    .head(10)
)

print("\nTop 10 Sellers by Customer Loyalty:")
print(
    top_10_loyal_sellers[
        [
            "seller_id",
            "total_customers",
            "repeat_customers",
            "repeat_customer_percentage",
            "loyalty_level"
        ]
    ]
)


# Close connection
connection.close()

print("\nStep 35 Seller Customer Loyalty Analysis completed successfully.")