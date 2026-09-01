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
# Step 1: Seller Performance Data
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

seller_data = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Opportunity Analysis:")
print(seller_data.head(10))


# ---------------------------------------------------------
# Step 2: Calculate Average Performance
# ---------------------------------------------------------

average_sales = seller_data[
    "total_sales"
].mean()

average_orders = seller_data[
    "total_orders"
].mean()

average_customers = seller_data[
    "unique_customers"
].mean()


# ---------------------------------------------------------
# Step 3: Growth Score
# ---------------------------------------------------------

def calculate_growth_score(row):

    score = 0

    if row["total_sales"] >= average_sales:
        score += 1

    if row["total_orders"] >= average_orders:
        score += 1

    if row["unique_customers"] >= average_customers:
        score += 1

    return score


seller_data["growth_score"] = seller_data.apply(
    calculate_growth_score,
    axis=1
)


# ---------------------------------------------------------
# Step 4: Risk Score
# ---------------------------------------------------------

def calculate_risk_score(row):

    score = 0

    # Low sales
    if row["total_sales"] < average_sales:
        score += 1

    # Low order volume
    if row["total_orders"] < average_orders:
        score += 1

    # Low customer reach
    if row["unique_customers"] < average_customers:
        score += 1

    return score


seller_data["risk_score"] = seller_data.apply(
    calculate_risk_score,
    axis=1
)


# ---------------------------------------------------------
# Step 5: Opportunity Score
# ---------------------------------------------------------

seller_data["opportunity_score"] = (
    seller_data["growth_score"]
    - seller_data["risk_score"]
)


# ---------------------------------------------------------
# Step 6: Opportunity Level
# ---------------------------------------------------------

def opportunity_level(row):

    growth = row["growth_score"]
    risk = row["risk_score"]

    if growth == 3 and risk == 0:
        return "High Opportunity"

    elif growth >= 2 and risk <= 1:
        return "Medium Opportunity"

    elif risk >= 2:
        return "Low Opportunity"

    else:
        return "Monitor"


seller_data["opportunity_level"] = seller_data.apply(
    opportunity_level,
    axis=1
)


# ---------------------------------------------------------
# Step 7: Rank Sellers
# ---------------------------------------------------------

seller_data = seller_data.sort_values(
    [
        "opportunity_score",
        "total_sales"
    ],
    ascending=[
        False,
        False
    ]
)


print("\nTop 10 Seller Opportunities:")

print(
    seller_data[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "sales_per_order",
            "sales_per_customer",
            "growth_score",
            "risk_score",
            "opportunity_score",
            "opportunity_level"
        ]
    ].head(10)
)


# ---------------------------------------------------------
# Step 8: High Opportunity Sellers
# ---------------------------------------------------------

high_opportunity = seller_data[
    seller_data["opportunity_level"] ==
    "High Opportunity"
]


print("\nHigh Opportunity Sellers:")

print(
    high_opportunity[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "growth_score",
            "risk_score",
            "opportunity_score",
            "opportunity_level"
        ]
    ].head(10)
)


# ---------------------------------------------------------
# Step 9: Medium Opportunity Sellers
# ---------------------------------------------------------

medium_opportunity = seller_data[
    seller_data["opportunity_level"] ==
    "Medium Opportunity"
]


print("\nMedium Opportunity Sellers:")

print(
    medium_opportunity[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "growth_score",
            "risk_score",
            "opportunity_score",
            "opportunity_level"
        ]
    ].head(10)
)


# ---------------------------------------------------------
# Step 10: Opportunity Summary
# ---------------------------------------------------------

print("\nSeller Opportunity Summary:")

print(
    "Total Sellers:"
)

print(
    seller_data["seller_id"].nunique()
)


print(
    "\nHigh Opportunity Sellers:"
)

print(
    len(high_opportunity)
)


print(
    "\nMedium Opportunity Sellers:"
)

print(
    len(medium_opportunity)
)


print(
    "\nLow Opportunity Sellers:"
)

print(
    len(
        seller_data[
            seller_data["opportunity_level"] ==
            "Low Opportunity"
        ]
    )
)


print(
    "\nSellers to Monitor:"
)

print(
    len(
        seller_data[
            seller_data["opportunity_level"] ==
            "Monitor"
        ]
    )
)


print(
    "\nHighest Opportunity Score:"
)

print(
    seller_data["opportunity_score"].max()
)


# ---------------------------------------------------------
# Step 11: Close connection
# ---------------------------------------------------------

connection.close()


print(
    "\nStep 40 Seller Opportunity Analysis "
    "completed successfully."
)