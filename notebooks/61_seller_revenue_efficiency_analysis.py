import sqlite3
import pandas as pd

# ============================================================
# Step 61: Seller Revenue Efficiency Analysis
# ============================================================

# Step 1: Connect to Database
connection = sqlite3.connect("../database/olist.db")

# Step 2: Load Seller Revenue Data
query = """
SELECT
    s.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.price + oi.freight_value) AS total_revenue,
    AVG(oi.price + oi.freight_value) AS average_order_value,
    AVG(r.review_score) AS average_review_score
FROM sellers s
JOIN order_items oi
    ON s.seller_id = oi.seller_id
LEFT JOIN order_reviews r
    ON oi.order_id = r.order_id
GROUP BY s.seller_id
"""

seller_data = pd.read_sql_query(query, connection)

# Step 3: Calculate Revenue Efficiency
seller_data["revenue_per_order"] = (
    seller_data["total_revenue"] /
    seller_data["total_orders"]
)

# Step 4: Calculate Efficiency Score
seller_data["efficiency_score"] = (
    seller_data["revenue_per_order"]
    / seller_data["revenue_per_order"].max()
) * 100

seller_data["efficiency_score"] = seller_data[
    "efficiency_score"
].round(2)

# Step 5: Categorize Sellers
def categorize_efficiency(score):
    if score >= 75:
        return "High Efficiency"
    elif score >= 40:
        return "Medium Efficiency"
    else:
        return "Low Efficiency"


seller_data["efficiency_category"] = seller_data[
    "efficiency_score"
].apply(categorize_efficiency)

# Step 6: Count Efficiency Categories
high_efficiency = (
    seller_data["efficiency_category"] == "High Efficiency"
).sum()

medium_efficiency = (
    seller_data["efficiency_category"] == "Medium Efficiency"
).sum()

low_efficiency = (
    seller_data["efficiency_category"] == "Low Efficiency"
).sum()

# Step 7: Top 10 Efficient Sellers
top_sellers = seller_data.sort_values(
    by="efficiency_score",
    ascending=False
).head(10)

# Step 8: Display Results
print("\nHigh Efficiency Sellers:")
print(high_efficiency)

print("\nMedium Efficiency Sellers:")
print(medium_efficiency)

print("\nLow Efficiency Sellers:")
print(low_efficiency)

print("\nHighest Efficiency Score:")
print(seller_data["efficiency_score"].max())

print("\nTop 10 Sellers by Revenue Efficiency:")
print(
    top_sellers[
        [
            "seller_id",
            "total_orders",
            "total_revenue",
            "revenue_per_order",
            "efficiency_score",
            "efficiency_category"
        ]
    ].to_string(index=False)
)

# Step 9: Close Connection
connection.close()

# ============================================================
# Completion Message
# ============================================================

print(
    "\nStep 61 Seller Revenue Efficiency Analysis "
    "completed successfully."
)