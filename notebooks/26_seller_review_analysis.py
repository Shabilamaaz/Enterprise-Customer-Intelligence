import os
import sqlite3
import pandas as pd


# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "customer_intelligence.db")


# Connect to database
connection = sqlite3.connect(DB_PATH)

print("Database exists:", os.path.exists(DB_PATH))


# Seller Review Analysis
seller_review_analysis = pd.read_sql_query(
    """
    SELECT
        oi.seller_id,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        COUNT(DISTINCT r.review_id) AS total_reviews,
        ROUND(AVG(r.review_score), 2) AS average_review_score
    FROM order_items oi
    JOIN reviews r
        ON oi.order_id = r.order_id
    GROUP BY oi.seller_id
    ORDER BY average_review_score DESC
    """,
    connection
)


# Display seller review analysis
print("\nSeller Review Analysis:")
print(seller_review_analysis.head(10))


# Review Score Distribution
review_distribution = pd.read_sql_query(
    """
    SELECT
        review_score,
        COUNT(*) AS review_count
    FROM reviews
    GROUP BY review_score
    ORDER BY review_score
    """,
    connection
)


print("\nReview Score Distribution:")
print(review_distribution)


# Close connection
connection.close()


print("\nStep 26 Seller Review Analysis completed successfully.")