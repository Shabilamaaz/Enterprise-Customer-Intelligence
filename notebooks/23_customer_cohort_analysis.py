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

# Customer Cohort Analysis
cohort_analysis = pd.read_sql_query(
    """
    SELECT
        customer_id,
        order_id,
        order_purchase_timestamp
    FROM orders
    """,
    connection
)

# Convert date column
cohort_analysis["order_purchase_timestamp"] = pd.to_datetime(
    cohort_analysis["order_purchase_timestamp"]
)

# Create order month
cohort_analysis["order_month"] = (
    cohort_analysis["order_purchase_timestamp"]
    .dt.to_period("M")
)

# Find first purchase month for each customer
first_purchase = (
    cohort_analysis
    .groupby("customer_id")["order_month"]
    .min()
    .reset_index()
)

first_purchase.columns = [
    "customer_id",
    "cohort_month"
]

# Merge cohort month
cohort_analysis = cohort_analysis.merge(
    first_purchase,
    on="customer_id",
    how="left"
)

# Calculate cohort index
cohort_analysis["cohort_index"] = (
    (cohort_analysis["order_month"].dt.year -
     cohort_analysis["cohort_month"].dt.year) * 12
    +
    (cohort_analysis["order_month"].dt.month -
     cohort_analysis["cohort_month"].dt.month)
    + 1
)

# Count unique customers in each cohort
cohort_table = (
    cohort_analysis
    .groupby(
        ["cohort_month", "cohort_index"]
    )["customer_id"]
    .nunique()
    .reset_index()
)

# Create cohort retention table
cohort_pivot = cohort_table.pivot(
    index="cohort_month",
    columns="cohort_index",
    values="customer_id"
)

# Calculate retention percentage
cohort_size = cohort_pivot.iloc[:, 0]

retention_table = (
    cohort_pivot
    .divide(cohort_size, axis=0)
    * 100
)

retention_table = retention_table.round(2)

# Display cohort customer counts
print("\nCustomer Cohort Analysis:")
print(cohort_pivot.head(10))

# Display retention percentage
print("\nCustomer Cohort Retention (%):")
print(retention_table.head(10))

# Average retention by cohort month
print("\nAverage Retention by Cohort:")
print(
    retention_table
    .mean(axis=1)
    .round(2)
    .sort_values(ascending=False)
    .head(10)
)

# Month 1 retention
if 2 in retention_table.columns:
    print("\nMonth 1 Retention:")
    print(
        retention_table[2]
        .mean()
        .round(2),
        "%"
    )

# Month 3 retention
if 4 in retention_table.columns:
    print("\nMonth 3 Retention:")
    print(
        retention_table[4]
        .mean()
        .round(2),
        "%"
    )

# Close connection
connection.close()

print(
    "\nStep 23 Customer Cohort Analysis completed successfully."
)