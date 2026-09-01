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
# Step 1: Seller Revenue Performance
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

seller_performance = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Revenue Performance:")
print(seller_performance.head(10))


# ---------------------------------------------------------
# Step 2: Revenue Performance Score
# ---------------------------------------------------------

average_revenue = seller_performance[
    "total_revenue"
].mean()

average_revenue_per_order = seller_performance[
    "revenue_per_order"
].mean()

average_revenue_per_customer = seller_performance[
    "revenue_per_customer"
].mean()


seller_performance["revenue_score"] = (
    seller_performance["total_revenue"]
    / average_revenue
)

seller_performance["order_value_score"] = (
    seller_performance["revenue_per_order"]
    / average_revenue_per_order
)

seller_performance["customer_value_score"] = (
    seller_performance["revenue_per_customer"]
    / average_revenue_per_customer
)


# ---------------------------------------------------------
# Step 3: Overall Performance Score
# ---------------------------------------------------------

seller_performance["performance_score"] = (
    seller_performance["revenue_score"] * 0.50
    + seller_performance["order_value_score"] * 0.25
    + seller_performance["customer_value_score"] * 0.25
)

seller_performance["performance_score"] = (
    seller_performance["performance_score"].round(2)
)


# ---------------------------------------------------------
# Step 4: Performance Classification
# ---------------------------------------------------------

seller_performance["performance_level"] = pd.cut(
    seller_performance["performance_score"],
    bins=[
        -float("inf"),
        0.75,
        1.50,
        float("inf")
    ],
    labels=[
        "Low Performance",
        "Medium Performance",
        "High Performance"
    ]
)


# ---------------------------------------------------------
# Step 5: Top Performing Sellers
# ---------------------------------------------------------

top_performing_sellers = (
    seller_performance
    .sort_values(
        "performance_score",
        ascending=False
    )
    .head(10)
)

print("\nTop 10 Sellers by Revenue Performance:")

print(
    top_performing_sellers[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_revenue",
            "revenue_per_order",
            "revenue_per_customer",
            "performance_score",
            "performance_level"
        ]
    ]
)


# ---------------------------------------------------------
# Step 6: Performance Summary
# ---------------------------------------------------------

high_performance = seller_performance[
    seller_performance["performance_level"]
    == "High Performance"
]

medium_performance = seller_performance[
    seller_performance["performance_level"]
    == "Medium Performance"
]

low_performance = seller_performance[
    seller_performance["performance_level"]
    == "Low Performance"
]


print("\nSeller Revenue Performance Summary:")

print(
    "\nHigh Performance Sellers:"
)

print(
    len(high_performance)
)


print(
    "\nMedium Performance Sellers:"
)

print(
    len(medium_performance)
)


print(
    "\nLow Performance Sellers:"
)

print(
    len(low_performance)
)


# ---------------------------------------------------------
# Step 7: Highest Performance Seller
# ---------------------------------------------------------

highest_performance_seller = seller_performance.loc[
    seller_performance["performance_score"].idxmax()
]

print(
    "\nHighest Performance Seller:"
)

print(
    highest_performance_seller["seller_id"]
)

print(
    "Performance Score:"
)

print(
    highest_performance_seller["performance_score"]
)

print(
    "Total Revenue:"
)

print(
    highest_performance_seller["total_revenue"]
)


# ---------------------------------------------------------
# Step 8: Average Performance Score
# ---------------------------------------------------------

average_performance_score = seller_performance[
    "performance_score"
].mean()

print(
    "\nAverage Seller Performance Score:"
)

print(
    round(average_performance_score, 2)
)


# ---------------------------------------------------------
# Step 9: Close connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Step 10: Completion Message
# ---------------------------------------------------------

print(
    "\nStep 46 Seller Revenue Performance Analysis "
    "completed successfully."
)