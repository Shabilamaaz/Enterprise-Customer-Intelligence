import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 73: Seller Performance Category Analysis
# ============================================================

print("\n============================================================")
print("Step 73: Seller Performance Category Analysis")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Find Database
# ============================================================

db_path = (
    project_root
    / "database"
    / "customer_intelligence.db"
)

print("\nDatabase path:")
print(db_path)


if not db_path.exists():
    raise FileNotFoundError(
        "\nERROR: customer_intelligence.db was not found.\n"
        f"Expected location:\n{db_path}"
    )


# ============================================================
# Step 3: Connect to Database
# ============================================================

connection = sqlite3.connect(str(db_path))

print("\nDatabase connection successful.")


# ============================================================
# Step 4: Load Seller Performance Data
# ============================================================

query = """
SELECT

    oi.seller_id,

    COUNT(DISTINCT oi.order_id)
        AS total_orders,

    COUNT(DISTINCT o.customer_id)
        AS unique_customers,

    SUM(oi.price)
        AS total_revenue,

    SUM(oi.freight_value)
        AS total_freight,

    AVG(oi.price)
        AS average_order_value

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

WHERE o.order_status
NOT IN ('canceled', 'unavailable')

GROUP BY oi.seller_id
"""


seller_data = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# Step 5: Validate Data
# ============================================================

print(
    f"\nTotal sellers analyzed: "
    f"{len(seller_data)}"
)


if seller_data.empty:
    connection.close()

    raise RuntimeError(
        "\nERROR: No seller performance data was returned."
    )


# ============================================================
# Step 6: Calculate Revenue per Customer
# ============================================================

seller_data["revenue_per_customer"] = (
    seller_data["total_revenue"]
    /
    seller_data["unique_customers"]
)


seller_data["revenue_per_customer"] = (
    seller_data["revenue_per_customer"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 7: Calculate Performance Scores
# ============================================================

seller_data["revenue_score"] = (
    seller_data["total_revenue"]
    /
    seller_data["total_revenue"].max()
) * 100


seller_data["order_score"] = (
    seller_data["total_orders"]
    /
    seller_data["total_orders"].max()
) * 100


seller_data["customer_score"] = (
    seller_data["unique_customers"]
    /
    seller_data["unique_customers"].max()
) * 100


seller_data["aov_score"] = (
    seller_data["average_order_value"]
    /
    seller_data["average_order_value"].max()
) * 100


# ============================================================
# Step 8: Overall Performance Score
# ============================================================

seller_data["performance_score"] = (
    seller_data["revenue_score"] * 0.40
    +
    seller_data["order_score"] * 0.25
    +
    seller_data["customer_score"] * 0.20
    +
    seller_data["aov_score"] * 0.15
)


seller_data["performance_score"] = (
    seller_data["performance_score"]
    .clip(lower=0, upper=100)
    .round(2)
)


# ============================================================
# Step 9: Performance Category
# ============================================================

def classify_performance(score):

    if score >= 70:
        return "Excellent Performer"

    elif score >= 50:
        return "Strong Performer"

    elif score >= 30:
        return "Average Performer"

    elif score >= 15:
        return "Weak Performer"

    else:
        return "Low Performer"


seller_data["performance_category"] = (
    seller_data["performance_score"]
    .apply(classify_performance)
)


# ============================================================
# Step 10: Category Summary
# ============================================================

category_summary = (
    seller_data
    .groupby("performance_category")
    .agg(
        seller_count=(
            "seller_id",
            "count"
        ),

        total_revenue=(
            "total_revenue",
            "sum"
        ),

        average_revenue=(
            "total_revenue",
            "mean"
        ),

        average_orders=(
            "total_orders",
            "mean"
        ),

        average_customers=(
            "unique_customers",
            "mean"
        ),

        average_order_value=(
            "average_order_value",
            "mean"
        ),

        average_performance_score=(
            "performance_score",
            "mean"
        )
    )
    .reset_index()
)


# ============================================================
# Step 11: Category Percentage
# ============================================================

total_sellers = (
    category_summary["seller_count"]
    .sum()
)


category_summary["seller_percentage"] = (
    category_summary["seller_count"]
    /
    total_sellers
) * 100


# ============================================================
# Step 12: Revenue Contribution
# ============================================================

total_revenue = (
    category_summary["total_revenue"]
    .sum()
)


category_summary["revenue_contribution"] = (
    category_summary["total_revenue"]
    /
    total_revenue
) * 100


# ============================================================
# Step 13: Round Results
# ============================================================

numeric_columns = [
    "total_revenue",
    "average_revenue",
    "average_orders",
    "average_customers",
    "average_order_value",
    "average_performance_score",
    "seller_percentage",
    "revenue_contribution"
]


category_summary[numeric_columns] = (
    category_summary[numeric_columns]
    .round(2)
)


# ============================================================
# Step 14: Sort Categories
# ============================================================

category_order = [
    "Excellent Performer",
    "Strong Performer",
    "Average Performer",
    "Weak Performer",
    "Low Performer"
]


category_summary["category_order"] = (
    category_summary["performance_category"]
    .map(
        {
            category: index
            for index, category
            in enumerate(category_order)
        }
    )
)


category_summary = (
    category_summary
    .sort_values("category_order")
    .drop(columns=["category_order"])
    .reset_index(drop=True)
)


# ============================================================
# Step 15: Display Category Summary
# ============================================================

print("\n============================================================")
print("Seller Performance Category Summary")
print("============================================================")


print(
    category_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 16: Seller Distribution
# ============================================================

print("\n============================================================")
print("Seller Distribution by Performance")
print("============================================================")


for _, row in category_summary.iterrows():

    print(
        f"{row['performance_category']}: "
        f"{int(row['seller_count'])} sellers "
        f"({row['seller_percentage']:.2f}%)"
    )


# ============================================================
# Step 17: Revenue Contribution
# ============================================================

print("\n============================================================")
print("Revenue Contribution by Performance Category")
print("============================================================")


for _, row in category_summary.iterrows():

    print(
        f"{row['performance_category']}: "
        f"{row['revenue_contribution']:.2f}%"
    )


# ============================================================
# Step 18: Highest Revenue Category
# ============================================================

highest_revenue_category = (
    category_summary.loc[
        category_summary[
            "total_revenue"
        ].idxmax()
    ]
)


print("\n============================================================")
print("Highest Revenue Performance Category")
print("============================================================")


print(
    f"Category            : "
    f"{highest_revenue_category['performance_category']}"
)

print(
    f"Seller Count        : "
    f"{int(highest_revenue_category['seller_count'])}"
)

print(
    f"Total Revenue       : "
    f"{highest_revenue_category['total_revenue']:.2f}"
)

print(
    f"Revenue Contribution: "
    f"{highest_revenue_category['revenue_contribution']:.2f}%"
)


# ============================================================
# Step 19: Highest Average Score Category
# ============================================================

highest_score_category = (
    category_summary.loc[
        category_summary[
            "average_performance_score"
        ].idxmax()
    ]
)


print("\n============================================================")
print("Highest Average Performance Category")
print("============================================================")


print(
    f"Category       : "
    f"{highest_score_category['performance_category']}"
)

print(
    f"Average Score  : "
    f"{highest_score_category['average_performance_score']:.2f}"
)

print(
    f"Average Revenue: "
    f"{highest_score_category['average_revenue']:.2f}"
)


# ============================================================
# Step 20: Best Seller
# ============================================================

best_seller = (
    seller_data
    .sort_values(
        "performance_score",
        ascending=False
    )
    .iloc[0]
)


print("\n============================================================")
print("Best Performing Seller")
print("============================================================")


print(
    f"Seller ID         : "
    f"{best_seller['seller_id']}"
)

print(
    f"Performance Score : "
    f"{best_seller['performance_score']:.2f}"
)

print(
    f"Category          : "
    f"{best_seller['performance_category']}"
)

print(
    f"Total Revenue     : "
    f"{best_seller['total_revenue']:.2f}"
)

print(
    f"Total Orders      : "
    f"{int(best_seller['total_orders'])}"
)


# ============================================================
# Step 21: Save Category Summary
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_performance_category_summary.csv"
)


category_summary.to_csv(
    output_path,
    index=False
)


print("\nCategory summary saved to:")
print(output_path)


# ============================================================
# Step 22: Save Detailed Seller Performance
# ============================================================

detail_path = (
    project_root
    / "data"
    / "seller_performance_category_detail.csv"
)


seller_data[
    [
        "seller_id",
        "total_orders",
        "unique_customers",
        "total_revenue",
        "average_order_value",
        "performance_score",
        "performance_category"
    ]
].to_csv(
    detail_path,
    index=False
)


print("\nDetailed seller performance saved to:")
print(detail_path)


# ============================================================
# Step 23: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 73 Seller Performance Category Analysis "
    "completed successfully."
)
print("============================================================")