import sqlite3
import pandas as pd
import os


# =========================================================
# Database Path
# =========================================================

db_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "database",
    "customer_intelligence.db"
)

print("Database path:")
print(db_path)

print("\nDatabase exists:")
print(os.path.exists(db_path))


# =========================================================
# Connect to Database
# =========================================================

connection = sqlite3.connect(db_path)


# =========================================================
# Step 1: Seller Revenue
# =========================================================

query = """
SELECT
    oi.seller_id,
    ROUND(SUM(oi.price), 2) AS total_sales,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
GROUP BY oi.seller_id
ORDER BY total_sales DESC
"""

seller_revenue = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Revenue:")
print(seller_revenue.head(10))


# =========================================================
# Step 2: Total Revenue
# =========================================================

total_revenue = seller_revenue[
    "total_sales"
].sum()

print("\nTotal Revenue:")
print(round(total_revenue, 2))


# =========================================================
# Step 3: Revenue Contribution
# =========================================================

seller_revenue["revenue_percentage"] = (
    seller_revenue["total_sales"]
    / total_revenue
    * 100
).round(2)


# =========================================================
# Step 4: Cumulative Revenue
# =========================================================

seller_revenue["cumulative_revenue"] = (
    seller_revenue["total_sales"]
    .cumsum()
)


seller_revenue["cumulative_revenue_percentage"] = (
    seller_revenue["revenue_percentage"]
    .cumsum()
).round(2)


# =========================================================
# Step 5: Identify Sellers Required for 50% Revenue
# =========================================================

sellers_for_50_percent = (
    seller_revenue[
        seller_revenue[
            "cumulative_revenue_percentage"
        ] >= 50
    ]
    .index[0]
    + 1
)


# =========================================================
# Step 6: Identify Sellers Required for 80% Revenue
# =========================================================

sellers_for_80_percent = (
    seller_revenue[
        seller_revenue[
            "cumulative_revenue_percentage"
        ] >= 80
    ]
    .index[0]
    + 1
)


# =========================================================
# Step 7: Identify Sellers Required for 90% Revenue
# =========================================================

sellers_for_90_percent = (
    seller_revenue[
        seller_revenue[
            "cumulative_revenue_percentage"
        ] >= 90
    ]
    .index[0]
    + 1
)


# =========================================================
# Step 8: Pareto Analysis
# =========================================================

total_sellers = len(seller_revenue)


seller_revenue["seller_percentage"] = (
    (seller_revenue.index + 1)
    / total_sellers
    * 100
).round(2)


# =========================================================
# Step 9: Revenue Dependency Level
# =========================================================

seller_revenue["dependency_level"] = (
    seller_revenue[
        "cumulative_revenue_percentage"
    ].apply(
        lambda x:
            "Core Revenue"
            if x <= 50
            else
            "Major Revenue"
            if x <= 80
            else
            "Long Tail"
    )
)


# =========================================================
# Step 10: Top 10 Dependency Analysis
# =========================================================

print("\nTop 10 Sellers Revenue Dependency:")

print(
    seller_revenue[
        [
            "seller_id",
            "total_sales",
            "revenue_percentage",
            "cumulative_revenue_percentage"
        ]
    ].head(10)
)


# =========================================================
# Step 11: Revenue Milestones
# =========================================================

print("\nRevenue Dependency Summary:")

print(
    "Total Sellers:"
)

print(
    total_sellers
)


print(
    "\nSellers Required for 50% Revenue:"
)

print(
    sellers_for_50_percent
)


print(
    "\nSellers Required for 80% Revenue:"
)

print(
    sellers_for_80_percent
)


print(
    "\nSellers Required for 90% Revenue:"
)

print(
    sellers_for_90_percent
)


# =========================================================
# Step 12: Dependency Percentages
# =========================================================

percentage_sellers_for_50 = (
    sellers_for_50_percent
    / total_sellers
    * 100
)


percentage_sellers_for_80 = (
    sellers_for_80_percent
    / total_sellers
    * 100
)


percentage_sellers_for_90 = (
    sellers_for_90_percent
    / total_sellers
    * 100
)


print(
    "\nPercentage of Sellers Generating 50% Revenue:"
)

print(
    round(percentage_sellers_for_50, 2)
)


print(
    "\nPercentage of Sellers Generating 80% Revenue:"
)

print(
    round(percentage_sellers_for_80, 2)
)


print(
    "\nPercentage of Sellers Generating 90% Revenue:"
)

print(
    round(percentage_sellers_for_90, 2)
)


# =========================================================
# Step 13: Highest Revenue Seller
# =========================================================

highest_revenue_seller = seller_revenue.iloc[0]


print(
    "\nHighest Revenue Seller:"
)

print(
    highest_revenue_seller[
        "seller_id"
    ]
)


print(
    "Revenue:"
)

print(
    highest_revenue_seller[
        "total_sales"
    ]
)


print(
    "Revenue Contribution:"
)

print(
    highest_revenue_seller[
        "revenue_percentage"
    ]
)


# =========================================================
# Step 14: Close Connection
# =========================================================

connection.close()


# =========================================================
# Completion Message
# =========================================================

print(
    "\nStep 43 Seller Revenue Dependency Analysis "
    "completed successfully."
)