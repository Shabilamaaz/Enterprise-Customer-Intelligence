import sqlite3
import pandas as pd
import os

# Database path
db_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "database",
    "customer_intelligence.db"
)

print("Database path:")
print(db_path)

print("\nDatabase exists:")
print(os.path.exists(db_path))

if not os.path.exists(db_path):
    print("\nERROR: Database file nahi mil rahi.")
    exit()

# Connect to database
connection = sqlite3.connect(db_path)

# Customer payment analysis
payment_analysis = pd.read_sql_query(
    """
    SELECT
        payment_type,
        COUNT(*) AS payment_count,
        ROUND(SUM(payment_value), 2) AS total_payment_value,
        ROUND(AVG(payment_value), 2) AS average_payment_value
    FROM payments
    GROUP BY payment_type
    ORDER BY total_payment_value DESC
    """,
    connection
)

print("\nCustomer Payment Analysis:")
print(payment_analysis)

# Most used payment method
print("\nMost Used Payment Method:")
print(
    payment_analysis.iloc[0]["payment_type"]
)

# Close connection
connection.close()

print("\nStep 13 Customer Payment Analysis completed successfully.")