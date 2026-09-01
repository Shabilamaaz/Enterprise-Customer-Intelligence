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
# Step 3: Revenue Change
# ---------------------------------------------------------

seller_monthly_revenue["revenue_change"] = (
    seller_monthly_revenue["monthly_revenue"]
    -
    seller_monthly_revenue["previous_month_revenue"]
)


# ---------------------------------------------------------
# Step 4: Growth Percentage
# ---------------------------------------------------------

seller_monthly_revenue["growth_percentage"] = (
    seller_monthly_revenue["revenue_change"]
    /
    seller_monthly_revenue["previous_month_revenue"]
    * 100
)


# ---------------------------------------------------------
# Step 5: Identify Growth and Decline Months
# ---------------------------------------------------------

seller_monthly_revenue["growth_month"] = (
    seller_monthly_revenue["revenue_change"] > 0
).astype(int)

seller_monthly_revenue["decline_month"] = (
    seller_monthly_revenue["revenue_change"] < 0
).astype(int)


# ---------------------------------------------------------
# Step 6: Identify Recovery Months
# ---------------------------------------------------------

seller_monthly_revenue["recovery_month"] = (
    (
        seller_monthly_revenue["previous_month_revenue"].notna()
    )
    &
    (
        seller_monthly_revenue["revenue_change"] > 0
    )
).astype(int)


# ---------------------------------------------------------
# Step 7: Remove First Month Records
# ---------------------------------------------------------

resilience_data = seller_monthly_revenue[
    seller_monthly_revenue["previous_month_revenue"].notna()
].copy()


# ---------------------------------------------------------
# Step 8: Seller Resilience Metrics
# ---------------------------------------------------------

seller_resilience = (
    resilience_data
    .groupby("seller_id", as_index=False)
    .agg(
        total_revenue_change=(
            "revenue_change",
            "sum"
        ),
        average_growth_percentage=(
            "growth_percentage",
            "mean"
        ),
        growth_months=(
            "growth_month",
            "sum"
        ),
        decline_months=(
            "decline_month",
            "sum"
        ),
        recovery_months=(
            "recovery_month",
            "sum"
        ),
        observed_months=(
            "revenue_change",
            "count"
        )
    )
)


# ---------------------------------------------------------
# Step 9: Recovery Ratio
# ---------------------------------------------------------

seller_resilience["recovery_ratio"] = (
    seller_resilience["recovery_months"]
    /
    seller_resilience["observed_months"]
)


# ---------------------------------------------------------
# Step 10: Growth Consistency
# ---------------------------------------------------------

seller_resilience["growth_consistency"] = (
    seller_resilience["growth_months"]
    /
    seller_resilience["observed_months"]
)


# ---------------------------------------------------------
# Step 11: Resilience Score
# ---------------------------------------------------------

seller_resilience["resilience_score"] = (
    seller_resilience["recovery_ratio"] * 2
    +
    seller_resilience["growth_consistency"]
    +
    seller_resilience["average_growth_percentage"]
    .clip(lower=-100, upper=100)
    / 100
)


seller_resilience["resilience_score"] = (
    seller_resilience["resilience_score"]
    .round(2)
)


# ---------------------------------------------------------
# Step 12: Resilience Classification
# ---------------------------------------------------------

def classify_resilience(row):

    if (
        row["recovery_ratio"] >= 0.60
        and row["growth_consistency"] >= 0.50
    ):
        return "High Resilience"

    elif (
        row["recovery_ratio"] >= 0.40
        and row["growth_consistency"] >= 0.30
    ):
        return "Medium Resilience"

    else:
        return "Low Resilience"


seller_resilience["resilience_category"] = (
    seller_resilience.apply(
        classify_resilience,
        axis=1
    )
)


# ---------------------------------------------------------
# Step 13: Top Resilient Sellers
# ---------------------------------------------------------

top_resilient_sellers = (
    seller_resilience
    .sort_values(
        "resilience_score",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Sellers by Revenue Resilience:")

print(
    top_resilient_sellers[
        [
            "seller_id",
            "total_revenue_change",
            "average_growth_percentage",
            "growth_months",
            "decline_months",
            "recovery_months",
            "recovery_ratio",
            "resilience_score",
            "resilience_category"
        ]
    ]
)


# ---------------------------------------------------------
# Step 14: Resilience Category Counts
# ---------------------------------------------------------

high_resilience_sellers = seller_resilience[
    seller_resilience["resilience_category"]
    == "High Resilience"
]


medium_resilience_sellers = seller_resilience[
    seller_resilience["resilience_category"]
    == "Medium Resilience"
]


low_resilience_sellers = seller_resilience[
    seller_resilience["resilience_category"]
    == "Low Resilience"
]


print("\nHigh Resilience Sellers:")
print(len(high_resilience_sellers))


print("\nMedium Resilience Sellers:")
print(len(medium_resilience_sellers))


print("\nLow Resilience Sellers:")
print(len(low_resilience_sellers))


# ---------------------------------------------------------
# Step 15: Strongest Resilient Seller
# ---------------------------------------------------------

strongest_resilience = (
    seller_resilience
    .sort_values(
        "resilience_score",
        ascending=False
    )
    .iloc[0]
)


print("\nStrongest Resilient Seller:")

print(
    strongest_resilience["seller_id"]
)

print("Resilience Score:")

print(
    strongest_resilience["resilience_score"]
)

print("Recovery Ratio:")

print(
    round(
        strongest_resilience[
            "recovery_ratio"
        ],
        2
    )
)


# ---------------------------------------------------------
# Step 16: Weakest Resilient Seller
# ---------------------------------------------------------

weakest_resilience = (
    seller_resilience
    .sort_values(
        "resilience_score",
        ascending=True
    )
    .iloc[0]
)


print("\nWeakest Resilient Seller:")

print(
    weakest_resilience["seller_id"]
)

print("Resilience Score:")

print(
    weakest_resilience["resilience_score"]
)

print("Recovery Ratio:")

print(
    round(
        weakest_resilience[
            "recovery_ratio"
        ],
        2
    )
)


# ---------------------------------------------------------
# Step 17: Resilience Summary
# ---------------------------------------------------------

print("\nSeller Revenue Resilience Summary:")

print(
    "High Resilience Sellers:"
)

print(
    len(high_resilience_sellers)
)


print(
    "\nMedium Resilience Sellers:"
)

print(
    len(medium_resilience_sellers)
)


print(
    "\nLow Resilience Sellers:"
)

print(
    len(low_resilience_sellers)
)


print(
    "\nHighest Resilience Score:"
)

print(
    seller_resilience[
        "resilience_score"
    ].max()
)


# ---------------------------------------------------------
# Step 18: Close Connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Completion Message
# ---------------------------------------------------------

print(
    "\nStep 57 Seller Revenue Resilience Analysis "
    "completed successfully."
)