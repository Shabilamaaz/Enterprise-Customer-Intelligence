import sqlite3
import pandas as pd

# ============================================================
# Step 60: Seller Revenue Quality Analysis
# ============================================================

# Step 1: Connect to Database
connection = sqlite3.connect("data/database/olist.db")
# Step 2: Load Seller Revenue Data
query = """
SELECT
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.price) AS total_revenue,
    AVG(oi.price) AS average_order_value
FROM order_items oi
GROUP BY oi.seller_id
"""

seller_revenue = pd.read_sql_query(query, connection)

# Step 3: Calculate Revenue Quality Metrics
seller_revenue["revenue_per_order"] = (
    seller_revenue["total_revenue"] /
    seller_revenue["total_orders"]
)

# Step 4: Revenue Quality Score
seller_revenue["quality_score"] = (
    seller_revenue["revenue_per_order"] /
    seller_revenue["revenue_per_order"].max()
) * 100

# Step 5: Classify Revenue Quality
seller_revenue["quality_category"] = pd.cut(
    seller_revenue["quality_score"],
    bins=[-1, 33, 66, 100],
    labels=["Low Quality", "Medium Quality", "High Quality"]
)

# Step 6: Display Results
print("\nSeller Revenue Quality Analysis")
print("--------------------------------")

print("\nTotal Sellers:")
print(len(seller_revenue))

print("\nAverage Quality Score:")
print(round(seller_revenue["quality_score"].mean(), 2))

print("\nHighest Quality Score:")
print(round(seller_revenue["quality_score"].max(), 2))

print("\nHigh Quality Sellers:")
print(
    (seller_revenue["quality_category"] == "High Quality").sum()
)

print("\nMedium Quality Sellers:")
print(
    (seller_revenue["quality_category"] == "Medium Quality").sum()
)

print("\nLow Quality Sellers:")
print(
    (seller_revenue["quality_category"] == "Low Quality").sum()
)

# Step 7: Top Quality Sellers
top_quality_sellers = seller_revenue.sort_values(
    "quality_score",
    ascending=False
).head(10)

print("\nTop 10 Sellers by Revenue Quality:")
print(
    top_quality_sellers[
        [
            "seller_id",
            "total_orders",
            "total_revenue",
            "revenue_per_order",
            "quality_score"
        ]
    ].to_string(index=False)
)

# Step 8: Close Connection
connection.close()

# ============================================================
# Completion Message
# ============================================================

print(
    "\nStep 60 Seller Revenue Quality Analysis "
    "completed successfully."
)