import sqlite3
import pandas as pd

# ============================================================
# Step 62: Seller Revenue Profitability Analysis
# ============================================================

# Step 1: Connect to Database
connection = sqlite3.connect("../data/database/olist.db")

# Step 2: Load Seller Revenue Data
query = """
SELECT
    s.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.price) AS total_revenue,
    AVG(oi.price) AS average_order_value,
    AVG(r.review_score) AS average_review_score
FROM sellers s
JOIN order_items oi
    ON s.seller_id = oi.seller_id
JOIN orders o
    ON oi.order_id = o.order_id
LEFT JOIN order_reviews r
    ON o.order_id = r.order_id
GROUP BY s.seller_id
"""

df = pd.read_sql_query(query, connection)

# Step 3: Calculate Revenue per Order
df["revenue_per_order"] = (
    df["total_revenue"] / df["total_orders"]
)

# Step 4: Calculate Profitability Score
df["profitability_score"] = (
    df["total_revenue"] * 0.5
    + df["revenue_per_order"] * 0.3
    + df["average_review_score"].fillna(0) * 100 * 0.2
)

# Step 5: Create Profitability Categories
df["profitability_category"] = pd.cut(
    df["profitability_score"],
    bins=[-float("inf"), 500, 1500, float("inf")],
    labels=["Low Profitability", "Medium Profitability", "High Profitability"]
)

# Step 6: Top 10 Most Profitable Sellers
top_sellers = df.sort_values(
    by="profitability_score",
    ascending=False
).head(10)

# Step 7: Display Summary
print("\nSeller Revenue Profitability Summary")
print("------------------------------------")

print("\nTotal Sellers:")
print(len(df))

print("\nHigh Profitability Sellers:")
print(
    (df["profitability_category"] == "High Profitability").sum()
)

print("\nMedium Profitability Sellers:")
print(
    (df["profitability_category"] == "Medium Profitability").sum()
)

print("\nLow Profitability Sellers:")
print(
    (df["profitability_category"] == "Low Profitability").sum()
)

print("\nHighest Profitability Score:")
print(round(df["profitability_score"].max(), 2))

# Step 8: Display Top 10 Sellers
print("\nTop 10 Sellers by Profitability:")
print(
    top_sellers[
        [
            "seller_id",
            "total_orders",
            "total_revenue",
            "revenue_per_order",
            "average_review_score",
            "profitability_score",
            "profitability_category"
        ]
    ].to_string(index=False)
)

# Step 9: Close Connection
connection.close()

# ============================================================
# Completion Message
# ============================================================

print(
    "\nStep 62 Seller Revenue Profitability Analysis "
    "completed successfully."
)