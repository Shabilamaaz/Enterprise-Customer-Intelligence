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

# Customer Order Value Analysis
order_value = pd.read_sql_query(
    """
    SELECT
        o.customer_id,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(oi.price + oi.freight_value) AS total_spent,
        AVG(oi.price + oi.freight_value) AS average_order_value
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    GROUP BY o.customer_id
    ORDER BY total_spent DESC
    """,
    connection
)

print("\nCustomer Order Value Analysis:")
print(order_value.head(10))

print("\nTop 10 Customers by Total Spending:")
print(order_value.head(10))

print("\nAverage Order Value:")
print(round(order_value["average_order_value"].mean(), 2))

# Close connection
connection.close()

print("\nStep 14 Customer Order Value Analysis completed successfully.")