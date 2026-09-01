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
# Connect to Database
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
WHERE
    o.order_purchase_timestamp IS NOT NULL
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


# =========================================================
# Step 2: Calculate Average Revenue
# =========================================================

seller_stability = (
    seller_monthly_revenue
    .groupby("seller_id", as_index=False)
    .agg(
        average_monthly_revenue=(
            "monthly_revenue",
            "mean"
        ),
        highest_monthly_revenue=(
            "monthly_revenue",
            "max"
        ),
        lowest_monthly_revenue=(
            "monthly_revenue",
            "min"
        ),
        revenue_months=(
            "monthly_revenue",
            "count"
        )
    )
)


# =========================================================
# Step 3: Revenue Standard Deviation
# =========================================================

revenue_std = (
    seller_monthly_revenue
    .groupby("seller_id")["monthly_revenue"]
    .std()
    .reset_index(
        name="revenue_standard_deviation"
    )
)


seller_stability = seller_stability.merge(
    revenue_std,
    on="seller_id",
    how="left"
)


seller_stability[
    "revenue_standard_deviation"
] = seller_stability[
    "revenue_standard_deviation"
].fillna(0)


# =========================================================
# Step 4: Revenue Range
# =========================================================

seller_stability["revenue_range"] = (
    seller_stability["highest_monthly_revenue"]
    -
    seller_stability["lowest_monthly_revenue"]
)


# =========================================================
# Step 5: Coefficient of Variation
# =========================================================

seller_stability["coefficient_of_variation"] = (
    seller_stability[
        "revenue_standard_deviation"
    ]
    /
    seller_stability[
        "average_monthly_revenue"
    ]
    * 100
)


seller_stability[
    "coefficient_of_variation"
] = seller_stability[
    "coefficient_of_variation"
].replace(
    [float("inf"), -float("inf")],
    0
)


seller_stability[
    "coefficient_of_variation"
] = seller_stability[
    "coefficient_of_variation"
].fillna(0)


# =========================================================
# Step 6: Revenue Stability Score
# =========================================================

seller_stability["stability_score"] = (
    100
    -
    seller_stability[
        "coefficient_of_variation"
    ]
)


seller_stability["stability_score"] = (
    seller_stability[
        "stability_score"
    ]
    .clip(
        lower=0,
        upper=100
    )
    .round(2)
)


# =========================================================
# Step 7: Stability Classification
# =========================================================

def classify_stability(row):

    if (
        row["coefficient_of_variation"] <= 50
        and row["revenue_months"] >= 3
    ):
        return "High Stability"

    elif (
        row["coefficient_of_variation"] <= 100
        and row["revenue_months"] >= 3
    ):
        return "Medium Stability"

    else:
        return "Low Stability"


seller_stability[
    "stability_category"
] = seller_stability.apply(
    classify_stability,
    axis=1
)


# =========================================================
# Step 8: Top 10 Most Stable Sellers
# =========================================================

top_stable_sellers = (
    seller_stability
    .sort_values(
        "stability_score",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Most Stable Sellers:")

print(
    top_stable_sellers[
        [
            "seller_id",
            "average_monthly_revenue",
            "highest_monthly_revenue",
            "lowest_monthly_revenue",
            "coefficient_of_variation",
            "stability_score",
            "stability_category"
        ]
    ]
)


# =========================================================
# Step 9: High Stability Sellers
# =========================================================

high_stability_sellers = seller_stability[
    seller_stability[
        "stability_category"
    ]
    == "High Stability"
]


print("\nHigh Stability Sellers:")

print(
    len(high_stability_sellers)
)


# =========================================================
# Step 10: Medium Stability Sellers
# =========================================================

medium_stability_sellers = seller_stability[
    seller_stability[
        "stability_category"
    ]
    == "Medium Stability"
]


print("\nMedium Stability Sellers:")

print(
    len(medium_stability_sellers)
)


# =========================================================
# Step 11: Low Stability Sellers
# =========================================================

low_stability_sellers = seller_stability[
    seller_stability[
        "stability_category"
    ]
    == "Low Stability"
]


print("\nLow Stability Sellers:")

print(
    len(low_stability_sellers)
)


# =========================================================
# Step 12: Most Stable Seller
# =========================================================

most_stable_seller = (
    seller_stability
    .sort_values(
        "stability_score",
        ascending=False
    )
    .iloc[0]
)


print("\nMost Stable Seller:")

print(
    most_stable_seller[
        "seller_id"
    ]
)

print(
    "Stability Score:"
)

print(
    most_stable_seller[
        "stability_score"
    ]
)

print(
    "Coefficient of Variation:"
)

print(
    round(
        most_stable_seller[
            "coefficient_of_variation"
        ],
        2
    )
)


# =========================================================
# Step 13: Least Stable Seller
# =========================================================

least_stable_seller = (
    seller_stability
    .sort_values(
        "stability_score",
        ascending=True
    )
    .iloc[0]
)


print("\nLeast Stable Seller:")

print(
    least_stable_seller[
        "seller_id"
    ]
)

print(
    "Stability Score:"
)

print(
    least_stable_seller[
        "stability_score"
    ]
)

print(
    "Coefficient of Variation:"
)

print(
    round(
        least_stable_seller[
            "coefficient_of_variation"
        ],
        2
    )
)


# =========================================================
# Step 14: Stability Summary
# =========================================================

print("\nSeller Revenue Stability Summary:")

print(
    "High Stability Sellers:"
)

print(
    len(high_stability_sellers)
)

print(
    "\nMedium Stability Sellers:"
)

print(
    len(medium_stability_sellers)
)

print(
    "\nLow Stability Sellers:"
)

print(
    len(low_stability_sellers)
)

print(
    "\nHighest Stability Score:"
)

print(
    seller_stability[
        "stability_score"
    ].max()
)

print(
    "\nLowest Stability Score:"
)

print(
    seller_stability[
        "stability_score"
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
    "\nStep 56 Seller Revenue Stability Analysis "
    "completed successfully."
)