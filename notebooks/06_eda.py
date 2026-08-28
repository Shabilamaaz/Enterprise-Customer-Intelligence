import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt

# Project root
project_root = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Database path
db_path = os.path.join(
    project_root,
    "database",
    "customer_intelligence.db"
)

print("Database path:")
print(db_path)

# Connect to database
connection = sqlite3.connect(db_path)

# Load orders data
orders = pd.read_sql_query(
    "SELECT * FROM orders",
    connection
)

print("\nOrders shape:")
print(orders.shape)

print("\nOrders columns:")
print(orders.columns.tolist())

print("\nFirst 5 rows:")
print(orders.head())

print("\nMissing values:")
print(orders.isnull().sum())

# Close connection
connection.close()

print("\nStep 7 EDA setup completed successfully.")

# Order status analysis
connection = sqlite3.connect(db_path)

status_counts = pd.read_sql_query(
    """
    SELECT
        order_status,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY order_status
    ORDER BY order_count DESC
    """,
    connection
)

print("\nOrder Status Analysis:")
print(status_counts)

connection.close()

print("\nStep 8 Order Status Analysis completed successfully.")