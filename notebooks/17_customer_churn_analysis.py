import sqlite3
import pandas as pd
import os

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "customer_intelligence.db")

# Check database exists
print("Database exists:", os.path.exists(DB_PATH))

if not os.path.exists(DB_PATH):
    print("\nERROR: Database file nahi mil rahi.")
    exit()

# Connect to database
connection = sqlite3.connect(DB_PATH)

# Customer order activity
customer_activity = pd.read_sql_query(
    """
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS order_count,
        MAX(o.order_purchase_timestamp) AS last_order_date
    FROM orders o
    GROUP BY o.customer_id
    """,
    connection
)

# Convert date
customer_activity["last_order_date"] = pd.to_datetime(
    customer_activity["last_order_date"]
)

# Reference date
reference_date = customer_activity["last_order_date"].max()

# Calculate days since last order
customer_activity["days_since_last_order"] = (
    reference_date - customer_activity["last_order_date"]
).dt.days

# Define churn status
def churn_status(days):
    if days <= 90:
        return "Active"
    elif days <= 180:
        return "At Risk"
    else:
        return "Churned"


customer_activity["churn_status"] = (
    customer_activity["days_since_last_order"]
    .apply(churn_status)
)

# Display customer churn analysis
print("\nCustomer Churn Analysis:")
print(customer_activity.head(10))

# Churn distribution
print("\nCustomer Churn Distribution:")
print(
    customer_activity["churn_status"]
    .value_counts()
)

# Churn percentage
churned_customers = (
    customer_activity["churn_status"] == "Churned"
).sum()

total_customers = len(customer_activity)

churn_percentage = (
    churned_customers / total_customers
) * 100

print("\nTotal Customers:")
print(total_customers)

print("\nChurned Customers:")
print(churned_customers)

print("\nChurn Percentage:")
print(round(churn_percentage, 2), "%")

# Close connection
connection.close()

print("\nStep 17 Customer Churn Analysis completed successfully.")