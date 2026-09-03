import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 75: Seller Growth Trend Summary Analysis
# ============================================================

print("\n============================================================")
print("Step 75: Seller Growth Trend Summary Analysis")
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
# Step 4: Load Monthly Seller Data
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
        "\nERROR: No seller monthly data was returned."
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
# Step 9: Create Seller Trend Summary
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

        total_customers=(
            "unique_customers",
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
# Step 11: Calculate Trend Score
# ============================================================

seller_summary["trend_score"] = (
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


seller_summary["trend_score"] = (
    seller_summary["trend_score"]
    .clip(
        lower=0,
        upper=100
    )
    .round(2)
)


# ============================================================
# Step 12: Classify Seller Trend
# ============================================================

def classify_trend(row):

    if row["trend_score"] >= 70:
        return "Strong Growth"

    elif row["trend_score"] >= 50:
        return "Moderate Growth"

    elif row["declining_months"] > row["growth_months"]:
        return "Declining"

    else:
        return "Stable"


seller_summary["trend_category"] = (
    seller_summary
    .apply(
        classify_trend,
        axis=1
    )
)


# ============================================================
# Step 13: Rank Sellers
# ============================================================

seller_summary = (
    seller_summary
    .sort_values(
        by="trend_score",
        ascending=False
    )
    .reset_index(drop=True)
)


seller_summary["trend_rank"] = (
    seller_summary.index + 1
)


# ============================================================
# Step 14: Display Results
# ============================================================

result_columns = [
    "trend_rank",
    "seller_id",
    "months_active",
    "total_revenue",
    "total_orders",
    "average_monthly_revenue",
    "average_growth",
    "growth_months",
    "declining_months",
    "trend_score",
    "trend_category"
]


print("\n============================================================")
print("Seller Growth Trend Summary")
print("============================================================")


print(
    seller_summary[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 15: Trend Category Summary
# ============================================================

print("\n============================================================")
print("Trend Category Summary")
print("============================================================")


print(
    seller_summary[
        "trend_category"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 16: Calculate Overall Statistics
# ============================================================

average_growth = (
    seller_summary["average_growth"]
    .mean()
)

average_trend_score = (
    seller_summary["trend_score"]
    .mean()
)

strong_growth_sellers = (
    (
        seller_summary["trend_category"]
        == "Strong Growth"
    )
    .sum()
)

declining_sellers = (
    (
        seller_summary["trend_category"]
        == "Declining"
    )
    .sum()
)


print("\n============================================================")
print("Overall Growth Statistics")
print("============================================================")


print(
    f"Average Growth        : "
    f"{average_growth:.2f}%"
)

print(
    f"Average Trend Score   : "
    f"{average_trend_score:.2f}"
)

print(
    f"Strong Growth Sellers : "
    f"{int(strong_growth_sellers)}"
)

print(
    f"Declining Sellers     : "
    f"{int(declining_sellers)}"
)


# ============================================================
# Step 17: Strongest Growth Seller
# ============================================================

strongest = seller_summary.iloc[0]


print("\n============================================================")
print("Strongest Growth Seller")
print("============================================================")


print(
    f"Seller ID       : "
    f"{strongest['seller_id']}"
)

print(
    f"Trend Score     : "
    f"{strongest['trend_score']:.2f}"
)

print(
    f"Average Growth  : "
    f"{strongest['average_growth']:.2f}%"
)

print(
    f"Growth Months   : "
    f"{int(strongest['growth_months'])}"
)

print(
    f"Trend Category  : "
    f"{strongest['trend_category']}"
)


# ============================================================
# Step 18: Most Declining Seller
# ============================================================

most_declining = (
    seller_summary
    .sort_values(
        by="trend_score",
        ascending=True
    )
    .iloc[0]
)


print("\n============================================================")
print("Most Declining Seller")
print("============================================================")


print(
    f"Seller ID       : "
    f"{most_declining['seller_id']}"
)

print(
    f"Trend Score     : "
    f"{most_declining['trend_score']:.2f}"
)

print(
    f"Average Growth  : "
    f"{most_declining['average_growth']:.2f}%"
)

print(
    f"Declining Months: "
    f"{int(most_declining['declining_months'])}"
)

print(
    f"Trend Category  : "
    f"{most_declining['trend_category']}"
)


# ============================================================
# Step 19: Save Summary
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_growth_trend_summary.csv"
)


seller_summary[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nSeller growth trend summary saved to:")
print(output_path)


# ============================================================
# Step 20: Save Monthly Data
# ============================================================

monthly_output = (
    project_root
    / "data"
    / "seller_growth_monthly_detail.csv"
)


monthly_data.to_csv(
    monthly_output,
    index=False
)


print("\nMonthly growth detail saved to:")
print(monthly_output)


# ============================================================
# Step 21: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 75 Seller Growth Trend Summary "
    "completed successfully."
)
print("============================================================")