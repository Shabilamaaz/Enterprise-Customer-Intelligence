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


# Customer Review Analysis
review_analysis = pd.read_sql_query(
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

print("\nCustomer Review Analysis:")
print(review_analysis)


# Average review score
average_review_score = pd.read_sql_query(
    """
    SELECT
        ROUND(AVG(review_score), 2) AS average_review_score
    FROM reviews
    """,
    connection
)

print("\nAverage Review Score:")
print(average_review_score)


# Total reviews
total_reviews = pd.read_sql_query(
    """
    SELECT
        COUNT(*) AS total_reviews
    FROM reviews
    """,
    connection
)

print("\nTotal Reviews:")
print(total_reviews)


# Most common review score
most_common_score = review_analysis.loc[
    review_analysis["review_count"].idxmax(),
    "review_score"
]

print("\nMost Common Review Score:")
print(most_common_score)


# Close connection
connection.close()

print("\nStep 14 Customer Review Analysis completed successfully.")