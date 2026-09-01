import sqlite3
import pandas as pd
import os

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "customer_intelligence.db"
)

# Check database exists
print("Database exists:", os.path.exists(DB_PATH))

# Connect to database
connection = sqlite3.connect(DB_PATH)

# Order Delivery Analysis
delivery_analysis = pd.read_sql_query(
    """
    SELECT
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp,
        order_delivered_customer_date,
        order_estimated_delivery_date
    FROM orders
    WHERE order_delivered_customer_date IS NOT NULL
    """,
    connection
)

# Convert date columns
delivery_analysis["order_purchase_timestamp"] = pd.to_datetime(
    delivery_analysis["order_purchase_timestamp"]
)

delivery_analysis["order_delivered_customer_date"] = pd.to_datetime(
    delivery_analysis["order_delivered_customer_date"]
)

delivery_analysis["order_estimated_delivery_date"] = pd.to_datetime(
    delivery_analysis["order_estimated_delivery_date"]
)

# Calculate actual delivery days
delivery_analysis["delivery_days"] = (
    delivery_analysis["order_delivered_customer_date"]
    - delivery_analysis["order_purchase_timestamp"]
).dt.days

# Calculate delivery delay
delivery_analysis["delivery_delay_days"] = (
    delivery_analysis["order_delivered_customer_date"]
    - delivery_analysis["order_estimated_delivery_date"]
).dt.days

# Classify delivery status
delivery_analysis["delivery_status"] = delivery_analysis[
    "delivery_delay_days"
].apply(
    lambda x: "Late" if x > 0 else "On Time"
)

# Total orders
total_orders = len(delivery_analysis)

# Late orders
late_orders = (
    delivery_analysis["delivery_status"] == "Late"
).sum()

# On-time orders
on_time_orders = (
    delivery_analysis["delivery_status"] == "On Time"
).sum()

# Late delivery percentage
late_delivery_percentage = (
    late_orders / total_orders * 100
)

# Average delivery time
average_delivery_days = (
    delivery_analysis["delivery_days"]
    .mean()
)

# Average delivery delay
average_delivery_delay = (
    delivery_analysis["delivery_delay_days"]
    .mean()
)

# Display sample results
print("\nOrder Delivery Analysis:")
print(
    delivery_analysis[
        [
            "order_id",
            "delivery_days",
            "delivery_delay_days",
            "delivery_status"
        ]
    ].head(10)
)

# Display overall metrics
print("\nTotal Delivered Orders:")
print(total_orders)

print("\nOn-Time Orders:")
print(on_time_orders)

print("\nLate Orders:")
print(late_orders)

print("\nLate Delivery Percentage:")
print(
    round(late_delivery_percentage, 2),
    "%"
)

print("\nAverage Delivery Time:")
print(
    round(average_delivery_days, 2),
    "days"
)

print("\nAverage Delivery Delay:")
print(
    round(average_delivery_delay, 2),
    "days"
)

# Delivery status distribution
print("\nDelivery Status Distribution:")
print(
    delivery_analysis["delivery_status"]
    .value_counts()
)

# Average delivery time by delivery status
print("\nAverage Delivery Time by Status:")
print(
    delivery_analysis
    .groupby("delivery_status")["delivery_days"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
)

# Close connection
connection.close()

print(
    "\nStep 24 Order Delivery Analysis completed successfully."
)