import sqlite3
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

db_path = os.path.join(
    project_root,
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

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM orders")

total_orders = cursor.fetchone()[0]

print("\nTotal Orders:")
print(total_orders)

connection.close()

print("\nStep 6 query completed successfully.")