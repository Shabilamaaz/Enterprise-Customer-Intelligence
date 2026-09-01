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
# Step 1: Monthly Seller Revenue
# ---------------------------------------------------------

query = """
SELECT
    oi.seller_id,
    strftime('%Y-%m', o.order_purchase_timestamp) AS sales_month,
    ROUND(SUM(oi.price), 2) AS monthly_revenue
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
WHERE o.order_purchase_timestamp IS NOT NULL
GROUP BY
    oi.seller_id,
    sales_month
ORDER BY
    oi.seller_id,
    sales_month
"""

seller_monthly_revenue = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Monthly Revenue:")
print(seller_monthly_revenue.head(10))


# ---------------------------------------------------------
# Step 2: Previous Month Revenue
# ---------------------------------------------------------

seller_monthly_revenue["previous_month_revenue"] = (
    seller_monthly_revenue
    .groupby("seller_id")["monthly_revenue"]
    .shift(1)
)


# ---------------------------------------------------------
# Step 3: Revenue Growth
# ---------------------------------------------------------

seller_monthly_revenue["revenue_growth"] = (
    seller_monthly_revenue["monthly_revenue"]
    -
    seller_monthly_revenue["previous_month_revenue"]
)


# ---------------------------------------------------------
# Step 4: Growth Percentage
# ---------------------------------------------------------

seller_monthly_revenue["growth_percentage"] = (
    seller_monthly_revenue["revenue_growth"]
    /
    seller_monthly_revenue["previous_month_revenue"].replace(
        0,
        pd.NA
    )
    * 100
)


# ---------------------------------------------------------
# Step 5: Remove First Month Records
# ---------------------------------------------------------

growth_data = seller_monthly_revenue[
    seller_monthly_revenue["previous_month_revenue"].notna()
].copy()


# ---------------------------------------------------------
# Step 6: Seller Revenue Risk Metrics
# ---------------------------------------------------------

seller_risk = (
    growth_data
    .groupby("seller_id", as_index=False)
    .agg(
        average_monthly_revenue=(
            "monthly_revenue",
            "mean"
        ),
        revenue_std=(
            "monthly_revenue",
            "std"
        ),
        average_growth_percentage=(
            "growth_percentage",
            "mean"
        ),
        negative_growth_months=(
            "revenue_growth",
            lambda x: (x < 0).sum()
        ),
        positive_growth_months=(
            "revenue_growth",
            lambda x: (x > 0).sum()
        ),
        growth_periods=(
            "revenue_growth",
            "count"
        )
    )
)


# ---------------------------------------------------------
# Step 7: Revenue Volatility Ratio
# ---------------------------------------------------------

seller_risk["volatility_ratio"] = (
    seller_risk["revenue_std"]
    /
    seller_risk["average_monthly_revenue"].replace(
        0,
        pd.NA
    )
)


seller_risk["volatility_ratio"] = (
    seller_risk["volatility_ratio"]
    .fillna(0)
)


# ---------------------------------------------------------
# Step 8: Negative Growth Ratio
# ---------------------------------------------------------

seller_risk["negative_growth_ratio"] = (
    seller_risk["negative_growth_months"]
    /
    seller_risk["growth_periods"]
)


# ---------------------------------------------------------
# Step 9: Revenue Risk Score
# ---------------------------------------------------------

seller_risk["volatility_component"] = (
    seller_risk["volatility_ratio"]
    .clip(
        lower=0,
        upper=2
    )
    * 2
)


seller_risk["negative_growth_component"] = (
    seller_risk["negative_growth_ratio"]
    * 2
)


seller_risk["growth_component"] = (
    (-seller_risk["average_growth_percentage"])
    .clip(
        lower=0,
        upper=100
    )
    / 100
)


seller_risk["risk_score"] = (
    seller_risk["volatility_component"]
    +
    seller_risk["negative_growth_component"]
    +
    seller_risk["growth_component"]
)


seller_risk["risk_score"] = (
    seller_risk["risk_score"]
    .round(2)
)


# ---------------------------------------------------------
# Step 10: Risk Classification
# ---------------------------------------------------------

def classify_risk(row):

    if row["risk_score"] >= 3:
        return "High Risk"

    elif row["risk_score"] >= 1.5:
        return "Medium Risk"

    else:
        return "Low Risk"


seller_risk["risk_category"] = (
    seller_risk.apply(
        classify_risk,
        axis=1
    )
)


# ---------------------------------------------------------
# Step 11: Top Risky Sellers
# ---------------------------------------------------------

top_risky_sellers = (
    seller_risk
    .sort_values(
        "risk_score",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Sellers by Revenue Risk:")

print(
    top_risky_sellers[
        [
            "seller_id",
            "average_monthly_revenue",
            "volatility_ratio",
            "negative_growth_months",
            "average_growth_percentage",
            "risk_score",
            "risk_category"
        ]
    ]
)


# ---------------------------------------------------------
# Step 12: High Risk Sellers
# ---------------------------------------------------------

high_risk_sellers = seller_risk[
    seller_risk["risk_category"]
    == "High Risk"
]


print("\nHigh Risk Sellers:")
print(
    len(high_risk_sellers)
)


# ---------------------------------------------------------
# Step 13: Medium Risk Sellers
# ---------------------------------------------------------

medium_risk_sellers = seller_risk[
    seller_risk["risk_category"]
    == "Medium Risk"
]


print("\nMedium Risk Sellers:")
print(
    len(medium_risk_sellers)
)


# ---------------------------------------------------------
# Step 14: Low Risk Sellers
# ---------------------------------------------------------

low_risk_sellers = seller_risk[
    seller_risk["risk_category"]
    == "Low Risk"
]


print("\nLow Risk Sellers:")
print(
    len(low_risk_sellers)
)


# ---------------------------------------------------------
# Step 15: Highest Risk Seller
# ---------------------------------------------------------

highest_risk = (
    seller_risk
    .sort_values(
        "risk_score",
        ascending=False
    )
    .iloc[0]
)


print("\nHighest Revenue Risk Seller:")

print(
    highest_risk["seller_id"]
)

print(
    "Risk Score:"
)

print(
    highest_risk["risk_score"]
)

print(
    "Volatility Ratio:"
)

print(
    round(
        highest_risk["volatility_ratio"],
        2
    )
)

print(
    "Negative Growth Months:"
)

print(
    highest_risk["negative_growth_months"]
)


# ---------------------------------------------------------
# Step 16: Lowest Risk Seller
# ---------------------------------------------------------

lowest_risk = (
    seller_risk
    .sort_values(
        "risk_score",
        ascending=True
    )
    .iloc[0]
)


print("\nLowest Revenue Risk Seller:")

print(
    lowest_risk["seller_id"]
)

print(
    "Risk Score:"
)

print(
    lowest_risk["risk_score"]
)


# ---------------------------------------------------------
# Step 17: Revenue Risk Summary
# ---------------------------------------------------------

print("\nSeller Revenue Risk Summary:")

print(
    "High Risk Sellers:"
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
    len(low_risk_sellers)
)

print(
    "\nHighest Risk Score:"
)

print(
    seller_risk["risk_score"].max()
)

print(
    "\nLowest Risk Score:"
)

print(
    seller_risk["risk_score"].min()
)


# ---------------------------------------------------------
# Step 18: Close Connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Completion Message
# ---------------------------------------------------------

print(
    "\nStep 52 Seller Revenue Risk Analysis "
    "completed successfully."
)