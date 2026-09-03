import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 80: Seller Profitability Performance Analysis
# ============================================================

print("\n============================================================")
print("Step 80: Seller Profitability Performance Analysis")
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
# Step 4: Load Seller Revenue and Cost Data
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
        "\nERROR: No seller profitability data was returned."
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
# Step 8: Calculate Revenue per Order
# ============================================================

seller_data["revenue_per_order"] = (
    seller_data["total_revenue"]
    /
    seller_data["total_orders"]
)


# ============================================================
# Step 9: Calculate Profit per Order
# ============================================================

seller_data["profit_per_order"] = (
    seller_data["profit"]
    /
    seller_data["total_orders"]
)


# ============================================================
# Step 10: Calculate Revenue Score
# ============================================================

seller_data["revenue_score"] = (
    seller_data["total_revenue"]
    /
    seller_data["total_revenue"].max()
) * 100


# ============================================================
# Step 11: Calculate Profit Score
# ============================================================

max_profit = seller_data["profit"].max()

if max_profit > 0:

    seller_data["profit_score"] = (
        seller_data["profit"]
        /
        max_profit
    ) * 100

else:

    seller_data["profit_score"] = 0


# ============================================================
# Step 12: Calculate Margin Score
# ============================================================

max_margin = seller_data["profit_margin"].max()

if max_margin > 0:

    seller_data["margin_score"] = (
        seller_data["profit_margin"]
        /
        max_margin
    ) * 100

else:

    seller_data["margin_score"] = 0


# ============================================================
# Step 13: Overall Profitability Score
# ============================================================

seller_data["profitability_score"] = (
    seller_data["revenue_score"] * 0.30
    +
    seller_data["profit_score"] * 0.40
    +
    seller_data["margin_score"] * 0.30
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
# Step 14: Profitability Classification
# ============================================================

def classify_profitability(row):

    if (
        row["profitability_score"] >= 70
        and row["profit_margin"] >= 30
    ):
        return "Excellent Profitability"

    elif (
        row["profitability_score"] >= 50
        and row["profit_margin"] >= 20
    ):
        return "High Profitability"

    elif (
        row["profitability_score"] >= 30
        and row["profit_margin"] >= 10
    ):
        return "Moderate Profitability"

    elif row["profit"] > 0:
        return "Low Profitability"

    else:
        return "Negative Profitability"


seller_data["profitability_category"] = (
    seller_data
    .apply(
        classify_profitability,
        axis=1
    )
)


# ============================================================
# Step 15: Rank Sellers
# ============================================================

seller_data = (
    seller_data
    .sort_values(
        by=[
            "profitability_score",
            "profit",
            "profit_margin"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )
    .reset_index(drop=True)
)


seller_data["profitability_rank"] = (
    seller_data.index + 1
)


# ============================================================
# Step 16: Display Seller Profitability
# ============================================================

result_columns = [
    "profitability_rank",
    "seller_id",
    "total_orders",
    "unique_customers",
    "total_revenue",
    "total_freight_cost",
    "profit",
    "profit_margin",
    "revenue_per_order",
    "profit_per_order",
    "profitability_score",
    "profitability_category"
]


print("\n============================================================")
print("Seller Profitability Performance")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 17: Top 10 Most Profitable Sellers
# ============================================================

print("\n============================================================")
print("Top 10 Most Profitable Sellers")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# Step 18: Profitability Category Summary
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

        average_profit_margin=(
            "profit_margin",
            "mean"
        ),

        average_profitability_score=(
            "profitability_score",
            "mean"
        )
    )
    .reset_index()
)


category_summary[
    [
        "total_revenue",
        "total_profit",
        "average_profit_margin",
        "average_profitability_score"
    ]
] = (
    category_summary[
        [
            "total_revenue",
            "total_profit",
            "average_profit_margin",
            "average_profitability_score"
        ]
    ]
    .round(2)
)


print("\n============================================================")
print("Profitability Category Summary")
print("============================================================")


print(
    category_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 19: Overall Profitability Statistics
# ============================================================

total_revenue = seller_data["total_revenue"].sum()
total_profit = seller_data["profit"].sum()

overall_margin = (
    total_profit
    /
    total_revenue
) * 100


average_margin = (
    seller_data["profit_margin"]
    .mean()
)


average_score = (
    seller_data["profitability_score"]
    .mean()
)


print("\n============================================================")
print("Overall Profitability Statistics")
print("============================================================")


print(
    f"Total Revenue          : "
    f"{total_revenue:.2f}"
)

print(
    f"Total Profit           : "
    f"{total_profit:.2f}"
)

print(
    f"Overall Profit Margin  : "
    f"{overall_margin:.2f}%"
)

print(
    f"Average Seller Margin  : "
    f"{average_margin:.2f}%"
)

print(
    f"Average Profitability Score: "
    f"{average_score:.2f}"
)


# ============================================================
# Step 20: Best Profitability Seller
# ============================================================

best_seller = seller_data.iloc[0]


print("\n============================================================")
print("Best Seller by Profitability")
print("============================================================")


print(
    f"Seller ID          : "
    f"{best_seller['seller_id']}"
)

print(
    f"Rank               : "
    f"{int(best_seller['profitability_rank'])}"
)

print(
    f"Revenue            : "
    f"{best_seller['total_revenue']:.2f}"
)

print(
    f"Profit             : "
    f"{best_seller['profit']:.2f}"
)

print(
    f"Profit Margin      : "
    f"{best_seller['profit_margin']:.2f}%"
)

print(
    f"Profit per Order   : "
    f"{best_seller['profit_per_order']:.2f}"
)

print(
    f"Profitability Score: "
    f"{best_seller['profitability_score']:.2f}"
)

print(
    f"Category           : "
    f"{best_seller['profitability_category']}"
)


# ============================================================
# Step 21: Negative Profit Sellers
# ============================================================

negative_profit = seller_data[
    seller_data["profit"] < 0
]


print("\n============================================================")
print("Negative Profit Sellers")
print("============================================================")


print(
    f"Negative Profit Sellers: "
    f"{len(negative_profit)}"
)


if not negative_profit.empty:

    print(
        negative_profit[
            [
                "seller_id",
                "total_revenue",
                "total_freight_cost",
                "profit",
                "profit_margin"
            ]
        ]
        .sort_values(
            "profit"
        )
        .head(10)
        .to_string(index=False)
    )

else:

    print(
        "No sellers with negative profit were identified."
    )


# ============================================================
# Step 22: Save Seller Profitability Analysis
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_profitability_performance.csv"
)


seller_data[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nSeller profitability analysis saved to:")
print(output_path)


# ============================================================
# Step 23: Save Category Summary
# ============================================================

summary_path = (
    project_root
    / "data"
    / "seller_profitability_category_summary.csv"
)


category_summary.to_csv(
    summary_path,
    index=False
)


print("\nProfitability category summary saved to:")
print(summary_path)


# ============================================================
# Step 24: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 80 Seller Profitability Performance Analysis "
    "completed successfully."
)
print("============================================================")