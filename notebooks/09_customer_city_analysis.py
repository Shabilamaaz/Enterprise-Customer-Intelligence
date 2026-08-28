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

# City-wise customer count
city_analysis = pd.read_sql_query(
    """
    SELECT
        customer_city,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY customer_city
    ORDER BY customer_count DESC
    """,
    connection
)

print("\nCustomer City Analysis:")
print(city_analysis.head(20))

# Top 10 cities
print("\nTop 10 Cities by Customer Count:")
print(city_analysis.head(10))

# Close connection
connection.close()

print("\nStep 11 Customer City Analysis completed successfully.")