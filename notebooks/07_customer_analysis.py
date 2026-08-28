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

# Read customers table
customers = pd.read_sql_query(
    "SELECT * FROM customers",
    connection
)

print("\nCustomer Data Loaded Successfully.")

# Basic information
print("\nNumber of Customers:")
print(len(customers))

print("\nCustomer Columns:")
print(customers.columns.tolist())

print("\nFirst 5 Customers:")
print(customers.head())

print("\nMissing Values:")
print(customers.isnull().sum())

# Close connection
connection.close()

print("\nStep 9 Customer Analysis completed successfully.")