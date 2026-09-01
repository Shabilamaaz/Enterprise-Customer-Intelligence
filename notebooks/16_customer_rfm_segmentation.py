import sqlite3
import pandas as pd
import os

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "customer_intelligence.db")

# Check database exists
print("Database exists:", os.path.exists(DB_PATH))

# Connect to database
connection = sqlite3.connect(DB_PATH)

# RFM Analysis
rfm_analysis = pd.read_sql_query(
    """
    SELECT
        o.customer_id,
        MAX(o.order_purchase_timestamp) AS last_order_date,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(p.payment_value), 2) AS monetary
    FROM orders o
JOIN payments p
    ON o.order_id = p.order_id
    GROUP BY o.customer_id

    """,
    connection
)

# Convert date column
rfm_analysis["last_order_date"] = pd.to_datetime(
    rfm_analysis["last_order_date"]
)

# Calculate Recency
reference_date = rfm_analysis["last_order_date"].max()

rfm_analysis["recency"] = (
    reference_date - rfm_analysis["last_order_date"]
).dt.days

# Select important columns
rfm_analysis = rfm_analysis[
    ["customer_id", "recency", "frequency", "monetary"]
]

# Create RFM scores
rfm_analysis["R_score"] = pd.qcut(
    rfm_analysis["recency"],
    4,
    labels=[4, 3, 2, 1],
    duplicates="drop"
)

rfm_analysis["F_score"] = pd.qcut(
    rfm_analysis["frequency"].rank(method="first"),
    4,
    labels=[1, 2, 3, 4],
    duplicates="drop"
)

rfm_analysis["M_score"] = pd.qcut(
    rfm_analysis["monetary"],
    4,
    labels=[1, 2, 3, 4],
    duplicates="drop"
)

# Convert scores to numbers
rfm_analysis["R_score"] = rfm_analysis["R_score"].astype(int)
rfm_analysis["F_score"] = rfm_analysis["F_score"].astype(int)
rfm_analysis["M_score"] = rfm_analysis["M_score"].astype(int)

# Calculate total RFM score
rfm_analysis["RFM_score"] = (
    rfm_analysis["R_score"]
    + rfm_analysis["F_score"]
    + rfm_analysis["M_score"]
)

# Customer segmentation
def segment_customer(score):
    if score >= 10:
        return "Best Customers"
    elif score >= 8:
        return "High Value Customers"
    elif score >= 6:
        return "Regular Customers"
    elif score >= 4:
        return "At Risk Customers"
    else:
        return "Inactive Customers"


rfm_analysis["customer_segment"] = rfm_analysis["RFM_score"].apply(
    segment_customer
)

# Display results
print("\nCustomer RFM Analysis:")
print(rfm_analysis.head(10))

print("\nCustomer Segment Distribution:")
print(
    rfm_analysis["customer_segment"]
    .value_counts()
)

print("\nAverage Monetary Value by Segment:")
print(
    rfm_analysis.groupby("customer_segment")["monetary"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
)

# Close connection
connection.close()

print("\nStep 16 Customer RFM Segmentation completed successfully.")