import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 81: Seller Profitability Category Analysis
# ============================================================

print("\n============================================================")
print("Step 81: Seller Profitability Category Analysis")
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
# Step 4: Load Seller Data
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
        AS total_freight_cost,

    AVG(oi.price)
        AS average_order_value

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

WHERE
    o.order_status
    NOT IN ('canceled', 'unavailable')

GROUP BY
    oi.seller_id
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
        "\nERROR: No seller data was returned."
    )


# ============================================================
# Step 6: Calculate Profit
# ============================================================

seller_data["profit"] = (
    seller_data["total_revenue"]
    -
    seller_data["total_freight_cost"]
)


# ============================================================
# Step 7: Calculate Profit Margin
# ============================================================

seller_data["profit_margin"] = (
    seller_data["profit"]
    /
    seller_data["total_revenue"]
) * 100


seller_data["profit_margin"] = (
    seller_data["profit_margin"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 8: Calculate Profit per Order
# ============================================================

seller_data["profit_per_order"] = (
    seller_data["profit"]
    /
    seller_data["total_orders"]
)


# ============================================================
# Step 9: Calculate Profitability Score
# ============================================================

revenue_score = (
    seller_data["total_revenue"]
    /
    seller_data["total_revenue"].max()
) * 100


profit_score = (
    seller_data["profit"]
    /
    seller_data["profit"].max()
) * 100


margin_max = seller_data["profit_margin"].max()


if margin_max > 0:

    margin_score = (
        seller_data["profit_margin"]
        /
        margin_max
    ) * 100

else:

    margin_score = 0


seller_data["profitability_score"] = (
    revenue_score * 0.30
    +
    profit_score * 0.40
    +
    margin_score * 0.30
)


seller_data["profitability_score"] = (
    seller_data["profitability_score"]
    .clip(
        lower=0,
        upper=100
    )
    .round(2)
)


# ============================================================
# Step 10: Profitability Category
# ============================================================

def classify_profitability(row):

    if (
        row["profit"] > 0
        and row["profitability_score"] >= 70
        and row["profit_margin"] >= 30
    ):
        return "Excellent"

    elif (
        row["profit"] > 0
        and row["profitability_score"] >= 50
        and row["profit_margin"] >= 20
    ):
        return "High"

    elif (
        row["profit"] > 0
        and row["profitability_score"] >= 30
        and row["profit_margin"] >= 10
    ):
        return "Moderate"

    elif row["profit"] > 0:
        return "Low"

    else:
        return "Negative"


seller_data["profitability_category"] = (
    seller_data
    .apply(
        classify_profitability,
        axis=1
    )
)


# ============================================================
# Step 11: Create Category Summary
# ============================================================

category_summary = (
    seller_data
    .groupby("profitability_category")
    .agg(
        seller_count=(
            "seller_id",
            "count"
        ),

        total_revenue=(
            "total_revenue",
            "sum"
        ),

        total_profit=(
            "profit",
            "sum"
        ),

        average_profit=(
            "profit",
            "mean"
        ),

        average_margin=(
            "profit_margin",
            "mean"
        ),

        average_profit_per_order=(
            "profit_per_order",
            "mean"
        ),

        average_score=(
            "profitability_score",
            "mean"
        )
    )
    .reset_index()
)


# ============================================================
# Step 12: Seller Percentage
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
# Step 13: Revenue Contribution
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
# Step 14: Profit Contribution
# ============================================================

total_profit = (
    category_summary["total_profit"]
    .sum()
)


if total_profit != 0:

    category_summary["profit_contribution"] = (
        category_summary["total_profit"]
        /
        total_profit
    ) * 100

else:

    category_summary["profit_contribution"] = 0


# ============================================================
# Step 15: Round Values
# ============================================================

numeric_columns = [
    "total_revenue",
    "total_profit",
    "average_profit",
    "average_margin",
    "average_profit_per_order",
    "average_score",
    "seller_percentage",
    "revenue_contribution",
    "profit_contribution"
]


category_summary[numeric_columns] = (
    category_summary[numeric_columns]
    .round(2)
)


# ============================================================
# Step 16: Sort Categories
# ============================================================

category_order = [
    "Excellent",
    "High",
    "Moderate",
    "Low",
    "Negative"
]


category_summary["category_order"] = (
    category_summary["profitability_category"]
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
# Step 17: Display Category Analysis
# ============================================================

print("\n============================================================")
print("Seller Profitability Category Analysis")
print("============================================================")


print(
    category_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 18: Category Distribution
# ============================================================

print("\n============================================================")
print("Profitability Category Distribution")
print("============================================================")


for _, row in category_summary.iterrows():

    print(
        f"{row['profitability_category']}: "
        f"{int(row['seller_count'])} sellers "
        f"({row['seller_percentage']:.2f}%)"
    )


# ============================================================
# Step 19: Revenue Contribution
# ============================================================

print("\n============================================================")
print("Revenue Contribution by Category")
print("============================================================")


for _, row in category_summary.iterrows():

    print(
        f"{row['profitability_category']}: "
        f"{row['revenue_contribution']:.2f}%"
    )


# ============================================================
# Step 20: Profit Contribution
# ============================================================

print("\n============================================================")
print("Profit Contribution by Category")
print("============================================================")


for _, row in category_summary.iterrows():

    print(
        f"{row['profitability_category']}: "
        f"{row['profit_contribution']:.2f}%"
    )


# ============================================================
# Step 21: Best Profitability Category
# ============================================================

best_category = (
    category_summary.loc[
        category_summary["average_score"].idxmax()
    ]
)


print("\n============================================================")
print("Best Profitability Category")
print("============================================================")


print(
    f"Category        : "
    f"{best_category['profitability_category']}"
)

print(
    f"Seller Count    : "
    f"{int(best_category['seller_count'])}"
)

print(
    f"Average Margin  : "
    f"{best_category['average_margin']:.2f}%"
)

print(
    f"Average Score   : "
    f"{best_category['average_score']:.2f}"
)


# ============================================================
# Step 22: Best Seller
# ============================================================

best_seller = (
    seller_data
    .sort_values(
        by="profitability_score",
        ascending=False
    )
    .iloc[0]
)


print("\n============================================================")
print("Most Profitable Seller")
print("============================================================")


print(
    f"Seller ID       : "
    f"{best_seller['seller_id']}"
)

print(
    f"Revenue         : "
    f"{best_seller['total_revenue']:.2f}"
)

print(
    f"Profit          : "
    f"{best_seller['profit']:.2f}"
)

print(
    f"Profit Margin   : "
    f"{best_seller['profit_margin']:.2f}%"
)

print(
    f"Profit per Order: "
    f"{best_seller['profit_per_order']:.2f}"
)

print(
    f"Score           : "
    f"{best_seller['profitability_score']:.2f}"
)

print(
    f"Category        : "
    f"{best_seller['profitability_category']}"
)


# ============================================================
# Step 23: Negative Profit Analysis
# ============================================================

negative_sellers = seller_data[
    seller_data["profit"] < 0
]


print("\n============================================================")
print("Negative Profit Analysis")
print("============================================================")


print(
    f"Negative Profit Sellers: "
    f"{len(negative_sellers)}"
)


if not negative_sellers.empty:

    print(
        negative_sellers[
            [
                "seller_id",
                "total_revenue",
                "total_freight_cost",
                "profit",
                "profit_margin"
            ]
        ]
        .sort_values(
            by="profit"
        )
        .head(10)
        .to_string(index=False)
    )

else:

    print(
        "No negative-profit sellers identified."
    )


# ============================================================
# Step 24: Save Category Summary
# ============================================================

summary_path = (
    project_root
    / "data"
    / "seller_profitability_category_analysis.csv"
)


category_summary.to_csv(
    summary_path,
    index=False
)


print("\nProfitability category analysis saved to:")
print(summary_path)


# ============================================================
# Step 25: Save Detailed Seller Data
# ============================================================

detail_path = (
    project_root
    / "data"
    / "seller_profitability_category_detail.csv"
)


seller_data[
    [
        "seller_id",
        "total_orders",
        "unique_customers",
        "total_revenue",
        "total_freight_cost",
        "profit",
        "profit_margin",
        "profit_per_order",
        "profitability_score",
        "profitability_category"
    ]
].to_csv(
    detail_path,
    index=False
)


print("\nDetailed seller profitability data saved to:")
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
    "Step 81 Seller Profitability Category Analysis "
    "completed successfully."
)
print("============================================================")