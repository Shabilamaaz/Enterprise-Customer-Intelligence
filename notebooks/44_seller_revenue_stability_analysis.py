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
# Step 1: Seller Revenue Analysis
# ---------------------------------------------------------

query = """
SELECT
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(
        SUM(oi.price) / NULLIF(COUNT(DISTINCT oi.order_id), 0),
        2
    ) AS revenue_per_order,
    ROUND(
        SUM(oi.price) / NULLIF(COUNT(DISTINCT o.customer_id), 0),
        2
    ) AS revenue_per_customer
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
GROUP BY oi.seller_id
ORDER BY total_revenue DESC
"""

seller_revenue = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Revenue Stability Data:")
print(seller_revenue.head(10))


# ---------------------------------------------------------
# Step 2: Calculate Revenue Share
# ---------------------------------------------------------

total_market_revenue = seller_revenue[
    "total_revenue"
].sum()

seller_revenue["revenue_share"] = (
    seller_revenue["total_revenue"]
    / total_market_revenue
) * 100

seller_revenue["revenue_share"] = seller_revenue[
    "revenue_share"
].round(2)


print("\nSeller Revenue Share:")
print(
    seller_revenue[
        [
            "seller_id",
            "total_revenue",
            "revenue_share"
        ]
    ].head(10)
)


# ---------------------------------------------------------
# Step 3: Revenue Stability Classification
# ---------------------------------------------------------

seller_revenue["stability_level"] = pd.cut(
    seller_revenue["revenue_share"],
    bins=[
        -float("inf"),
        0.05,
        0.20,
        float("inf")
    ],
    labels=[
        "Low Stability",
        "Medium Stability",
        "High Stability"
    ]
)


# ---------------------------------------------------------
# Step 4: Top Stable Sellers
# ---------------------------------------------------------

top_stable_sellers = (
    seller_revenue
    .sort_values(
        "total_revenue",
        ascending=False
    )
    .head(10)
)

print("\nTop 10 Sellers by Revenue Stability:")
print(
    top_stable_sellers[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_revenue",
            "revenue_share",
            "stability_level"
        ]
    ]
)


# ---------------------------------------------------------
# Step 5: Revenue Concentration Risk
# ---------------------------------------------------------

high_dependency_sellers = seller_revenue[
    seller_revenue["revenue_share"] >= 0.20
]

medium_dependency_sellers = seller_revenue[
    (
        seller_revenue["revenue_share"] >= 0.05
    )
    &
    (
        seller_revenue["revenue_share"] < 0.20
    )
]

low_dependency_sellers = seller_revenue[
    seller_revenue["revenue_share"] < 0.05
]


print("\nRevenue Stability Summary:")

print(
    "\nHigh Stability Sellers:"
)

print(
    len(high_dependency_sellers)
)


print(
    "\nMedium Stability Sellers:"
)

print(
    len(medium_dependency_sellers)
)


print(
    "\nLow Stability Sellers:"
)

print(
    len(low_dependency_sellers)
)


# ---------------------------------------------------------
# Step 6: Highest Revenue Share Seller
# ---------------------------------------------------------

highest_revenue_seller = seller_revenue.iloc[0]

print(
    "\nHighest Revenue Seller:"
)

print(
    highest_revenue_seller["seller_id"]
)

print(
    "Revenue:"
)

print(
    highest_revenue_seller["total_revenue"]
)

print(
    "Revenue Share (%):"
)

print(
    highest_revenue_seller["revenue_share"]
)


# ---------------------------------------------------------
# Step 7: Average Revenue Share
# ---------------------------------------------------------

average_revenue_share = seller_revenue[
    "revenue_share"
].mean()

print(
    "\nAverage Seller Revenue Share:"
)

print(
    round(average_revenue_share, 4)
)


# ---------------------------------------------------------
# Step 8: Close connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Step 9: Completion Message
# ---------------------------------------------------------

print(
    "\nStep 44 Seller Revenue Stability Analysis "
    "completed successfully."
)