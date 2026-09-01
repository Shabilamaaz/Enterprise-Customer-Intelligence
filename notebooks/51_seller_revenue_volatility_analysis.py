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
# Step 2: Seller Revenue Statistics
# =========================================================

seller_volatility = (
    seller_monthly_revenue
    .groupby("seller_id", as_index=False)
    .agg(
        average_monthly_revenue=(
            "monthly_revenue",
            "mean"
        ),
        revenue_std_dev=(
            "monthly_revenue",
            "std"
        ),
        minimum_monthly_revenue=(
            "monthly_revenue",
            "min"
        ),
        maximum_monthly_revenue=(
            "monthly_revenue",
            "max"
        ),
        active_months=(
            "monthly_revenue",
            "count"
        )
    )
)


# =========================================================
# Step 3: Coefficient of Variation
# =========================================================

seller_volatility["coefficient_of_variation"] = (
    seller_volatility["revenue_std_dev"]
    /
    seller_volatility["average_monthly_revenue"]
)


seller_volatility["coefficient_of_variation"] = (
    seller_volatility["coefficient_of_variation"]
    .replace([float("inf"), -float("inf")], pd.NA)
    .fillna(0)
)


# =========================================================
# Step 4: Revenue Range
# =========================================================

seller_volatility["revenue_range"] = (
    seller_volatility["maximum_monthly_revenue"]
    -
    seller_volatility["minimum_monthly_revenue"]
)


# =========================================================
# Step 5: Volatility Score
# =========================================================

seller_volatility["volatility_score"] = (
    seller_volatility["coefficient_of_variation"] * 100
)


seller_volatility["volatility_score"] = (
    seller_volatility["volatility_score"]
    .round(2)
)


# =========================================================
# Step 6: Volatility Classification
# =========================================================

def classify_volatility(row):

    cv = row["coefficient_of_variation"]

    if cv <= 0.50:
        return "Low Volatility"

    elif cv <= 1.00:
        return "Medium Volatility"

    else:
        return "High Volatility"


seller_volatility["volatility_category"] = (
    seller_volatility.apply(
        classify_volatility,
        axis=1
    )
)


# =========================================================
# Step 7: Top 10 Most Volatile Sellers
# =========================================================

top_volatile_sellers = (
    seller_volatility
    .sort_values(
        "volatility_score",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Most Volatile Sellers:")

print(
    top_volatile_sellers[
        [
            "seller_id",
            "average_monthly_revenue",
            "revenue_std_dev",
            "minimum_monthly_revenue",
            "maximum_monthly_revenue",
            "coefficient_of_variation",
            "volatility_score",
            "volatility_category"
        ]
    ]
)


# =========================================================
# Step 8: Low Volatility Sellers
# =========================================================

low_volatility_sellers = seller_volatility[
    seller_volatility["volatility_category"]
    == "Low Volatility"
]


print("\nLow Volatility Sellers:")

print(
    len(low_volatility_sellers)
)


# =========================================================
# Step 9: Medium Volatility Sellers
# =========================================================

medium_volatility_sellers = seller_volatility[
    seller_volatility["volatility_category"]
    == "Medium Volatility"
]


print("\nMedium Volatility Sellers:")

print(
    len(medium_volatility_sellers)
)


# =========================================================
# Step 10: High Volatility Sellers
# =========================================================

high_volatility_sellers = seller_volatility[
    seller_volatility["volatility_category"]
    == "High Volatility"
]


print("\nHigh Volatility Sellers:")

print(
    len(high_volatility_sellers)
)


# =========================================================
# Step 11: Most Volatile Seller
# =========================================================

most_volatile_seller = (
    seller_volatility
    .sort_values(
        "volatility_score",
        ascending=False
    )
    .iloc[0]
)


print("\nMost Volatile Seller:")

print(
    most_volatile_seller["seller_id"]
)

print(
    "Volatility Score:"
)

print(
    most_volatile_seller["volatility_score"]
)

print(
    "Average Monthly Revenue:"
)

print(
    round(
        most_volatile_seller[
            "average_monthly_revenue"
        ],
        2
    )
)


# =========================================================
# Step 12: Most Stable Seller
# =========================================================

most_stable_seller = (
    seller_volatility
    .sort_values(
        "volatility_score",
        ascending=True
    )
    .iloc[0]
)


print("\nMost Stable Seller:")

print(
    most_stable_seller["seller_id"]
)

print(
    "Volatility Score:"
)

print(
    most_stable_seller["volatility_score"]
)

print(
    "Average Monthly Revenue:"
)

print(
    round(
        most_stable_seller[
            "average_monthly_revenue"
        ],
        2
    )
)


# =========================================================
# Step 13: Highest Revenue Range
# =========================================================

highest_range_seller = (
    seller_volatility
    .sort_values(
        "revenue_range",
        ascending=False
    )
    .iloc[0]
)


print("\nSeller With Highest Revenue Range:")

print(
    highest_range_seller["seller_id"]
)

print(
    "Revenue Range:"
)

print(
    round(
        highest_range_seller[
            "revenue_range"
        ],
        2
    )
)


# =========================================================
# Step 14: Volatility Summary
# =========================================================

print("\nSeller Revenue Volatility Summary:")

print(
    "Low Volatility Sellers:"
)

print(
    len(low_volatility_sellers)
)

print(
    "\nMedium Volatility Sellers:"
)

print(
    len(medium_volatility_sellers)
)

print(
    "\nHigh Volatility Sellers:"
)

print(
    len(high_volatility_sellers)
)

print(
    "\nHighest Volatility Score:"
)

print(
    seller_volatility[
        "volatility_score"
    ].max()
)

print(
    "\nLowest Volatility Score:"
)

print(
    seller_volatility[
        "volatility_score"
    ].min()
)


# =========================================================
# Step 15: Close Connection
# =========================================================

connection.close()


# =========================================================
# Completion Message
# =========================================================

print(
    "\nStep 51 Seller Revenue Volatility Analysis "
    "completed successfully."
)