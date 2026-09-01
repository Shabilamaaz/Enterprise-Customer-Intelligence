import sqlite3
import pandas as pd
from pathlib import Path

# ============================================================
# Step 64: Seller Revenue Margin Analysis
# ============================================================

# Step 1: Connect to Database
db_path = Path(__file__).resolve().parent.parent / "data" / "database" / "olist.db"
connection = sqlite3.connect(db_path)

# Step 2: Calculate Seller Revenue and Net Revenue
query = """
SELECT
    seller_id,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(price) AS total_revenue,
    SUM(freight_value) AS total_freight,
    SUM(price - freight_value) AS net_revenue
FROM order_items
GROUP BY seller_id
"""

seller_margin = pd.read_sql_query(query, connection)

# Step 3: Calculate Revenue Margin
seller_margin["revenue_margin"] = (
    seller_margin["net_revenue"] /
    seller_margin["total_revenue"]
) * 100

# Step 4: Handle invalid values
seller_margin["revenue_margin"] = (
    seller_margin["revenue_margin"]
    .replace([float("inf"), -float("inf")], 0)
    .fillna(0)
)

# Step 5: Categorize Sellers
def margin_category(margin):
    if margin >= 80:
        return "High Margin"
    elif margin >= 50:
        return "Medium Margin"
    else:
        return "Low Margin"

seller_margin["margin_category"] = (
    seller_margin["revenue_margin"]
    .apply(margin_category)
)

# Step 6: Sort by Revenue Margin
seller_margin = seller_margin.sort_values(
    by="revenue_margin",
    ascending=False
)

# Step 7: Display Summary
print("\nSeller Revenue Margin Analysis")
print("--------------------------------")

print("\nTotal Sellers:")
print(len(seller_margin))

print("\nAverage Revenue Margin:")
print(round(seller_margin["revenue_margin"].mean(), 2))

print("\nHighest Revenue Margin:")
print(round(seller_margin["revenue_margin"].max(), 2))

print("\nLowest Revenue Margin:")
print(round(seller_margin["revenue_margin"].min(), 2))

# Step 8: Category Counts
print("\nMargin Category Distribution:")
print(
    seller_margin["margin_category"]
    .value_counts()
)

# Step 9: Top 10 Sellers
print("\nTop 10 Sellers by Revenue Margin:")
print(
    seller_margin[
        [
            "seller_id",
            "total_orders",
            "total_revenue",
            "total_freight",
            "net_revenue",
            "revenue_margin",
            "margin_category"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

# Step 10: Close Connection
connection.close()

# ============================================================
# Completion Message
# ============================================================

print(
    "\nStep 64 Seller Revenue Margin Analysis "
    "completed successfully."
)