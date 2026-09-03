import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 76: Seller Growth Category Analysis
# ============================================================

print("\n============================================================")
print("Step 76: Seller Growth Category Analysis")
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
# Step 4: Load Monthly Seller Performance
# ============================================================

query = """
SELECT
    oi.seller_id,

    strftime(
        '%Y-%m',
        o.order_purchase_timestamp
    ) AS sales_month,

    COUNT(DISTINCT oi.order_id)
        AS total_orders,

    COUNT(DISTINCT o.customer_id)
        AS unique_customers,

    SUM(oi.price)
        AS total_revenue,

    AVG(oi.price)
        AS average_order_value

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

WHERE
    o.order_status
    NOT IN ('canceled', 'unavailable')

    AND o.order_purchase_timestamp IS NOT NULL

GROUP BY
    oi.seller_id,
    sales_month

ORDER BY
    oi.seller_id,
    sales_month
"""


monthly_data = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# Step 5: Validate Data
# ============================================================

print(
    f"\nMonthly seller records analyzed: "
    f"{len(monthly_data)}"
)


if monthly_data.empty:
    connection.close()

    raise RuntimeError(
        "\nERROR: No seller growth data was returned."
    )


# ============================================================
# Step 6: Calculate Previous Month Revenue
# ============================================================

monthly_data["previous_revenue"] = (
    monthly_data
    .groupby("seller_id")["total_revenue"]
    .shift(1)
)


# ============================================================
# Step 7: Calculate Revenue Growth
# ============================================================

monthly_data["revenue_growth"] = (
    monthly_data["total_revenue"]
    -
    monthly_data["previous_revenue"]
)


monthly_data["growth_percentage"] = (
    monthly_data["revenue_growth"]
    /
    monthly_data["previous_revenue"]
) * 100


monthly_data["growth_percentage"] = (
    monthly_data["growth_percentage"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 8: Growth Direction
# ============================================================

monthly_data["growth_direction"] = (
    monthly_data["revenue_growth"]
    .apply(
        lambda value:
        "Growing"
        if value > 0
        else (
            "Declining"
            if value < 0
            else "Stable"
        )
    )
)


# ============================================================
# Step 9: Create Seller Summary
# ============================================================

seller_summary = (
    monthly_data
    .groupby("seller_id")
    .agg(
        months_active=(
            "sales_month",
            "count"
        ),

        total_revenue=(
            "total_revenue",
            "sum"
        ),

        total_orders=(
            "total_orders",
            "sum"
        ),

        average_monthly_revenue=(
            "total_revenue",
            "mean"
        ),

        average_growth=(
            "growth_percentage",
            "mean"
        ),

        growth_months=(
            "growth_direction",
            lambda x:
            (x == "Growing").sum()
        ),

        declining_months=(
            "growth_direction",
            lambda x:
            (x == "Declining").sum()
        ),

        stable_months=(
            "growth_direction",
            lambda x:
            (x == "Stable").sum()
        )
    )
    .reset_index()
)


# ============================================================
# Step 10: Growth Ratio
# ============================================================

seller_summary["growth_ratio"] = (
    seller_summary["growth_months"]
    /
    seller_summary["months_active"]
)


# ============================================================
# Step 11: Calculate Growth Score
# ============================================================

seller_summary["growth_score"] = (
    seller_summary["growth_ratio"] * 70
    +
    (
        seller_summary["average_growth"]
        .clip(
            lower=-100,
            upper=100
        )
        / 100
        * 30
    )
)


seller_summary["growth_score"] = (
    seller_summary["growth_score"]
    .clip(
        lower=0,
        upper=100
    )
    .round(2)
)


# ============================================================
# Step 12: Classify Growth Category
# ============================================================

def classify_growth(row):

    if row["growth_score"] >= 70:
        return "High Growth"

    elif row["growth_score"] >= 50:
        return "Moderate Growth"

    elif row["declining_months"] > row["growth_months"]:
        return "Declining"

    else:
        return "Stable"


seller_summary["growth_category"] = (
    seller_summary
    .apply(
        classify_growth,
        axis=1
    )
)


# ============================================================
# Step 13: Category Summary
# ============================================================

category_summary = (
    seller_summary
    .groupby("growth_category")
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

        average_growth=(
            "average_growth",
            "mean"
        ),

        average_growth_score=(
            "growth_score",
            "mean"
        )
    )
    .reset_index()
)


# ============================================================
# Step 14: Seller Percentage
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
# Step 15: Revenue Contribution
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
# Step 16: Round Numeric Values
# ============================================================

numeric_columns = [
    "total_revenue",
    "average_revenue",
    "average_orders",
    "average_growth",
    "average_growth_score",
    "seller_percentage",
    "revenue_contribution"
]


category_summary[numeric_columns] = (
    category_summary[numeric_columns]
    .round(2)
)


# ============================================================
# Step 17: Sort Categories
# ============================================================

category_order = [
    "High Growth",
    "Moderate Growth",
    "Stable",
    "Declining"
]


category_summary["category_order"] = (
    category_summary["growth_category"]
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
# Step 18: Display Category Summary
# ============================================================

print("\n============================================================")
print("Seller Growth Category Summary")
print("============================================================")


print(
    category_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 19: Seller Distribution
# ============================================================

print("\n============================================================")
print("Seller Distribution by Growth Category")
print("============================================================")


for _, row in category_summary.iterrows():

    print(
        f"{row['growth_category']}: "
        f"{int(row['seller_count'])} sellers "
        f"({row['seller_percentage']:.2f}%)"
    )


# ============================================================
# Step 20: Revenue Contribution
# ============================================================

print("\n============================================================")
print("Revenue Contribution by Growth Category")
print("============================================================")


for _, row in category_summary.iterrows():

    print(
        f"{row['growth_category']}: "
        f"{row['revenue_contribution']:.2f}%"
    )


# ============================================================
# Step 21: Highest Growth Category
# ============================================================

highest_growth_category = (
    category_summary.loc[
        category_summary[
            "average_growth_score"
        ].idxmax()
    ]
)


print("\n============================================================")
print("Highest Growth Category")
print("============================================================")


print(
    f"Category       : "
    f"{highest_growth_category['growth_category']}"
)

print(
    f"Seller Count   : "
    f"{int(highest_growth_category['seller_count'])}"
)

print(
    f"Average Growth : "
    f"{highest_growth_category['average_growth']:.2f}%"
)

print(
    f"Average Score  : "
    f"{highest_growth_category['average_growth_score']:.2f}"
)


# ============================================================
# Step 22: Strongest Growing Seller
# ============================================================

strongest_seller = (
    seller_summary
    .sort_values(
        "growth_score",
        ascending=False
    )
    .iloc[0]
)


print("\n============================================================")
print("Strongest Growing Seller")
print("============================================================")


print(
    f"Seller ID      : "
    f"{strongest_seller['seller_id']}"
)

print(
    f"Growth Score   : "
    f"{strongest_seller['growth_score']:.2f}"
)

print(
    f"Average Growth : "
    f"{strongest_seller['average_growth']:.2f}%"
)

print(
    f"Growth Category: "
    f"{strongest_seller['growth_category']}"
)


# ============================================================
# Step 23: Most Declining Seller
# ============================================================

declining_seller = (
    seller_summary
    .sort_values(
        "growth_score",
        ascending=True
    )
    .iloc[0]
)


print("\n============================================================")
print("Most Declining Seller")
print("============================================================")


print(
    f"Seller ID      : "
    f"{declining_seller['seller_id']}"
)

print(
    f"Growth Score   : "
    f"{declining_seller['growth_score']:.2f}"
)

print(
    f"Average Growth : "
    f"{declining_seller['average_growth']:.2f}%"
)

print(
    f"Growth Category: "
    f"{declining_seller['growth_category']}"
)


# ============================================================
# Step 24: Save Category Summary
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_growth_category_summary.csv"
)


category_summary.to_csv(
    output_path,
    index=False
)


print("\nCategory summary saved to:")
print(output_path)


# ============================================================
# Step 25: Save Detailed Seller Growth Data
# ============================================================

detail_path = (
    project_root
    / "data"
    / "seller_growth_category_detail.csv"
)


seller_summary[
    [
        "seller_id",
        "months_active",
        "total_revenue",
        "total_orders",
        "average_monthly_revenue",
        "average_growth",
        "growth_months",
        "declining_months",
        "stable_months",
        "growth_score",
        "growth_category"
    ]
].to_csv(
    detail_path,
    index=False
)


print("\nDetailed growth data saved to:")
print(detail_path)


# ============================================================
# Step 26: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 76 Seller Growth Category Analysis "
    "completed successfully."
)
print("============================================================")