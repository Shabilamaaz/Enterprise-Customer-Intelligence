import os
import sqlite3
import pandas as pd


# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "customer_intelligence.db")


# Connect to database
connection = sqlite3.connect(DB_PATH)

print("Database exists:", os.path.exists(DB_PATH))


# Seller Performance Data
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


# Seller Review Data
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


# Merge seller performance and review data
seller_segmentation = seller_analysis.merge(
    seller_reviews,
    on="seller_id",
    how="left"
)


# Fill missing review values
seller_segmentation["total_reviews"] = (
    seller_segmentation["total_reviews"]
    .fillna(0)
)

seller_segmentation["average_review_score"] = (
    seller_segmentation["average_review_score"]
    .fillna(0)
)


# Create Seller Performance Score
seller_segmentation["performance_score"] = (
    seller_segmentation["total_sales"].rank(pct=True) * 0.5
    + seller_segmentation["total_orders"].rank(pct=True) * 0.3
    + seller_segmentation["average_review_score"].rank(pct=True) * 0.2
)


# Seller Segmentation
def segment_seller(score):

    if score >= 0.75:
        return "Top Performing Sellers"

    elif score >= 0.50:
        return "High Performing Sellers"

    elif score >= 0.25:
        return "Regular Sellers"

    else:
        return "Low Performing Sellers"


seller_segmentation["seller_segment"] = (
    seller_segmentation["performance_score"]
    .apply(segment_seller)
)


# Display top sellers
# Display top sellers
print("\nTop Sellers by Performance:")

top_sellers = (
    seller_segmentation
    .sort_values(
        "performance_score",
        ascending=False
    )
    .head(10)
)

print(
    top_sellers[
        [
            "seller_id",
            "total_orders",
            "total_sales",
            "average_review_score",
            "seller_segment"
        ]
    ]
)


# Seller Segment Distribution
print("\nSeller Segment Distribution:")

print(
    seller_segmentation["seller_segment"]
    .value_counts()
)


# Average Sales by Seller Segment
print("\nAverage Sales by Seller Segment:")

print(
    seller_segmentation
    .groupby("seller_segment")["total_sales"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
)


# Average Review Score by Seller Segment
print("\nAverage Review Score by Seller Segment:")

print(
    seller_segmentation
    .groupby("seller_segment")["average_review_score"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
)


# Close connection
connection.close()


print("\nStep 27 Seller Segmentation Analysis completed successfully.")