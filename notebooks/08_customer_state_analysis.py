import sqlite3
import pandas as pd
import os

# Database path
db_path = r"D:\Enterprise-Customer-Intelligence\database\customer_intelligence.db"

print("Database path:")
print(db_path)

# Check database
if not os.path.exists(db_path):
    print("\nERROR: Database file nahi mil rahi.")
    exit()

print("\nDatabase exists:")
print(True)

# Connect to database
connection = sqlite3.connect(db_path)

# State-wise customer count
state_analysis = pd.read_sql_query(
    """
    SELECT
        customer_state,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY customer_state
    ORDER BY customer_count DESC
    """,
    connection
)

print("\nCustomer State Analysis:")
print(state_analysis)

# Top 10 states
print("\nTop 10 States by Customer Count:")
print(state_analysis.head(10))

# Close connection
connection.close()

print("\nStep 10 Customer State Analysis completed successfully.")