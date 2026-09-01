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

# Customer retention analysis
retention_analysis = pd.read_sql_query(
    """
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(p.payment_value), 2) AS total_spent,
        ROUND(
            SUM(p.payment_value) / COUNT(DISTINCT o.order_id),
            2
        ) AS average_order_value,
        MAX(o.order_purchase_timestamp) AS last_order_date
    FROM orders o
    JOIN payments p
        ON o.order_id = p.order_id
    GROUP BY o.customer_id
    """,
    connection
)

# Convert date column
retention_analysis["last_order_date"] = pd.to_datetime(
    retention_analysis["last_order_date"]
)

# Reference date
reference_date = retention_analysis["last_order_date"].max()

# Calculate days since last order
retention_analysis["days_since_last_order"] = (
    reference_date - retention_analysis["last_order_date"]
).dt.days


# Customer retention status
def retention_status(days):
    if days <= 90:
        return "Retained"
    elif days <= 180:
        return "At Risk"
    else:
        return "Churned"


retention_analysis["retention_status"] = (
    retention_analysis["days_since_last_order"]
    .apply(retention_status)
)


# Display retention analysis
print("\nCustomer Retention Analysis:")
print(retention_analysis.head(10))


# Retention status distribution
print("\nCustomer Retention Distribution:")
print(
    retention_analysis["retention_status"]
    .value_counts()
)


# Retention percentage
total_customers = len(retention_analysis)

retained_customers = (
    retention_analysis["retention_status"] == "Retained"
).sum()

retained_percentage = (
    retained_customers / total_customers
) * 100

print("\nTotal Customers:")
print(total_customers)

print("\nRetained Customers:")
print(retained_customers)

print("\nRetention Percentage:")
print(round(retained_percentage, 2), "%")


# Average spending by retention status
print("\nAverage Spending by Retention Status:")
print(
    retention_analysis
    .groupby("retention_status")["total_spent"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
)


# Average orders by retention status
print("\nAverage Orders by Retention Status:")
print(
    retention_analysis
    .groupby("retention_status")["total_orders"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
)


# Close connection
connection.close()

print("\nStep 18 Customer Retention Analysis completed successfully.")