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
# Step 1: Seller Revenue Data
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
"""

seller_consistency = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Revenue Consistency Data:")
print(seller_consistency.head(10))


# ---------------------------------------------------------
# Step 2: Calculate Revenue Metrics
# ---------------------------------------------------------

average_revenue = seller_consistency[
    "total_revenue"
].mean()

median_revenue = seller_consistency[
    "total_revenue"
].median()

revenue_std = seller_consistency[
    "total_revenue"
].std()


print("\nRevenue Consistency Metrics:")

print(
    "Average Seller Revenue:"
)

print(
    round(average_revenue, 2)
)

print(
    "\nMedian Seller Revenue:"
)

print(
    round(median_revenue, 2)
)

print(
    "\nRevenue Standard Deviation:"
)

print(
    round(revenue_std, 2)
)


# ---------------------------------------------------------
# Step 3: Revenue Consistency Score
# ---------------------------------------------------------

seller_consistency["consistency_ratio"] = (
    seller_consistency["total_revenue"]
    / average_revenue
)

seller_consistency["consistency_ratio"] = (
    seller_consistency["consistency_ratio"].round(2)
)


# ---------------------------------------------------------
# Step 4: Seller Consistency Classification
# ---------------------------------------------------------

seller_consistency["consistency_level"] = pd.cut(
    seller_consistency["consistency_ratio"],
    bins=[
        -float("inf"),
        0.50,
        1.50,
        float("inf")
    ],
    labels=[
        "Low Consistency",
        "Medium Consistency",
        "High Consistency"
    ]
)


# ---------------------------------------------------------
# Step 5: Top Consistent Sellers
# ---------------------------------------------------------

top_consistent_sellers = (
    seller_consistency
    .sort_values(
        "total_revenue",
        ascending=False
    )
    .head(10)
)

print("\nTop 10 Sellers by Revenue Consistency:")

print(
    top_consistent_sellers[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_revenue",
            "consistency_ratio",
            "consistency_level"
        ]
    ]
)


# ---------------------------------------------------------
# Step 6: Consistency Summary
# ---------------------------------------------------------

high_consistency = seller_consistency[
    seller_consistency["consistency_level"]
    == "High Consistency"
]

medium_consistency = seller_consistency[
    seller_consistency["consistency_level"]
    == "Medium Consistency"
]

low_consistency = seller_consistency[
    seller_consistency["consistency_level"]
    == "Low Consistency"
]


print("\nSeller Consistency Summary:")

print(
    "\nHigh Consistency Sellers:"
)

print(
    len(high_consistency)
)

print(
    "\nMedium Consistency Sellers:"
)

print(
    len(medium_consistency)
)

print(
    "\nLow Consistency Sellers:"
)

print(
    len(low_consistency)
)


# ---------------------------------------------------------
# Step 7: Highest Revenue Seller
# ---------------------------------------------------------

highest_revenue_seller = seller_consistency.loc[
    seller_consistency["total_revenue"].idxmax()
]

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
    "Consistency Ratio:"
)

print(
    highest_revenue_seller["consistency_ratio"]
)


# ---------------------------------------------------------
# Step 8: Lowest Revenue Seller
# ---------------------------------------------------------

lowest_revenue_seller = seller_consistency.loc[
    seller_consistency["total_revenue"].idxmin()
]

print(
    "\nLowest Revenue Seller:"
)

print(
    lowest_revenue_seller["seller_id"]
)

print(
    "Revenue:"
)

print(
    lowest_revenue_seller["total_revenue"]
)


# ---------------------------------------------------------
# Step 9: Close connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Step 10: Completion Message
# ---------------------------------------------------------

print(
    "\nStep 45 Seller Revenue Consistency Analysis "
    "completed successfully."
)