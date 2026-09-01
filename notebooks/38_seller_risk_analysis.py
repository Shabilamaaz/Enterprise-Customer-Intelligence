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
# Step 1: Seller Risk Analysis
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

ORDER BY total_sales ASC
"""

seller_risk = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Risk Analysis:")
print(seller_risk.head(10))


# ---------------------------------------------------------
# Step 2: Calculate Risk Score
# ---------------------------------------------------------

average_sales = seller_risk[
    "total_sales"
].mean()

average_orders = seller_risk[
    "total_orders"
].mean()

average_customers = seller_risk[
    "unique_customers"
].mean()


def calculate_risk(row):

    risk_score = 0

    # Low sales risk
    if row["total_sales"] < average_sales:
        risk_score += 1

    # Low order volume risk
    if row["total_orders"] < average_orders:
        risk_score += 1

    # Low customer reach risk
    if row["unique_customers"] < average_customers:
        risk_score += 1

    return risk_score


seller_risk["risk_score"] = seller_risk.apply(
    calculate_risk,
    axis=1
)


# ---------------------------------------------------------
# Step 3: Assign Risk Level
# ---------------------------------------------------------

def risk_level(score):

    if score >= 3:
        return "High Risk"

    elif score == 2:
        return "Medium Risk"

    else:
        return "Low Risk"


seller_risk["risk_level"] = seller_risk[
    "risk_score"
].apply(risk_level)


# ---------------------------------------------------------
# Step 4: Sort Sellers by Risk
# ---------------------------------------------------------

seller_risk = seller_risk.sort_values(
    [
        "risk_score",
        "total_sales"
    ],
    ascending=[
        False,
        True
    ]
)


print("\nSeller Risk Ranking:")

print(
    seller_risk[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "sales_per_order",
            "sales_per_customer",
            "risk_score",
            "risk_level"
        ]
    ].head(10)
)


# ---------------------------------------------------------
# Step 5: High Risk Sellers
# ---------------------------------------------------------

high_risk_sellers = seller_risk[
    seller_risk["risk_level"] == "High Risk"
]


print("\nHigh Risk Sellers:")

print(
    high_risk_sellers[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "risk_score",
            "risk_level"
        ]
    ].head(10)
)


# ---------------------------------------------------------
# Step 6: Medium Risk Sellers
# ---------------------------------------------------------

medium_risk_sellers = seller_risk[
    seller_risk["risk_level"] == "Medium Risk"
]


print("\nMedium Risk Sellers:")

print(
    medium_risk_sellers[
        [
            "seller_id",
            "total_orders",
            "unique_customers",
            "total_sales",
            "risk_score",
            "risk_level"
        ]
    ].head(10)
)


# ---------------------------------------------------------
# Step 7: Risk Summary
# ---------------------------------------------------------

print("\nSeller Risk Summary:")

print(
    "Total Sellers:"
)

print(
    seller_risk["seller_id"].nunique()
)


print(
    "\nHigh Risk Sellers:"
)

print(
    len(high_risk_sellers)
)


print(
    "\nMedium Risk Sellers:"
)

print(
    len(medium_risk_sellers)
)


print(
    "\nLow Risk Sellers:"
)

print(
    len(
        seller_risk[
            seller_risk["risk_level"] == "Low Risk"
        ]
    )
)


print(
    "\nHighest Risk Score:"
)

print(
    seller_risk["risk_score"].max()
)


# ---------------------------------------------------------
# Step 8: Close connection
# ---------------------------------------------------------

connection.close()


print(
    "\nStep 38 Seller Risk Analysis "
    "completed successfully."
)