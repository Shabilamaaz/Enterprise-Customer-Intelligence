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

# Load customer orders
customer_orders = pd.read_sql_query(
    """
    SELECT
        c.customer_unique_id,
        COUNT(o.order_id) AS order_count
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
    """,
    connection
)

print("\nCustomer Order Analysis:")
print(customer_orders.head(10))

# Repeat customers
repeat_customers = customer_orders[
    customer_orders["order_count"] > 1
]

# Repeat customer percentage
repeat_percentage = (
    len(repeat_customers) / len(customer_orders)
) * 100

print("\nTotal Customers:")
print(len(customer_orders))

print("\nRepeat Customers:")
print(len(repeat_customers))

print("\nRepeat Customer Percentage:")
print(round(repeat_percentage, 2), "%")

# Close connection
connection.close()

print("\nStep 12 Repeat Customer Analysis completed successfully.")