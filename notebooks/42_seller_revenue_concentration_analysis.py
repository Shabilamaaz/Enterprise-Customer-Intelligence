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
# Step 1: Calculate Seller Revenue
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


print("\nSeller Revenue Analysis:")
print(seller_revenue.head(10))


# =========================================================
# Step 2: Calculate Total Revenue
# =========================================================

total_revenue = seller_revenue[
    "total_sales"
].sum()

print("\nTotal Seller Revenue:")
print(round(total_revenue, 2))


# =========================================================
# Step 3: Revenue Contribution Percentage
# =========================================================

seller_revenue["revenue_contribution_percentage"] = (
    seller_revenue["total_sales"]
    / total_revenue
    * 100
).round(2)


# =========================================================
# Step 4: Cumulative Revenue Contribution
# =========================================================

seller_revenue = seller_revenue.sort_values(
    "total_sales",
    ascending=False
)

seller_revenue["cumulative_revenue_percentage"] = (
    seller_revenue[
        "revenue_contribution_percentage"
    ].cumsum()
).round(2)


# =========================================================
# Step 5: Seller Revenue Concentration
# =========================================================

seller_revenue["concentration_level"] = (
    seller_revenue[
        "cumulative_revenue_percentage"
    ].apply(
        lambda x:
            "Top 20%"
            if x <= 20
            else
            "Top 50%"
            if x <= 50
            else
            "Top 80%"
            if x <= 80
            else
            "Remaining"
    )
)


# =========================================================
# Step 6: Display Top Sellers
# =========================================================

print("\nTop 10 Sellers by Revenue Contribution:")

print(
    seller_revenue[
        [
            "seller_id",
            "total_sales",
            "total_orders",
            "unique_customers",
            "revenue_contribution_percentage",
            "cumulative_revenue_percentage"
        ]
    ].head(10)
)


# =========================================================
# Step 7: Top 10 Seller Revenue Share
# =========================================================

top_10_revenue = seller_revenue.head(10)[
    "total_sales"
].sum()

top_10_revenue_percentage = (
    top_10_revenue
    / total_revenue
    * 100
)


print("\nTop 10 Seller Revenue Share:")

print(
    round(top_10_revenue_percentage, 2)
)


# =========================================================
# Step 8: Top 20 Seller Revenue Share
# =========================================================

top_20_revenue = seller_revenue.head(20)[
    "total_sales"
].sum()

top_20_revenue_percentage = (
    top_20_revenue
    / total_revenue
    * 100
)


print("\nTop 20 Seller Revenue Share:")

print(
    round(top_20_revenue_percentage, 2)
)


# =========================================================
# Step 9: Top 50 Seller Revenue Share
# =========================================================

top_50_revenue = seller_revenue.head(50)[
    "total_sales"
].sum()

top_50_revenue_percentage = (
    top_50_revenue
    / total_revenue
    * 100
)


print("\nTop 50 Seller Revenue Share:")

print(
    round(top_50_revenue_percentage, 2)
)


# =========================================================
# Step 10: Highest Revenue Seller
# =========================================================

highest_revenue_seller = seller_revenue.iloc[0]


print("\nHighest Revenue Seller:")

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
        "revenue_contribution_percentage"
    ]
)


# =========================================================
# Step 11: Revenue Concentration Summary
# =========================================================

print("\nSeller Revenue Concentration Summary:")

print(
    "Number of Sellers:"
)

print(
    len(seller_revenue)
)

print(
    "\nTop 10 Revenue Contribution:"
)

print(
    round(top_10_revenue_percentage, 2)
)

print(
    "\nTop 20 Revenue Contribution:"
)

print(
    round(top_20_revenue_percentage, 2)
)

print(
    "\nTop 50 Revenue Contribution:"
)

print(
    round(top_50_revenue_percentage, 2)
)


# =========================================================
# Step 12: Close Connection
# =========================================================

connection.close()


# =========================================================
# Completion Message
# =========================================================

print(
    "\nStep 42 Seller Revenue Concentration Analysis "
    "completed successfully."
)