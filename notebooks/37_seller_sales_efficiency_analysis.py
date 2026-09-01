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
# Step 1: Seller Sales Efficiency
# ---------------------------------------------------------

query = """
SELECT
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    ROUND(SUM(oi.price), 2) AS total_sales,
    ROUND(
        SUM(oi.price) / NULLIF(COUNT(DISTINCT oi.order_id), 0),
        2
    ) AS sales_per_order,
    ROUND(
        SUM(oi.price) / NULLIF(COUNT(DISTINCT o.customer_id), 0),
        2
    ) AS sales_per_customer
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
GROUP BY oi.seller_id
ORDER BY sales_per_order DESC
"""

seller_efficiency = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Sales Efficiency:")
print(seller_efficiency.head(10))


# ---------------------------------------------------------
# Step 2: Average Sales per Order
# ---------------------------------------------------------

average_sales_per_order = seller_efficiency[
    "sales_per_order"
].mean()

print("\nAverage Sales per Order:")
print(round(average_sales_per_order, 2))


# ---------------------------------------------------------
# Step 3: Average Sales per Customer
# ---------------------------------------------------------

average_sales_per_customer = seller_efficiency[
    "sales_per_customer"
].mean()

print("\nAverage Sales per Customer:")
print(round(average_sales_per_customer, 2))


# ---------------------------------------------------------
# Step 4: Top Sellers by Sales Efficiency
# ---------------------------------------------------------

top_efficient_sellers = (
    seller_efficiency
    .sort_values(
        "sales_per_order",
        ascending=False
    )
    .head(10)
)

print("\nTop 10 Sellers by Sales Efficiency:")
print(
    top_efficient_sellers[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "sales_per_order",
            "sales_per_customer"
        ]
    ]
)


# ---------------------------------------------------------
# Step 5: Highest Sales per Customer
# ---------------------------------------------------------

top_customer_value_sellers = (
    seller_efficiency
    .sort_values(
        "sales_per_customer",
        ascending=False
    )
    .head(10)
)

print("\nTop 10 Sellers by Sales per Customer:")
print(
    top_customer_value_sellers[
        [
            "seller_id",
            "unique_customers",
            "total_sales",
            "sales_per_customer"
        ]
    ]
)


# ---------------------------------------------------------
# Step 6: Seller Efficiency Summary
# ---------------------------------------------------------

print("\nSeller Efficiency Summary:")

print(
    "Highest Sales per Order:"
)

print(
    seller_efficiency[
        "sales_per_order"
    ].max()
)

print(
    "\nHighest Sales per Customer:"
)

print(
    seller_efficiency[
        "sales_per_customer"
    ].max()
)


# ---------------------------------------------------------
# Step 7: Close connection
# ---------------------------------------------------------

connection.close()


print(
    "\nStep 37 Seller Sales Efficiency Analysis "
    "completed successfully."
)