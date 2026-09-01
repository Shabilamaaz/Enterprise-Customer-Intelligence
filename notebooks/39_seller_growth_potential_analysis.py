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
# Step 1: Seller Growth Potential Analysis
# ---------------------------------------------------------

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

seller_growth = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Growth Potential Analysis:")
print(seller_growth.head(10))


# ---------------------------------------------------------
# Step 2: Calculate Average Metrics
# ---------------------------------------------------------

average_sales = seller_growth[
    "total_sales"
].mean()

average_orders = seller_growth[
    "total_orders"
].mean()

average_customers = seller_growth[
    "unique_customers"
].mean()


# ---------------------------------------------------------
# Step 3: Calculate Growth Potential Score
# ---------------------------------------------------------

def calculate_growth_score(row):

    score = 0

    # Sales potential
    if row["total_sales"] >= average_sales:
        score += 1

    # Order potential
    if row["total_orders"] >= average_orders:
        score += 1

    # Customer potential
    if row["unique_customers"] >= average_customers:
        score += 1

    return score


seller_growth["growth_score"] = seller_growth.apply(
    calculate_growth_score,
    axis=1
)


# ---------------------------------------------------------
# Step 4: Assign Growth Potential Level
# ---------------------------------------------------------

def growth_level(score):

    if score == 3:
        return "High Growth Potential"

    elif score == 2:
        return "Medium Growth Potential"

    else:
        return "Low Growth Potential"


seller_growth["growth_potential"] = seller_growth[
    "growth_score"
].apply(growth_level)


# ---------------------------------------------------------
# Step 5: Rank Sellers by Growth Potential
# ---------------------------------------------------------

seller_growth = seller_growth.sort_values(
    [
        "growth_score",
        "total_sales"
    ],
    ascending=[
        False,
        False
    ]
)


print("\nSeller Growth Potential Ranking:")

print(
    seller_growth[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "sales_per_order",
            "sales_per_customer",
            "growth_score",
            "growth_potential"
        ]
    ].head(10)
)


# ---------------------------------------------------------
# Step 6: High Growth Potential Sellers
# ---------------------------------------------------------

high_growth_sellers = seller_growth[
    seller_growth["growth_potential"] ==
    "High Growth Potential"
]


print("\nHigh Growth Potential Sellers:")

print(
    high_growth_sellers[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "growth_score",
            "growth_potential"
        ]
    ].head(10)
)


# ---------------------------------------------------------
# Step 7: Medium Growth Potential Sellers
# ---------------------------------------------------------

medium_growth_sellers = seller_growth[
    seller_growth["growth_potential"] ==
    "Medium Growth Potential"
]


print("\nMedium Growth Potential Sellers:")

print(
    medium_growth_sellers[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "growth_score",
            "growth_potential"
        ]
    ].head(10)
)


# ---------------------------------------------------------
# Step 8: Growth Summary
# ---------------------------------------------------------

print("\nSeller Growth Potential Summary:")

print(
    "Total Sellers:"
)

print(
    seller_growth["seller_id"].nunique()
)


print(
    "\nHigh Growth Potential Sellers:"
)

print(
    len(high_growth_sellers)
)


print(
    "\nMedium Growth Potential Sellers:"
)

print(
    len(medium_growth_sellers)
)


print(
    "\nLow Growth Potential Sellers:"
)

print(
    len(
        seller_growth[
            seller_growth["growth_potential"] ==
            "Low Growth Potential"
        ]
    )
)


print(
    "\nHighest Growth Score:"
)

print(
    seller_growth["growth_score"].max()
)


# ---------------------------------------------------------
# Step 9: Close connection
# ---------------------------------------------------------

connection.close()


print(
    "\nStep 39 Seller Growth Potential Analysis "
    "completed successfully."
)