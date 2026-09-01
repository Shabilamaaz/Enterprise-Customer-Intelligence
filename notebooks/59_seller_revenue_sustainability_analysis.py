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
print(
    seller_monthly_revenue.head(10)
)


# ---------------------------------------------------------
# Step 2: Calculate Revenue Statistics
# ---------------------------------------------------------

seller_consistency = (
    seller_monthly_revenue
    .groupby("seller_id", as_index=False)
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
        revenue_std=(
            "monthly_revenue",
            "std"
        ),
        revenue_months=(
            "monthly_revenue",
            "count"
        )
    )
)


# ---------------------------------------------------------
# Step 3: Revenue Range
# ---------------------------------------------------------

seller_consistency["revenue_range"] = (
    seller_consistency["maximum_monthly_revenue"]
    -
    seller_consistency["minimum_monthly_revenue"]
)


# ---------------------------------------------------------
# Step 4: Coefficient of Variation
# ---------------------------------------------------------

seller_consistency["coefficient_of_variation"] = (
    seller_consistency["revenue_std"]
    /
    seller_consistency["average_monthly_revenue"]
)


seller_consistency["coefficient_of_variation"] = (
    seller_consistency["coefficient_of_variation"]
    .replace(
        [float("inf"), -float("inf")],
        pd.NA
    )
)


# ---------------------------------------------------------
# Step 5: Consistency Score
# ---------------------------------------------------------

seller_consistency["consistency_score"] = (
    1
    /
    (
        1
        +
        seller_consistency[
            "coefficient_of_variation"
        ].fillna(0)
    )
    * 100
)


seller_consistency["consistency_score"] = (
    seller_consistency["consistency_score"]
    .clip(
        lower=0,
        upper=100
    )
    .round(2)
)


# ---------------------------------------------------------
# Step 6: Consistency Classification
# ---------------------------------------------------------

def classify_consistency(row):

    if (
        row["consistency_score"] >= 75
        and row["revenue_months"] >= 3
    ):
        return "High Consistency"

    elif (
        row["consistency_score"] >= 50
        and row["revenue_months"] >= 3
    ):
        return "Medium Consistency"

    else:
        return "Low Consistency"


seller_consistency["consistency_category"] = (
    seller_consistency.apply(
        classify_consistency,
        axis=1
    )
)


# ---------------------------------------------------------
# Step 7: Top Sellers by Consistency
# ---------------------------------------------------------

top_consistent_sellers = (
    seller_consistency
    .sort_values(
        "consistency_score",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Sellers by Revenue Consistency:")

print(
    top_consistent_sellers[
        [
            "seller_id",
            "average_monthly_revenue",
            "minimum_monthly_revenue",
            "maximum_monthly_revenue",
            "coefficient_of_variation",
            "consistency_score",
            "consistency_category"
        ]
    ]
)


# ---------------------------------------------------------
# Step 8: High Consistency Sellers
# ---------------------------------------------------------

high_consistency_sellers = seller_consistency[
    seller_consistency["consistency_category"]
    == "High Consistency"
]


print("\nHigh Consistency Sellers:")

print(
    len(high_consistency_sellers)
)


# ---------------------------------------------------------
# Step 9: Medium Consistency Sellers
# ---------------------------------------------------------

medium_consistency_sellers = seller_consistency[
    seller_consistency["consistency_category"]
    == "Medium Consistency"
]


print("\nMedium Consistency Sellers:")

print(
    len(medium_consistency_sellers)
)


# ---------------------------------------------------------
# Step 10: Low Consistency Sellers
# ---------------------------------------------------------

low_consistency_sellers = seller_consistency[
    seller_consistency["consistency_category"]
    == "Low Consistency"
]


print("\nLow Consistency Sellers:")

print(
    len(low_consistency_sellers)
)


# ---------------------------------------------------------
# Step 11: Most Consistent Seller
# ---------------------------------------------------------

most_consistent_seller = (
    seller_consistency
    .sort_values(
        "consistency_score",
        ascending=False
    )
    .iloc[0]
)


print("\nMost Consistent Seller:")

print(
    most_consistent_seller["seller_id"]
)

print(
    "Consistency Score:"
)

print(
    most_consistent_seller[
        "consistency_score"
    ]
)

print(
    "Average Monthly Revenue:"
)

print(
    round(
        most_consistent_seller[
            "average_monthly_revenue"
        ],
        2
    )
)


# ---------------------------------------------------------
# Step 12: Least Consistent Seller
# ---------------------------------------------------------

least_consistent_seller = (
    seller_consistency
    .sort_values(
        "consistency_score",
        ascending=True
    )
    .iloc[0]
)


print("\nLeast Consistent Seller:")

print(
    least_consistent_seller["seller_id"]
)

print(
    "Consistency Score:"
)

print(
    least_consistent_seller[
        "consistency_score"
    ]
)

print(
    "Coefficient of Variation:"
)

print(
    round(
        least_consistent_seller[
            "coefficient_of_variation"
        ],
        4
    )
)


# ---------------------------------------------------------
# Step 13: Consistency Summary
# ---------------------------------------------------------

print("\nSeller Revenue Consistency Summary:")

print(
    "High Consistency Sellers:"
)

print(
    len(high_consistency_sellers)
)

print(
    "\nMedium Consistency Sellers:"
)

print(
    len(medium_consistency_sellers)
)

print(
    "\nLow Consistency Sellers:"
)

print(
    len(low_consistency_sellers)
)

print(
    "\nHighest Consistency Score:"
)

print(
    seller_consistency[
        "consistency_score"
    ].max()
)


# ---------------------------------------------------------
# Step 14: Close Connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Completion Message
# ---------------------------------------------------------

print(
    "\nStep 59 Seller Revenue Consistency Analysis "
    "completed successfully."
)