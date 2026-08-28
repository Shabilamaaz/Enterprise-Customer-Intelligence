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

# Customer order frequency
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

print("\nCustomer Order Frequency:")
print(customer_orders.head(10))

# Order frequency distribution
frequency_distribution = (
    customer_orders
    .groupby("order_count")
    .size()
    .reset_index(name="customer_count")
    .sort_values("order_count")
)

print("\nOrder Frequency Distribution:")
print(frequency_distribution)

# Close connection
connection.close()

print("\nStep 13 Customer Order Frequency Analysis completed successfully.")