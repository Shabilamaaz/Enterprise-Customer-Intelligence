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
# Step 1: Seller Base Performance
# =========================================================

query = """
SELECT
    oi.seller_id,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    COUNT(DISTINCT o.customer_id) AS unique_customers,

    ROUND(SUM(oi.price), 2) AS total_sales,

    ROUND(
        SUM(oi.price) /
        NULLIF(COUNT(DISTINCT oi.order_id), 0),
        2
    ) AS sales_per_order,

    ROUND(
        SUM(oi.price) /
        NULLIF(COUNT(DISTINCT o.customer_id), 0),
        2
    ) AS sales_per_customer

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

GROUP BY oi.seller_id
"""


seller_data = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Base Performance:")
print(seller_data.head(10))


# =========================================================
# Step 2: Calculate Performance Scores
# =========================================================

seller_data["sales_score"] = (
    seller_data["total_sales"]
    >= seller_data["total_sales"].median()
).astype(int)

seller_data["order_score"] = (
    seller_data["total_orders"]
    >= seller_data["total_orders"].median()
).astype(int)

seller_data["customer_score"] = (
    seller_data["unique_customers"]
    >= seller_data["unique_customers"].median()
).astype(int)

seller_data["efficiency_score"] = (
    seller_data["sales_per_order"]
    >= seller_data["sales_per_order"].median()
).astype(int)


# =========================================================
# Step 3: Calculate Seller Priority Score
# =========================================================

seller_data["priority_score"] = (
    seller_data["sales_score"]
    + seller_data["order_score"]
    + seller_data["customer_score"]
    + seller_data["efficiency_score"]
)


# =========================================================
# Step 4: Seller Priority Classification
# =========================================================

seller_data["priority_level"] = seller_data[
    "priority_score"
].apply(
    lambda score:
        "High Priority"
        if score >= 3
        else
        "Medium Priority"
        if score == 2
        else
        "Low Priority"
)


# =========================================================
# Step 5: Sort Sellers by Priority
# =========================================================

seller_priority = seller_data.sort_values(
    by=[
        "priority_score",
        "total_sales"
    ],
    ascending=[
        False,
        False
    ]
)


print("\nSeller Priority Analysis:")

print(
    seller_priority[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "sales_per_order",
            "sales_per_customer",
            "priority_score",
            "priority_level"
        ]
    ].head(10)
)


# =========================================================
# Step 6: High Priority Sellers
# =========================================================

high_priority_sellers = seller_priority[
    seller_priority["priority_level"]
    == "High Priority"
]


print("\nHigh Priority Sellers:")

print(
    len(high_priority_sellers)
)


# =========================================================
# Step 7: Medium Priority Sellers
# =========================================================

medium_priority_sellers = seller_priority[
    seller_priority["priority_level"]
    == "Medium Priority"
]


print("\nMedium Priority Sellers:")

print(
    len(medium_priority_sellers)
)


# =========================================================
# Step 8: Low Priority Sellers
# =========================================================

low_priority_sellers = seller_priority[
    seller_priority["priority_level"]
    == "Low Priority"
]


print("\nLow Priority Sellers:")

print(
    len(low_priority_sellers)
)


# =========================================================
# Step 9: Top Priority Sellers
# =========================================================

top_priority_sellers = seller_priority.head(10)


print("\nTop 10 Priority Sellers:")

print(
    top_priority_sellers[
        [
            "seller_id",
            "total_sales",
            "total_orders",
            "unique_customers",
            "priority_score",
            "priority_level"
        ]
    ]
)


# =========================================================
# Step 10: Priority Summary
# =========================================================

print("\nSeller Priority Summary:")

print(
    "Highest Priority Score:"
)

print(
    seller_priority[
        "priority_score"
    ].max()
)


print("\nHigh Priority Sellers:")

print(
    len(high_priority_sellers)
)


print("\nMedium Priority Sellers:")

print(
    len(medium_priority_sellers)
)


print("\nLow Priority Sellers:")

print(
    len(low_priority_sellers)
)


# =========================================================
# Step 11: Highest Sales Seller
# =========================================================

highest_sales_seller = seller_priority.loc[
    seller_priority["total_sales"].idxmax()
]


print("\nHighest Sales Seller:")

print(
    highest_sales_seller[
        "seller_id"
    ]
)


# =========================================================
# Step 12: Highest Efficiency Seller
# =========================================================

highest_efficiency_seller = seller_priority.loc[
    seller_priority["sales_per_order"].idxmax()
]


print("\nHighest Efficiency Seller:")

print(
    highest_efficiency_seller[
        "seller_id"
    ]
)


# =========================================================
# Step 13: Close Connection
# =========================================================

connection.close()


# =========================================================
# Completion Message
# =========================================================

print(
    "\nStep 41 Seller Priority Analysis "
    "completed successfully."
)