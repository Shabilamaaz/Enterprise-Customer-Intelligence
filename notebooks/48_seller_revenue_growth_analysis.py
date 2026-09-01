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
    ROUND(SUM(oi.price), 2) AS monthly_revenue
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
# Step 2: Calculate Previous Month Revenue
# ---------------------------------------------------------

seller_monthly_revenue["previous_month_revenue"] = (
    seller_monthly_revenue
    .groupby("seller_id")["monthly_revenue"]
    .shift(1)
)


print("\nRevenue with Previous Month:")
print(
    seller_monthly_revenue.head(10)
)


# ---------------------------------------------------------
# Step 3: Calculate Revenue Growth
# ---------------------------------------------------------

seller_monthly_revenue["revenue_growth"] = (
    seller_monthly_revenue["monthly_revenue"]
    -
    seller_monthly_revenue["previous_month_revenue"]
)


seller_monthly_revenue["growth_percentage"] = (
    (
        seller_monthly_revenue["revenue_growth"]
        /
        seller_monthly_revenue["previous_month_revenue"]
    )
    * 100
).round(2)


print("\nSeller Revenue Growth:")
print(
    seller_monthly_revenue[
        [
            "seller_id",
            "sales_month",
            "monthly_revenue",
            "previous_month_revenue",
            "revenue_growth",
            "growth_percentage"
        ]
    ].head(15)
)


# ---------------------------------------------------------
# Step 4: Remove First Month Records
# ---------------------------------------------------------

growth_data = seller_monthly_revenue[
    seller_monthly_revenue["previous_month_revenue"].notna()
].copy()


print("\nGrowth Records:")
print(len(growth_data))


# ---------------------------------------------------------
# Step 5: Growing Sellers
# ---------------------------------------------------------

growing_sellers = growth_data[
    growth_data["revenue_growth"] > 0
]


print("\nGrowing Seller Records:")
print(len(growing_sellers))


# ---------------------------------------------------------
# Step 6: Declining Sellers
# ---------------------------------------------------------

declining_sellers = growth_data[
    growth_data["revenue_growth"] < 0
]


print("\nDeclining Seller Records:")
print(len(declining_sellers))


# ---------------------------------------------------------
# Step 7: Top Revenue Growth
# ---------------------------------------------------------

top_growth = (
    growth_data
    .sort_values(
        "growth_percentage",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Sellers by Revenue Growth:")

print(
    top_growth[
        [
            "seller_id",
            "sales_month",
            "previous_month_revenue",
            "monthly_revenue",
            "revenue_growth",
            "growth_percentage"
        ]
    ]
)


# ---------------------------------------------------------
# Step 8: Top Revenue Decline
# ---------------------------------------------------------

top_decline = (
    growth_data
    .sort_values(
        "growth_percentage",
        ascending=True
    )
    .head(10)
)


print("\nTop 10 Sellers by Revenue Decline:")

print(
    top_decline[
        [
            "seller_id",
            "sales_month",
            "previous_month_revenue",
            "monthly_revenue",
            "revenue_growth",
            "growth_percentage"
        ]
    ]
)


# ---------------------------------------------------------
# Step 9: Highest Growth Seller
# ---------------------------------------------------------

highest_growth = (
    growth_data
    .sort_values(
        "growth_percentage",
        ascending=False
    )
    .iloc[0]
)


print("\nHighest Revenue Growth Seller:")

print(
    highest_growth["seller_id"]
)

print(
    "Month:"
)

print(
    highest_growth["sales_month"]
)

print(
    "Growth Percentage:"
)

print(
    highest_growth["growth_percentage"]
)


# ---------------------------------------------------------
# Step 10: Highest Revenue Increase
# ---------------------------------------------------------

highest_revenue_increase = (
    growth_data
    .sort_values(
        "revenue_growth",
        ascending=False
    )
    .iloc[0]
)


print("\nHighest Revenue Increase:")

print(
    highest_revenue_increase["seller_id"]
)

print(
    "Revenue Increase:"
)

print(
    round(
        highest_revenue_increase["revenue_growth"],
        2
    )
)


# ---------------------------------------------------------
# Step 11: Overall Growth Summary
# ---------------------------------------------------------

average_growth_percentage = (
    growth_data["growth_percentage"]
    .replace([float("inf"), -float("inf")], pd.NA)
    .dropna()
    .mean()
)


print("\nSeller Revenue Growth Summary:")

print(
    "Growing Seller Records:"
)

print(
    len(growing_sellers)
)

print(
    "\nDeclining Seller Records:"
)

print(
    len(declining_sellers)
)

print(
    "\nAverage Revenue Growth Percentage:"
)

print(
    round(
        average_growth_percentage,
        2
    )
)


# ---------------------------------------------------------
# Step 12: Growth Rate by Month
# ---------------------------------------------------------

monthly_growth = (
    growth_data
    .groupby("sales_month", as_index=False)
    .agg(
        average_growth_percentage=(
            "growth_percentage",
            "mean"
        ),
        total_revenue_growth=(
            "revenue_growth",
            "sum"
        )
    )
)


monthly_growth["average_growth_percentage"] = (
    monthly_growth[
        "average_growth_percentage"
    ].round(2)
)


print("\nMonthly Revenue Growth:")

print(
    monthly_growth
)


# ---------------------------------------------------------
# Step 13: Close Connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Completion Message
# ---------------------------------------------------------

print(
    "\nStep 48 Seller Revenue Growth Analysis "
    "completed successfully."
)