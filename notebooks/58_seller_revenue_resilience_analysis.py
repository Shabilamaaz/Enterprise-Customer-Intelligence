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
# Step 2: Calculate Revenue Statistics
# ---------------------------------------------------------

seller_resilience = (
    seller_monthly_revenue
    .groupby("seller_id")
    .agg(
        average_monthly_revenue=(
            "monthly_revenue",
            "mean"
        ),
        minimum_monthly_revenue=(
            "monthly_revenue",
            "min"
        ),
        maximum_monthly_revenue=(
            "monthly_revenue",
            "max"
        ),
        revenue_months=(
            "monthly_revenue",
            "count"
        )
    )
    .reset_index()
)


# ---------------------------------------------------------
# Step 3: Revenue Stability Ratio
# ---------------------------------------------------------

seller_resilience["revenue_stability_ratio"] = (
    seller_resilience["minimum_monthly_revenue"]
    /
    seller_resilience["maximum_monthly_revenue"]
)


# ---------------------------------------------------------
# Step 4: Revenue Resilience Score
# ---------------------------------------------------------

seller_resilience["resilience_score"] = (
    seller_resilience["revenue_stability_ratio"]
    * 100
)


seller_resilience["resilience_score"] = (
    seller_resilience["resilience_score"]
    .round(2)
)


# ---------------------------------------------------------
# Step 5: Resilience Classification
# ---------------------------------------------------------

def classify_resilience(row):

    if row["revenue_stability_ratio"] >= 0.70:
        return "High Resilience"

    elif row["revenue_stability_ratio"] >= 0.40:
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
# Step 6: Top Resilient Sellers
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
            "average_monthly_revenue",
            "minimum_monthly_revenue",
            "maximum_monthly_revenue",
            "revenue_stability_ratio",
            "resilience_score",
            "resilience_category"
        ]
    ]
)


# ---------------------------------------------------------
# Step 7: High Resilience Sellers
# ---------------------------------------------------------

high_resilience_sellers = seller_resilience[
    seller_resilience["resilience_category"]
    == "High Resilience"
]


print("\nHigh Resilience Sellers:")
print(
    len(high_resilience_sellers)
)


# ---------------------------------------------------------
# Step 8: Medium Resilience Sellers
# ---------------------------------------------------------

medium_resilience_sellers = seller_resilience[
    seller_resilience["resilience_category"]
    == "Medium Resilience"
]


print("\nMedium Resilience Sellers:")
print(
    len(medium_resilience_sellers)
)


# ---------------------------------------------------------
# Step 9: Low Resilience Sellers
# ---------------------------------------------------------

low_resilience_sellers = seller_resilience[
    seller_resilience["resilience_category"]
    == "Low Resilience"
]


print("\nLow Resilience Sellers:")
print(
    len(low_resilience_sellers)
)


# ---------------------------------------------------------
# Step 10: Strongest Resilient Seller
# ---------------------------------------------------------

strongest_resilience = (
    seller_resilience
    .sort_values(
        "resilience_score",
        ascending=False
    )
    .iloc[0]
)


print("\nStrongest Revenue Resilience Seller:")

print(
    strongest_resilience["seller_id"]
)

print(
    "Resilience Score:"
)

print(
    strongest_resilience["resilience_score"]
)

print(
    "Revenue Stability Ratio:"
)

print(
    round(
        strongest_resilience[
            "revenue_stability_ratio"
        ],
        4
    )
)


# ---------------------------------------------------------
# Step 11: Weakest Resilient Seller
# ---------------------------------------------------------

weakest_resilience = (
    seller_resilience
    .sort_values(
        "resilience_score",
        ascending=True
    )
    .iloc[0]
)


print("\nWeakest Revenue Resilience Seller:")

print(
    weakest_resilience["seller_id"]
)

print(
    "Resilience Score:"
)

print(
    weakest_resilience["resilience_score"]
)

print(
    "Revenue Stability Ratio:"
)

print(
    round(
        weakest_resilience[
            "revenue_stability_ratio"
        ],
        4
    )
)


# ---------------------------------------------------------
# Step 12: Resilience Summary
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
    seller_resilience["resilience_score"].max()
)


# ---------------------------------------------------------
# Step 13: Close Connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Completion Message
# ---------------------------------------------------------

print(
    "\nStep 58 Seller Revenue Resilience Analysis "
    "completed successfully."
)