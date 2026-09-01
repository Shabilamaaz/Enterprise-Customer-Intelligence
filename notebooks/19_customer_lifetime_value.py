import sqlite3
import pandas as pd
import os

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "customer_intelligence.db")

# Check database exists
print("Database exists:", os.path.exists(DB_PATH))

# Connect to database
connection = sqlite3.connect(DB_PATH)

# Customer Lifetime Value Analysis
clv_analysis = pd.read_sql_query(
    """
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(p.payment_value), 2) AS total_spent,
        ROUND(AVG(p.payment_value), 2) AS average_order_value,
        MIN(o.order_purchase_timestamp) AS first_order_date,
        MAX(o.order_purchase_timestamp) AS last_order_date
    FROM orders o
    JOIN payments p
        ON o.order_id = p.order_id
    GROUP BY o.customer_id
    """,
    connection
)

# Convert date columns
clv_analysis["first_order_date"] = pd.to_datetime(
    clv_analysis["first_order_date"]
)

clv_analysis["last_order_date"] = pd.to_datetime(
    clv_analysis["last_order_date"]
)

# Calculate customer lifetime in days
clv_analysis["customer_lifetime_days"] = (
    clv_analysis["last_order_date"]
    - clv_analysis["first_order_date"]
).dt.days

# Replace zero lifetime with 1 day
clv_analysis["customer_lifetime_days"] = (
    clv_analysis["customer_lifetime_days"]
    .replace(0, 1)
)

# Calculate average monthly value
clv_analysis["monthly_value"] = (
    clv_analysis["total_spent"]
    / (clv_analysis["customer_lifetime_days"] / 30)
)

# Handle customers with only one order
clv_analysis["monthly_value"] = (
    clv_analysis["monthly_value"]
    .replace([float("inf"), -float("inf")], 0)
    .fillna(clv_analysis["total_spent"])
)

# Estimated Customer Lifetime Value
clv_analysis["estimated_clv"] = (
    clv_analysis["monthly_value"] * 12
)

clv_analysis["estimated_clv"] = (
    clv_analysis["estimated_clv"].round(2)
)

# Select important columns
clv_analysis = clv_analysis[
    [
        "customer_id",
        "total_orders",
        "total_spent",
        "average_order_value",
        "customer_lifetime_days",
        "estimated_clv"
    ]
]

# Display results
print("\nCustomer Lifetime Value Analysis:")
print(clv_analysis.head(10))

print("\nTop 10 Customers by Total Spending:")
print(
    clv_analysis
    .sort_values("total_spent", ascending=False)
    .head(10)
    [
        [
            "customer_id",
            "total_orders",
            "total_spent",
            "average_order_value"
        ]
    ]
)

print("\nTop 10 Customers by Estimated CLV:")
print(
    clv_analysis
    .sort_values("estimated_clv", ascending=False)
    .head(10)
    [
        [
            "customer_id",
            "total_orders",
            "total_spent",
            "estimated_clv"
        ]
    ]
)

print("\nAverage Estimated CLV:")
print(
    round(clv_analysis["estimated_clv"].mean(), 2)
)

# Close connection
connection.close()

print("\nStep 19 Customer Lifetime Value Analysis completed successfully.")