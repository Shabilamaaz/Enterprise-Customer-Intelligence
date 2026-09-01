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
# Step 1: Seller Product Revenue
# ---------------------------------------------------------

query = """
SELECT
    oi.seller_id,
    oi.product_id,
    ROUND(SUM(oi.price), 2) AS product_revenue
FROM order_items oi
GROUP BY
    oi.seller_id,
    oi.product_id
ORDER BY
    oi.seller_id,
    product_revenue DESC
"""

seller_product_revenue = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Product Revenue:")
print(
    seller_product_revenue.head(10)
)


# ---------------------------------------------------------
# Step 2: Seller Revenue Summary
# ---------------------------------------------------------

seller_revenue_summary = (
    seller_product_revenue
    .groupby("seller_id", as_index=False)
    .agg(
        total_revenue=(
            "product_revenue",
            "sum"
        ),
        product_count=(
            "product_id",
            "nunique"
        )
    )
)


# ---------------------------------------------------------
# Step 3: Revenue Share by Product
# ---------------------------------------------------------

seller_product_revenue = seller_product_revenue.merge(
    seller_revenue_summary[
        [
            "seller_id",
            "total_revenue"
        ]
    ],
    on="seller_id",
    how="left"
)


seller_product_revenue["revenue_share"] = (
    seller_product_revenue["product_revenue"]
    /
    seller_product_revenue["total_revenue"]
)


# ---------------------------------------------------------
# Step 4: Revenue Concentration
# ---------------------------------------------------------

seller_concentration = (
    seller_product_revenue
    .groupby("seller_id", as_index=False)
    .agg(
        highest_product_share=(
            "revenue_share",
            "max"
        ),
        average_product_share=(
            "revenue_share",
            "mean"
        )
    )
)


# ---------------------------------------------------------
# Step 5: Diversification Score
# ---------------------------------------------------------

seller_diversification = seller_revenue_summary.merge(
    seller_concentration,
    on="seller_id",
    how="left"
)


seller_diversification["diversification_score"] = (
    seller_diversification["product_count"]
    *
    (
        1
        -
        seller_diversification["highest_product_share"]
    )
)


seller_diversification["diversification_score"] = (
    seller_diversification[
        "diversification_score"
    ]
    .round(2)
)


# ---------------------------------------------------------
# Step 6: Diversification Classification
# ---------------------------------------------------------

def classify_diversification(row):

    if (
        row["product_count"] >= 10
        and row["highest_product_share"] <= 0.40
    ):
        return "High Diversification"

    elif (
        row["product_count"] >= 5
        and row["highest_product_share"] <= 0.70
    ):
        return "Medium Diversification"

    else:
        return "Low Diversification"


seller_diversification[
    "diversification_category"
] = seller_diversification.apply(
    classify_diversification,
    axis=1
)


# ---------------------------------------------------------
# Step 7: Top Diversified Sellers
# ---------------------------------------------------------

top_diversified_sellers = (
    seller_diversification
    .sort_values(
        "diversification_score",
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Sellers by Revenue Diversification:")

print(
    top_diversified_sellers[
        [
            "seller_id",
            "total_revenue",
            "product_count",
            "highest_product_share",
            "diversification_score",
            "diversification_category"
        ]
    ]
)


# ---------------------------------------------------------
# Step 8: High Diversification Sellers
# ---------------------------------------------------------

high_diversification_sellers = (
    seller_diversification[
        seller_diversification[
            "diversification_category"
        ]
        == "High Diversification"
    ]
)


print("\nHigh Diversification Sellers:")
print(
    len(high_diversification_sellers)
)


# ---------------------------------------------------------
# Step 9: Medium Diversification Sellers
# ---------------------------------------------------------

medium_diversification_sellers = (
    seller_diversification[
        seller_diversification[
            "diversification_category"
        ]
        == "Medium Diversification"
    ]
)


print("\nMedium Diversification Sellers:")
print(
    len(medium_diversification_sellers)
)


# ---------------------------------------------------------
# Step 10: Low Diversification Sellers
# ---------------------------------------------------------

low_diversification_sellers = (
    seller_diversification[
        seller_diversification[
            "diversification_category"
        ]
        == "Low Diversification"
    ]
)


print("\nLow Diversification Sellers:")
print(
    len(low_diversification_sellers)
)


# ---------------------------------------------------------
# Step 11: Strongest Diversified Seller
# ---------------------------------------------------------

strongest_diversification = (
    seller_diversification
    .sort_values(
        "diversification_score",
        ascending=False
    )
    .iloc[0]
)


print("\nStrongest Diversified Seller:")

print(
    strongest_diversification[
        "seller_id"
    ]
)

print(
    "Diversification Score:"
)

print(
    strongest_diversification[
        "diversification_score"
    ]
)

print(
    "Product Count:"
)

print(
    strongest_diversification[
        "product_count"
    ]
)


# ---------------------------------------------------------
# Step 12: Least Diversified Seller
# ---------------------------------------------------------

weakest_diversification = (
    seller_diversification
    .sort_values(
        "diversification_score",
        ascending=True
    )
    .iloc[0]
)


print("\nLeast Diversified Seller:")

print(
    weakest_diversification[
        "seller_id"
    ]
)

print(
    "Diversification Score:"
)

print(
    weakest_diversification[
        "diversification_score"
    ]
)

print(
    "Product Count:"
)

print(
    weakest_diversification[
        "product_count"
    ]
)


# ---------------------------------------------------------
# Step 13: Diversification Summary
# ---------------------------------------------------------

print("\nSeller Revenue Diversification Summary:")

print(
    "High Diversification Sellers:"
)

print(
    len(high_diversification_sellers)
)

print(
    "\nMedium Diversification Sellers:"
)

print(
    len(medium_diversification_sellers)
)

print(
    "\nLow Diversification Sellers:"
)

print(
    len(low_diversification_sellers)
)

print(
    "\nHighest Diversification Score:"
)

print(
    seller_diversification[
        "diversification_score"
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
    "\nStep 55 Seller Revenue Diversification Analysis "
    "completed successfully."
)