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


# Seller Sales and Review Analysis
seller_analysis = pd.read_sql_query(
    """
    SELECT
        oi.seller_id,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        COUNT(oi.order_item_id) AS total_items,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_sales,
        ROUND(AVG(oi.price + oi.freight_value), 2) AS average_sales_per_item
    FROM order_items oi
    GROUP BY oi.seller_id
    """,
    connection
)


# Seller Review Analysis
seller_reviews = pd.read_sql_query(
    """
    SELECT
        oi.seller_id,
        COUNT(DISTINCT r.review_id) AS total_reviews,
        ROUND(AVG(r.review_score), 2) AS average_review_score
    FROM order_items oi
    JOIN reviews r
        ON oi.order_id = r.order_id
    GROUP BY oi.seller_id
    """,
    connection
)


# Merge sales and review data
seller_performance = seller_analysis.merge(
    seller_reviews,
    on="seller_id",
    how="left"
)


# Remove sellers without reviews
seller_performance = seller_performance.dropna(
    subset=["average_review_score"]
)


# Calculate correlation
sales_review_correlation = seller_performance[
    ["total_sales", "average_review_score"]
].corr().loc[
    "total_sales",
    "average_review_score"
]


print("\nSales and Review Correlation:")
print(round(sales_review_correlation, 4))


# Top sellers by sales
print("\nTop 10 Sellers by Total Sales:")

print(
    seller_performance[
        [
            "seller_id",
            "total_orders",
            "total_sales",
            "average_review_score"
        ]
    ]
    .sort_values(
        "total_sales",
        ascending=False
    )
    .head(10)
)


# Top rated sellers
print("\nTop 10 Sellers by Review Score:")

print(
    seller_performance[
        [
            "seller_id",
            "total_orders",
            "total_sales",
            "average_review_score"
        ]
    ]
    .sort_values(
        "average_review_score",
        ascending=False
    )
    .head(10)
)


# Average sales by review score
print("\nAverage Sales by Review Score:")

print(
    seller_performance
    .groupby("average_review_score")["total_sales"]
    .mean()
    .round(2)
    .sort_index(ascending=False)
    .head(10)
)


# Overall averages
print("\nAverage Seller Sales:")
print(
    round(
        seller_performance["total_sales"].mean(),
        2
    )
)

print("\nAverage Seller Review Score:")
print(
    round(
        seller_performance["average_review_score"].mean(),
        2
    )
)


# Close connection
connection.close()


print(
    "\nStep 28 Seller Sales and Review Analysis "
    "completed successfully."
)