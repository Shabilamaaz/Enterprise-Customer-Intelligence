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


seller_monthly_revenue["growth_percentage"] = (
    seller_monthly_revenue["revenue_growth"]
    /
    seller_monthly_revenue["previous_month_revenue"]
    * 100
)


# ---------------------------------------------------------
# Step 4: Remove First Month Records
# ---------------------------------------------------------

growth_data = seller_monthly_revenue[
    seller_monthly_revenue["previous_month_revenue"].notna()
].copy()


# ---------------------------------------------------------
# Step 5: Calculate Recent Momentum
# ---------------------------------------------------------

growth_data["positive_growth"] = (
    growth_data["revenue_growth"] > 0
).astype(int)

growth_data["negative_growth"] = (
    growth_data["revenue_growth"] < 0
).astype(int)


seller_momentum = (
    growth_data
    .groupby("seller_id", as_index=False)
    .agg(
        total_growth=("revenue_growth", "sum"),
        average_growth_percentage=(
            "growth_percentage",
            "mean"
        ),
        positive_growth_months=(
            "positive_growth",
            "sum"
        ),
        negative_growth_months=(
            "negative_growth",
            "sum"
        ),
        growth_periods=(
            "revenue_growth",
            "count"
        )
    )
)


# ---------------------------------------------------------
# Step 6: Momentum Score
# ---------------------------------------------------------

seller_momentum["positive_growth_ratio"] = (
    seller_momentum["positive_growth_months"]
    /
    seller_momentum["growth_periods"]
)


seller_momentum["momentum_score"] = (
    seller_momentum["positive_growth_ratio"] * 2
    +
    seller_momentum["average_growth_percentage"].clip(
        lower=-100,
        upper=100
    ) / 100
)


seller_momentum["momentum_score"] = (
    seller_momentum["momentum_score"]
    .round(2)
)


# ---------------------------------------------------------
# Step 7: Momentum Classification
# ---------------------------------------------------------

def classify_momentum(row):

    if (
        row["positive_growth_ratio"] >= 0.60
        and row["average_growth_percentage"] > 0
    ):
        return "High Momentum"

    elif (
        row["positive_growth_ratio"] >= 0.40
        and row["average_growth_percentage"] >= 0
    ):
        return "Medium Momentum"

    else:
        return "Low Momentum"


seller_momentum["momentum_category"] = (
    seller_momentum.apply(
        classify_momentum,
        axis=1
    )
)


# ---------------------------------------------------------
# Step 8: Top Sellers by Momentum
# ---------------------------------------------------------

top_momentum_sellers = (
    seller_momentum
    .sort_values(
        "momentum_score",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Sellers by Revenue Momentum:")

print(
    top_momentum_sellers[
        [
            "seller_id",
            "total_growth",
            "average_growth_percentage",
            "positive_growth_months",
            "negative_growth_months",
            "momentum_score",
            "momentum_category"
        ]
    ]
)


# ---------------------------------------------------------
# Step 9: High Momentum Sellers
# ---------------------------------------------------------

high_momentum_sellers = seller_momentum[
    seller_momentum["momentum_category"]
    == "High Momentum"
]


print("\nHigh Momentum Sellers:")
print(
    len(high_momentum_sellers)
)


# ---------------------------------------------------------
# Step 10: Medium Momentum Sellers
# ---------------------------------------------------------

medium_momentum_sellers = seller_momentum[
    seller_momentum["momentum_category"]
    == "Medium Momentum"
]


print("\nMedium Momentum Sellers:")
print(
    len(medium_momentum_sellers)
)


# ---------------------------------------------------------
# Step 11: Low Momentum Sellers
# ---------------------------------------------------------

low_momentum_sellers = seller_momentum[
    seller_momentum["momentum_category"]
    == "Low Momentum"
]


print("\nLow Momentum Sellers:")
print(
    len(low_momentum_sellers)
)


# ---------------------------------------------------------
# Step 12: Strongest Momentum Seller
# ---------------------------------------------------------

strongest_momentum = (
    seller_momentum
    .sort_values(
        "momentum_score",
        ascending=False
    )
    .iloc[0]
)


print("\nStrongest Momentum Seller:")

print(
    strongest_momentum["seller_id"]
)

print(
    "Momentum Score:"
)

print(
    strongest_momentum["momentum_score"]
)

print(
    "Average Growth Percentage:"
)

print(
    round(
        strongest_momentum[
            "average_growth_percentage"
        ],
        2
    )
)


# ---------------------------------------------------------
# Step 13: Most Declining Seller
# ---------------------------------------------------------

weakest_momentum = (
    seller_momentum
    .sort_values(
        "momentum_score",
        ascending=True
    )
    .iloc[0]
)


print("\nWeakest Momentum Seller:")

print(
    weakest_momentum["seller_id"]
)

print(
    "Momentum Score:"
)

print(
    weakest_momentum["momentum_score"]
)

print(
    "Average Growth Percentage:"
)

print(
    round(
        weakest_momentum[
            "average_growth_percentage"
        ],
        2
    )
)


# ---------------------------------------------------------
# Step 14: Momentum Summary
# ---------------------------------------------------------

print("\nSeller Revenue Momentum Summary:")

print(
    "High Momentum Sellers:"
)

print(
    len(high_momentum_sellers)
)

print(
    "\nMedium Momentum Sellers:"
)

print(
    len(medium_momentum_sellers)
)

print(
    "\nLow Momentum Sellers:"
)

print(
    len(low_momentum_sellers)
)

print(
    "\nHighest Momentum Score:"
)

print(
    seller_momentum["momentum_score"].max()
)


# ---------------------------------------------------------
# Step 15: Close Connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Completion Message
# ---------------------------------------------------------

print(
    "\nStep 49 Seller Revenue Momentum Analysis "
    "completed successfully."
)