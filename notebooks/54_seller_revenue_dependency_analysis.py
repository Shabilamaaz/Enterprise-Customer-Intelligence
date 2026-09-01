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
# Step 1: Seller Revenue
# ---------------------------------------------------------

query = """
SELECT
    oi.seller_id,
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
WHERE o.order_purchase_timestamp IS NOT NULL
GROUP BY
    oi.seller_id
ORDER BY
    total_revenue DESC
"""

seller_revenue = pd.read_sql_query(
    query,
    connection
)


print("\nSeller Revenue:")
print(
    seller_revenue.head(10)
)


# ---------------------------------------------------------
# Step 2: Total Marketplace Revenue
# ---------------------------------------------------------

total_revenue = seller_revenue[
    "total_revenue"
].sum()


print("\nTotal Marketplace Revenue:")
print(
    round(total_revenue, 2)
)


# ---------------------------------------------------------
# Step 3: Revenue Share
# ---------------------------------------------------------

seller_revenue["revenue_share_percentage"] = (
    seller_revenue["total_revenue"]
    /
    total_revenue
    * 100
)


seller_revenue[
    "revenue_share_percentage"
] = seller_revenue[
    "revenue_share_percentage"
].round(2)


# ---------------------------------------------------------
# Step 4: Cumulative Revenue Share
# ---------------------------------------------------------

seller_revenue[
    "cumulative_revenue_share"
] = (
    seller_revenue[
        "revenue_share_percentage"
    ].cumsum()
)


seller_revenue[
    "cumulative_revenue_share"
] = (
    seller_revenue[
        "cumulative_revenue_share"
    ].round(2)
)


print("\nSeller Revenue Share:")
print(
    seller_revenue.head(10)
)


# ---------------------------------------------------------
# Step 5: Top 10 Seller Dependency
# ---------------------------------------------------------

top_10_sellers = (
    seller_revenue
    .head(10)
)


top_10_revenue_share = (
    top_10_sellers[
        "revenue_share_percentage"
    ].sum()
)


print("\nTop 10 Seller Revenue Dependency:")

print(
    round(
        top_10_revenue_share,
        2
    )
)


# ---------------------------------------------------------
# Step 6: Top 20 Seller Dependency
# ---------------------------------------------------------

top_20_sellers = (
    seller_revenue
    .head(20)
)


top_20_revenue_share = (
    top_20_sellers[
        "revenue_share_percentage"
    ].sum()
)


print("\nTop 20 Seller Revenue Dependency:")

print(
    round(
        top_20_revenue_share,
        2
    )
)


# ---------------------------------------------------------
# Step 7: Revenue Dependency Classification
# ---------------------------------------------------------

def classify_dependency(share):

    if share >= 1.0:
        return "High Dependency"

    elif share >= 0.25:
        return "Medium Dependency"

    else:
        return "Low Dependency"


seller_revenue[
    "dependency_category"
] = seller_revenue[
    "revenue_share_percentage"
].apply(
    classify_dependency
)


# ---------------------------------------------------------
# Step 8: Dependency Summary
# ---------------------------------------------------------

high_dependency_sellers = seller_revenue[
    seller_revenue[
        "dependency_category"
    ]
    == "High Dependency"
]


medium_dependency_sellers = seller_revenue[
    seller_revenue[
        "dependency_category"
    ]
    == "Medium Dependency"
]


low_dependency_sellers = seller_revenue[
    seller_revenue[
        "dependency_category"
    ]
    == "Low Dependency"
]


print("\nHigh Dependency Sellers:")
print(
    len(high_dependency_sellers)
)


print("\nMedium Dependency Sellers:")
print(
    len(medium_dependency_sellers)
)


print("\nLow Dependency Sellers:")
print(
    len(low_dependency_sellers)
)


# ---------------------------------------------------------
# Step 9: Most Revenue Dependent Seller
# ---------------------------------------------------------

most_dependent_seller = (
    seller_revenue
    .sort_values(
        "revenue_share_percentage",
        ascending=False
    )
    .iloc[0]
)


print("\nMost Revenue Dependent Seller:")

print(
    most_dependent_seller[
        "seller_id"
    ]
)

print(
    "Total Revenue:"
)

print(
    most_dependent_seller[
        "total_revenue"
    ]
)

print(
    "Revenue Share Percentage:"
)

print(
    most_dependent_seller[
        "revenue_share_percentage"
    ]
)


# ---------------------------------------------------------
# Step 10: Least Revenue Dependent Seller
# ---------------------------------------------------------

least_dependent_seller = (
    seller_revenue
    .sort_values(
        "revenue_share_percentage",
        ascending=True
    )
    .iloc[0]
)


print("\nLeast Revenue Dependent Seller:")

print(
    least_dependent_seller[
        "seller_id"
    ]
)

print(
    "Revenue Share Percentage:"
)

print(
    least_dependent_seller[
        "revenue_share_percentage"
    ]
)


# ---------------------------------------------------------
# Step 11: Revenue Dependency Summary
# ---------------------------------------------------------

print(
    "\nSeller Revenue Dependency Summary:"
)

print(
    "Total Sellers:"
)

print(
    len(seller_revenue)
)

print(
    "\nTop 10 Revenue Share:"
)

print(
    round(
        top_10_revenue_share,
        2
    )
)

print(
    "\nTop 20 Revenue Share:"
)

print(
    round(
        top_20_revenue_share,
        2
    )
)

print(
    "\nHighest Seller Revenue Share:"
)

print(
    seller_revenue[
        "revenue_share_percentage"
    ].max()
)

print(
    "\nAverage Seller Revenue Share:"
)

print(
    round(
        seller_revenue[
            "revenue_share_percentage"
        ].mean(),
        4
    )
)


# ---------------------------------------------------------
# Step 12: Close Connection
# ---------------------------------------------------------

connection.close()


# ---------------------------------------------------------
# Completion Message
# ---------------------------------------------------------

print(
    "\nStep 54 Seller Revenue Dependency Analysis "
    "completed successfully."
)