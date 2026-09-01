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
# Step 1: Seller Total Revenue
# ---------------------------------------------------------

query = """
SELECT
    oi.seller_id,
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
WHERE o.order_purchase_timestamp IS NOT NULL
GROUP BY
    oi.seller_id
ORDER BY
    total_revenue DESC
"""

seller_revenue = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Total Revenue:")
print(
    seller_revenue.head(10)
)


# ---------------------------------------------------------
# Step 2: Total Marketplace Revenue
# ---------------------------------------------------------

total_marketplace_revenue = (
    seller_revenue["total_revenue"]
    .sum()
)


print("\nTotal Marketplace Revenue:")
print(
    round(
        total_marketplace_revenue,
        2
    )
)


# ---------------------------------------------------------
# Step 3: Seller Revenue Share
# ---------------------------------------------------------

seller_revenue["revenue_share_percentage"] = (
    seller_revenue["total_revenue"]
    /
    total_marketplace_revenue
    * 100
)


seller_revenue["revenue_share_percentage"] = (
    seller_revenue["revenue_share_percentage"]
    .round(2)
)


# ---------------------------------------------------------
# Step 4: Cumulative Revenue Share
# ---------------------------------------------------------

seller_revenue["cumulative_revenue_share"] = (
    seller_revenue["revenue_share_percentage"]
    .cumsum()
)


seller_revenue["cumulative_revenue_share"] = (
    seller_revenue["cumulative_revenue_share"]
    .round(2)
)


# ---------------------------------------------------------
# Step 5: Revenue Concentration Classification
# ---------------------------------------------------------

def classify_concentration(row):

    if row["revenue_share_percentage"] >= 1.0:
        return "High Concentration"

    elif row["revenue_share_percentage"] >= 0.25:
        return "Medium Concentration"

    else:
        return "Low Concentration"


seller_revenue["concentration_category"] = (
    seller_revenue.apply(
        classify_concentration,
        axis=1
    )
)


# ---------------------------------------------------------
# Step 6: Top 10 Revenue Sellers
# ---------------------------------------------------------

top_revenue_sellers = (
    seller_revenue
    .sort_values(
        "total_revenue",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Sellers by Revenue:")

print(
    top_revenue_sellers[
        [
            "seller_id",
            "total_revenue",
            "revenue_share_percentage",
            "cumulative_revenue_share",
            "concentration_category"
        ]
    ]
)


# ---------------------------------------------------------
# Step 7: Top 10 Seller Revenue Concentration
# ---------------------------------------------------------

top_10_revenue_share = (
    top_revenue_sellers[
        "revenue_share_percentage"
    ].sum()
)


print("\nTop 10 Sellers Revenue Share:")

print(
    round(
        top_10_revenue_share,
        2
    )
)


# ---------------------------------------------------------
# Step 8: Top 20 Seller Revenue Concentration
# ---------------------------------------------------------

top_20_revenue_share = (
    seller_revenue
    .head(20)[
        "revenue_share_percentage"
    ]
    .sum()
)


print("\nTop 20 Sellers Revenue Share:")

print(
    round(
        top_20_revenue_share,
        2
    )
)


# ---------------------------------------------------------
# Step 9: High Concentration Sellers
# ---------------------------------------------------------

high_concentration_sellers = seller_revenue[
    seller_revenue["concentration_category"]
    == "High Concentration"
]


print("\nHigh Concentration Sellers:")

print(
    len(
        high_concentration_sellers
    )
)


# ---------------------------------------------------------
# Step 10: Medium Concentration Sellers
# ---------------------------------------------------------

medium_concentration_sellers = seller_revenue[
    seller_revenue["concentration_category"]
    == "Medium Concentration"
]


print("\nMedium Concentration Sellers:")

print(
    len(
        medium_concentration_sellers
    )
)


# ---------------------------------------------------------
# Step 11: Low Concentration Sellers
# ---------------------------------------------------------

low_concentration_sellers = seller_revenue[
    seller_revenue["concentration_category"]
    == "Low Concentration"
]


print("\nLow Concentration Sellers:")

print(
    len(
        low_concentration_sellers
    )
)


# ---------------------------------------------------------
# Step 12: Highest Revenue Seller
# ---------------------------------------------------------

highest_revenue_seller = (
    seller_revenue
    .sort_values(
        "total_revenue",
        ascending=False
    )
    .iloc[0]
)


print("\nHighest Revenue Seller:")

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
    "Revenue Share:"
)

print(
    highest_revenue_seller[
        "revenue_share_percentage"
    ]
)


# ---------------------------------------------------------
# Step 13: Revenue Concentration Index
# ---------------------------------------------------------

seller_revenue["revenue_share_decimal"] = (
    seller_revenue["revenue_share_percentage"]
    / 100
)


seller_revenue["squared_share"] = (
    seller_revenue["revenue_share_decimal"]
    ** 2
)


revenue_concentration_index = (
    seller_revenue["squared_share"]
    .sum()
)


print("\nRevenue Concentration Index:")

print(
    round(
        revenue_concentration_index,
        4
    )
)


# ---------------------------------------------------------
# Step 14: Revenue Concentration Summary
# ---------------------------------------------------------

print("\nSeller Revenue Concentration Summary:")

print(
    "Total Sellers:"
)

print(
    len(
        seller_revenue
    )
)

print(
    "\nHigh Concentration Sellers:"
)

print(
    len(
        high_concentration_sellers
    )
)

print(
    "\nMedium Concentration Sellers:"
)

print(
    len(
        medium_concentration_sellers
    )
)

print(
    "\nLow Concentration Sellers:"
)

print(
    len(
        low_concentration_sellers
    )
)

print(
    "\nTop 10 Revenue Share:"
)

print(
    round(
        top_10_revenue_share,
        2
    )
)

print(
    "\nRevenue Concentration Index:"
)

print(
    round(
        revenue_concentration_index,
        4
    )
)


# ---------------------------------------------------------
# Step 15: Close Connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Completion Message
# ---------------------------------------------------------

print(
    "\nStep 53 Seller Revenue Concentration Analysis "
    "completed successfully."
)