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
# Connect to SQLite Database
# =========================================================

connection = sqlite3.connect(db_path)


# =========================================================
# Step 1: Monthly Seller Revenue
# =========================================================

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


# =========================================================
# Step 2: Previous Month Revenue
# =========================================================

seller_monthly_revenue["previous_month_revenue"] = (
    seller_monthly_revenue
    .groupby("seller_id")["monthly_revenue"]
    .shift(1)
)


# =========================================================
# Step 3: Revenue Growth
# =========================================================

seller_monthly_revenue["revenue_growth"] = (
    seller_monthly_revenue["monthly_revenue"]
    -
    seller_monthly_revenue["previous_month_revenue"]
)


# =========================================================
# Step 4: Growth Percentage
# =========================================================

seller_monthly_revenue["growth_percentage"] = (
    seller_monthly_revenue["revenue_growth"]
    /
    seller_monthly_revenue["previous_month_revenue"]
    * 100
)


# =========================================================
# Step 5: Previous Growth Percentage
# =========================================================

seller_monthly_revenue["previous_growth_percentage"] = (
    seller_monthly_revenue
    .groupby("seller_id")["growth_percentage"]
    .shift(1)
)


# =========================================================
# Step 6: Revenue Acceleration
# =========================================================

seller_monthly_revenue["revenue_acceleration"] = (
    seller_monthly_revenue["growth_percentage"]
    -
    seller_monthly_revenue["previous_growth_percentage"]
)


# =========================================================
# Step 7: Remove Invalid Records
# =========================================================

acceleration_data = seller_monthly_revenue[
    seller_monthly_revenue["previous_growth_percentage"].notna()
].copy()


# =========================================================
# Step 8: Positive and Negative Acceleration
# =========================================================

acceleration_data["positive_acceleration"] = (
    acceleration_data["revenue_acceleration"] > 0
).astype(int)

acceleration_data["negative_acceleration"] = (
    acceleration_data["revenue_acceleration"] < 0
).astype(int)


# =========================================================
# Step 9: Seller Acceleration Summary
# =========================================================

seller_acceleration = (
    acceleration_data
    .groupby("seller_id", as_index=False)
    .agg(
        average_acceleration=(
            "revenue_acceleration",
            "mean"
        ),
        total_acceleration=(
            "revenue_acceleration",
            "sum"
        ),
        positive_acceleration_months=(
            "positive_acceleration",
            "sum"
        ),
        negative_acceleration_months=(
            "negative_acceleration",
            "sum"
        ),
        acceleration_periods=(
            "revenue_acceleration",
            "count"
        )
    )
)


# =========================================================
# Step 10: Acceleration Ratio
# =========================================================

seller_acceleration["positive_acceleration_ratio"] = (
    seller_acceleration["positive_acceleration_months"]
    /
    seller_acceleration["acceleration_periods"]
)


# =========================================================
# Step 11: Acceleration Score
# =========================================================

seller_acceleration["acceleration_score"] = (
    seller_acceleration["positive_acceleration_ratio"] * 2
    +
    seller_acceleration["average_acceleration"]
        .clip(lower=-100, upper=100) / 100
)


seller_acceleration["acceleration_score"] = (
    seller_acceleration["acceleration_score"]
    .round(2)
)


# =========================================================
# Step 12: Acceleration Classification
# =========================================================

def classify_acceleration(row):

    if (
        row["positive_acceleration_ratio"] >= 0.60
        and row["average_acceleration"] > 0
    ):
        return "High Acceleration"

    elif (
        row["positive_acceleration_ratio"] >= 0.40
        and row["average_acceleration"] >= 0
    ):
        return "Medium Acceleration"

    else:
        return "Low Acceleration"


seller_acceleration["acceleration_category"] = (
    seller_acceleration.apply(
        classify_acceleration,
        axis=1
    )
)


# =========================================================
# Step 13: Top Sellers by Acceleration
# =========================================================

top_acceleration_sellers = (
    seller_acceleration
    .sort_values(
        "acceleration_score",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Sellers by Revenue Acceleration:")

print(
    top_acceleration_sellers[
        [
            "seller_id",
            "average_acceleration",
            "total_acceleration",
            "positive_acceleration_months",
            "negative_acceleration_months",
            "acceleration_score",
            "acceleration_category"
        ]
    ]
)


# =========================================================
# Step 14: High Acceleration Sellers
# =========================================================

high_acceleration_sellers = seller_acceleration[
    seller_acceleration["acceleration_category"]
    == "High Acceleration"
]


print("\nHigh Acceleration Sellers:")

print(
    len(high_acceleration_sellers)
)


# =========================================================
# Step 15: Medium Acceleration Sellers
# =========================================================

medium_acceleration_sellers = seller_acceleration[
    seller_acceleration["acceleration_category"]
    == "Medium Acceleration"
]


print("\nMedium Acceleration Sellers:")

print(
    len(medium_acceleration_sellers)
)


# =========================================================
# Step 16: Low Acceleration Sellers
# =========================================================

low_acceleration_sellers = seller_acceleration[
    seller_acceleration["acceleration_category"]
    == "Low Acceleration"
]


print("\nLow Acceleration Sellers:")

print(
    len(low_acceleration_sellers)
)


# =========================================================
# Step 17: Strongest Accelerating Seller
# =========================================================

strongest_acceleration = (
    seller_acceleration
    .sort_values(
        "acceleration_score",
        ascending=False
    )
    .iloc[0]
)


print("\nStrongest Accelerating Seller:")

print(
    strongest_acceleration["seller_id"]
)

print(
    "Acceleration Score:"
)

print(
    strongest_acceleration["acceleration_score"]
)

print(
    "Average Acceleration:"
)

print(
    round(
        strongest_acceleration[
            "average_acceleration"
        ],
        2
    )
)


# =========================================================
# Step 18: Most Decelerating Seller
# =========================================================

weakest_acceleration = (
    seller_acceleration
    .sort_values(
        "acceleration_score",
        ascending=True
    )
    .iloc[0]
)


print("\nMost Decelerating Seller:")

print(
    weakest_acceleration["seller_id"]
)

print(
    "Acceleration Score:"
)

print(
    weakest_acceleration["acceleration_score"]
)

print(
    "Average Acceleration:"
)

print(
    round(
        weakest_acceleration[
            "average_acceleration"
        ],
        2
    )
)


# =========================================================
# Step 19: Acceleration Summary
# =========================================================

print("\nSeller Revenue Acceleration Summary:")

print(
    "High Acceleration Sellers:"
)

print(
    len(high_acceleration_sellers)
)

print(
    "\nMedium Acceleration Sellers:"
)

print(
    len(medium_acceleration_sellers)
)

print(
    "\nLow Acceleration Sellers:"
)

print(
    len(low_acceleration_sellers)
)

print(
    "\nHighest Acceleration Score:"
)

print(
    seller_acceleration[
        "acceleration_score"
    ].max()
)


# =========================================================
# Step 20: Close Connection
# =========================================================

connection.close()


# =========================================================
# Completion Message
# =========================================================

print(
    "\nStep 50 Seller Revenue Acceleration Analysis "
    "completed successfully."
)