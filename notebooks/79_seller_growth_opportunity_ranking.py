import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 79: Seller Growth Opportunity Ranking
# ============================================================

print("\n============================================================")
print("Step 79: Seller Growth Opportunity Ranking")
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
# Step 4: Load Seller Performance
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

    AVG(oi.price)
        AS average_order_value,

    SUM(oi.freight_value)
        AS total_freight_cost

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
        "\nERROR: No seller performance data was returned."
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
# Step 7: Calculate Revenue Score
# ============================================================

seller_data["revenue_score"] = (
    seller_data["total_revenue"]
    /
    seller_data["total_revenue"].max()
) * 100


# ============================================================
# Step 8: Calculate Order Score
# ============================================================

seller_data["order_score"] = (
    seller_data["total_orders"]
    /
    seller_data["total_orders"].max()
) * 100


# ============================================================
# Step 9: Calculate Customer Score
# ============================================================

seller_data["customer_score"] = (
    seller_data["unique_customers"]
    /
    seller_data["unique_customers"].max()
) * 100


# ============================================================
# Step 10: Calculate Profit Score
# ============================================================

seller_data["profit_score"] = (
    seller_data["profit"]
    /
    seller_data["profit"].max()
) * 100


# ============================================================
# Step 11: Calculate AOV Score
# ============================================================

seller_data["aov_score"] = (
    seller_data["average_order_value"]
    /
    seller_data["average_order_value"].max()
) * 100


# ============================================================
# Step 12: Overall Opportunity Score
# ============================================================

seller_data["opportunity_score"] = (
    seller_data["revenue_score"] * 0.30
    +
    seller_data["profit_score"] * 0.25
    +
    seller_data["order_score"] * 0.20
    +
    seller_data["customer_score"] * 0.15
    +
    seller_data["aov_score"] * 0.10
)


seller_data["opportunity_score"] = (
    seller_data["opportunity_score"]
    .clip(
        lower=0,
        upper=100
    )
    .round(2)
)


# ============================================================
# Step 13: Opportunity Category
# ============================================================

def classify_opportunity(score):

    if score >= 70:
        return "High Opportunity"

    elif score >= 50:
        return "Good Opportunity"

    elif score >= 30:
        return "Moderate Opportunity"

    elif score >= 15:
        return "Low Opportunity"

    else:
        return "Minimal Opportunity"


seller_data["opportunity_category"] = (
    seller_data["opportunity_score"]
    .apply(classify_opportunity)
)


# ============================================================
# Step 14: Rank Sellers
# ============================================================

seller_data = (
    seller_data
    .sort_values(
        by=[
            "opportunity_score",
            "total_revenue",
            "profit"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )
    .reset_index(drop=True)
)


seller_data["opportunity_rank"] = (
    seller_data.index + 1
)


# ============================================================
# Step 15: Display Ranking
# ============================================================

result_columns = [
    "opportunity_rank",
    "seller_id",
    "total_orders",
    "unique_customers",
    "total_revenue",
    "total_freight_cost",
    "profit",
    "average_order_value",
    "opportunity_score",
    "opportunity_category"
]


print("\n============================================================")
print("Seller Growth Opportunity Ranking")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 16: Top 10 Sellers
# ============================================================

print("\n============================================================")
print("Top 10 Seller Growth Opportunities")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# Step 17: Category Summary
# ============================================================

category_summary = (
    seller_data
    .groupby("opportunity_category")
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

        average_score=(
            "opportunity_score",
            "mean"
        )
    )
    .reset_index()
)


category_summary["average_score"] = (
    category_summary["average_score"]
    .round(2)
)


print("\n============================================================")
print("Opportunity Category Summary")
print("============================================================")


print(
    category_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 18: Best Seller
# ============================================================

best_seller = seller_data.iloc[0]


print("\n============================================================")
print("Highest Opportunity Seller")
print("============================================================")


print(
    f"Seller ID        : "
    f"{best_seller['seller_id']}"
)

print(
    f"Rank             : "
    f"{int(best_seller['opportunity_rank'])}"
)

print(
    f"Revenue          : "
    f"{best_seller['total_revenue']:.2f}"
)

print(
    f"Profit           : "
    f"{best_seller['profit']:.2f}"
)

print(
    f"Orders           : "
    f"{int(best_seller['total_orders'])}"
)

print(
    f"Customers        : "
    f"{int(best_seller['unique_customers'])}"
)

print(
    f"Opportunity Score: "
    f"{best_seller['opportunity_score']:.2f}"
)

print(
    f"Category         : "
    f"{best_seller['opportunity_category']}"
)


# ============================================================
# Step 19: Overall Statistics
# ============================================================

average_score = (
    seller_data["opportunity_score"]
    .mean()
)

highest_score = (
    seller_data["opportunity_score"]
    .max()
)

lowest_score = (
    seller_data["opportunity_score"]
    .min()
)


print("\n============================================================")
print("Opportunity Ranking Statistics")
print("============================================================")


print(
    f"Average Score : "
    f"{average_score:.2f}"
)

print(
    f"Highest Score : "
    f"{highest_score:.2f}"
)

print(
    f"Lowest Score  : "
    f"{lowest_score:.2f}"
)


# ============================================================
# Step 20: Save Ranking
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_growth_opportunity_ranking.csv"
)


seller_data[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nSeller opportunity ranking saved to:")
print(output_path)


# ============================================================
# Step 21: Save Category Summary
# ============================================================

summary_path = (
    project_root
    / "data"
    / "seller_growth_opportunity_ranking_summary.csv"
)


category_summary.to_csv(
    summary_path,
    index=False
)


print("\nOpportunity category summary saved to:")
print(summary_path)


# ============================================================
# Step 22: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 79 Seller Growth Opportunity Ranking "
    "completed successfully."
)
print("============================================================")