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


# Connect to database
connection = sqlite3.connect(db_path)


# ---------------------------------------------------------
# Step 1: Monthly Seller Revenue
# ---------------------------------------------------------

query = """
SELECT
    oi.seller_id,
    strftime('%Y-%m', o.order_purchase_timestamp) AS sales_month,
    ROUND(SUM(oi.price), 2) AS monthly_revenue,
    COUNT(DISTINCT oi.order_id) AS monthly_orders
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
WHERE o.order_purchase_timestamp IS NOT NULL
GROUP BY
    oi.seller_id,
    sales_month
ORDER BY
    oi.seller_id,
    sales_month
"""

seller_monthly_revenue = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Monthly Revenue:")
print(seller_monthly_revenue.head(10))


# ---------------------------------------------------------
# Step 2: Total Revenue by Seller
# ---------------------------------------------------------

seller_revenue = (
    seller_monthly_revenue
    .groupby("seller_id", as_index=False)
    .agg(
        total_revenue=("monthly_revenue", "sum"),
        total_orders=("monthly_orders", "sum"),
        active_months=("sales_month", "nunique")
    )
)


print("\nSeller Revenue Summary:")
print(seller_revenue.head(10))


# ---------------------------------------------------------
# Step 3: Average Monthly Revenue
# ---------------------------------------------------------

seller_revenue["average_monthly_revenue"] = (
    seller_revenue["total_revenue"] /
    seller_revenue["active_months"]
).round(2)


print("\nAverage Monthly Revenue:")
print(
    seller_revenue[
        [
            "seller_id",
            "total_revenue",
            "active_months",
            "average_monthly_revenue"
        ]
    ].head(10)
)


# ---------------------------------------------------------
# Step 4: Top Sellers by Monthly Revenue
# ---------------------------------------------------------

top_monthly_revenue_sellers = (
    seller_revenue
    .sort_values(
        "average_monthly_revenue",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Sellers by Average Monthly Revenue:")

print(
    top_monthly_revenue_sellers[
        [
            "seller_id",
            "total_revenue",
            "active_months",
            "average_monthly_revenue"
        ]
    ]
)


# ---------------------------------------------------------
# Step 5: Most Consistent Sellers
# ---------------------------------------------------------

consistent_sellers = (
    seller_revenue
    .sort_values(
        "active_months",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Sellers by Active Months:")

print(
    consistent_sellers[
        [
            "seller_id",
            "active_months",
            "total_revenue",
            "average_monthly_revenue"
        ]
    ]
)


# ---------------------------------------------------------
# Step 6: Overall Revenue Trend
# ---------------------------------------------------------

monthly_overall_revenue = (
    seller_monthly_revenue
    .groupby("sales_month", as_index=False)
    .agg(
        total_revenue=("monthly_revenue", "sum"),
        total_orders=("monthly_orders", "sum")
    )
    .sort_values("sales_month")
)


print("\nOverall Monthly Revenue Trend:")
print(monthly_overall_revenue.head(12))


# ---------------------------------------------------------
# Step 7: Highest Revenue Month
# ---------------------------------------------------------

highest_revenue_month = (
    monthly_overall_revenue
    .sort_values(
        "total_revenue",
        ascending=False
    )
    .iloc[0]
)


print("\nHighest Revenue Month:")
print(highest_revenue_month["sales_month"])

print("Revenue:")
print(round(highest_revenue_month["total_revenue"], 2))


# ---------------------------------------------------------
# Step 8: Lowest Revenue Month
# ---------------------------------------------------------

lowest_revenue_month = (
    monthly_overall_revenue
    .sort_values(
        "total_revenue",
        ascending=True
    )
    .iloc[0]
)


print("\nLowest Revenue Month:")
print(lowest_revenue_month["sales_month"])

print("Revenue:")
print(round(lowest_revenue_month["total_revenue"], 2))


# ---------------------------------------------------------
# Step 9: Seller Revenue Trend Summary
# ---------------------------------------------------------

print("\nSeller Revenue Trend Summary:")

print(
    "Number of Sellers:"
)

print(
    seller_revenue["seller_id"].nunique()
)

print(
    "\nAverage Seller Revenue:"
)

print(
    round(
        seller_revenue["total_revenue"].mean(),
        2
    )
)

print(
    "\nHighest Average Monthly Revenue:"
)

print(
    round(
        seller_revenue["average_monthly_revenue"].max(),
        2
    )
)

print(
    "\nHighest Active Months:"
)

print(
    seller_revenue["active_months"].max()
)


# ---------------------------------------------------------
# Step 10: Close connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Completion Message
# ---------------------------------------------------------

print(
    "\nStep 47 Seller Revenue Trend Analysis "
    "completed successfully."
)