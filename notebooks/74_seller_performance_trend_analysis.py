import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 74: Seller Performance Trend Analysis
# ============================================================

print("\n============================================================")
print("Step 74: Seller Performance Trend Analysis")
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

    AND
    o.order_purchase_timestamp IS NOT NULL

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
        "\nERROR: No monthly seller performance data "
        "was returned."
    )


# ============================================================
# Step 6: Calculate Revenue Growth
# ============================================================

monthly_data["previous_month_revenue"] = (
    monthly_data
    .groupby("seller_id")["total_revenue"]
    .shift(1)
)


monthly_data["revenue_growth"] = (
    monthly_data["total_revenue"]
    -
    monthly_data["previous_month_revenue"]
)


monthly_data["growth_percentage"] = (
    monthly_data["revenue_growth"]
    /
    monthly_data["previous_month_revenue"]
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
# Step 7: Calculate Order Growth
# ============================================================

monthly_data["previous_month_orders"] = (
    monthly_data
    .groupby("seller_id")["total_orders"]
    .shift(1)
)


monthly_data["order_growth"] = (
    monthly_data["total_orders"]
    -
    monthly_data["previous_month_orders"]
)


monthly_data["order_growth_percentage"] = (
    monthly_data["order_growth"]
    /
    monthly_data["previous_month_orders"]
) * 100


monthly_data["order_growth_percentage"] = (
    monthly_data["order_growth_percentage"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 8: Identify Growth Direction
# ============================================================

monthly_data["growth_direction"] = (
    monthly_data["revenue_growth"]
    .apply(
        lambda x:
        "Growing"
        if x > 0
        else (
            "Declining"
            if x < 0
            else "Stable"
        )
    )
)


# ============================================================
# Step 9: Seller Trend Summary
# ============================================================

trend_summary = (
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

        average_monthly_revenue=(
            "total_revenue",
            "mean"
        ),

        total_orders=(
            "total_orders",
            "sum"
        ),

        average_monthly_orders=(
            "total_orders",
            "mean"
        ),

        average_growth_percentage=(
            "growth_percentage",
            "mean"
        ),

        positive_growth_months=(
            "growth_direction",
            lambda x:
            (x == "Growing").sum()
        ),

        negative_growth_months=(
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

trend_summary["growth_month_ratio"] = (

    trend_summary["positive_growth_months"]
    /
    trend_summary["months_active"]

)


# ============================================================
# Step 11: Trend Classification
# ============================================================

def classify_trend(row):

    if (
        row["growth_month_ratio"] >= 0.60
        and row["average_growth_percentage"] > 0
    ):
        return "Strong Growth"

    elif (
        row["growth_month_ratio"] >= 0.40
        and row["average_growth_percentage"] >= 0
    ):
        return "Moderate Growth"

    elif (
        row["negative_growth_months"]
        >
        row["positive_growth_months"]
    ):
        return "Declining"

    else:
        return "Stable"


trend_summary["performance_trend"] = (
    trend_summary
    .apply(
        classify_trend,
        axis=1
    )
)


# ============================================================
# Step 12: Trend Score
# ============================================================

trend_summary["trend_score"] = (

    trend_summary["growth_month_ratio"] * 70

    +

    (
        trend_summary["average_growth_percentage"]
        .clip(
            lower=-100,
            upper=100
        )
        / 100
        * 30
    )

)


trend_summary["trend_score"] = (
    trend_summary["trend_score"]
    .clip(
        lower=0,
        upper=100
    )
    .round(2)
)


# ============================================================
# Step 13: Rank Sellers by Trend
# ============================================================

trend_summary = (
    trend_summary
    .sort_values(
        by="trend_score",
        ascending=False
    )
    .reset_index(drop=True)
)


trend_summary["trend_rank"] = (
    trend_summary.index + 1
)


# ============================================================
# Step 14: Display Trend Analysis
# ============================================================

result_columns = [

    "trend_rank",
    "seller_id",
    "months_active",
    "total_revenue",
    "average_monthly_revenue",
    "total_orders",
    "average_growth_percentage",
    "positive_growth_months",
    "negative_growth_months",
    "growth_month_ratio",
    "trend_score",
    "performance_trend"

]


print("\n============================================================")
print("Seller Performance Trend Analysis")
print("============================================================")


print(
    trend_summary[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 15: Top 10 Growing Sellers
# ============================================================

print("\n============================================================")
print("Top 10 Sellers by Performance Trend")
print("============================================================")


print(
    trend_summary[
        result_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# Step 16: Trend Category Summary
# ============================================================

print("\n============================================================")
print("Performance Trend Summary")
print("============================================================")


print(
    trend_summary[
        "performance_trend"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 17: Trend Statistics
# ============================================================

average_trend_score = (
    trend_summary["trend_score"]
    .mean()
)


highest_trend_score = (
    trend_summary["trend_score"]
    .max()
)


lowest_trend_score = (
    trend_summary["trend_score"]
    .min()
)


print("\n============================================================")
print("Trend Statistics")
print("============================================================")


print(
    f"Average Trend Score : "
    f"{average_trend_score:.2f}"
)


print(
    f"Highest Trend Score : "
    f"{highest_trend_score:.2f}"
)


print(
    f"Lowest Trend Score  : "
    f"{lowest_trend_score:.2f}"
)


# ============================================================
# Step 18: Strongest Growing Seller
# ============================================================

strongest_seller = trend_summary.iloc[0]


print("\n============================================================")
print("Strongest Growing Seller")
print("============================================================")


print(
    f"Seller ID             : "
    f"{strongest_seller['seller_id']}"
)


print(
    f"Trend Score           : "
    f"{strongest_seller['trend_score']:.2f}"
)


print(
    f"Average Growth        : "
    f"{strongest_seller['average_growth_percentage']:.2f}%"
)


print(
    f"Positive Growth Months: "
    f"{int(strongest_seller['positive_growth_months'])}"
)


print(
    f"Negative Growth Months: "
    f"{int(strongest_seller['negative_growth_months'])}"
)


print(
    f"Trend Category        : "
    f"{strongest_seller['performance_trend']}"
)


# ============================================================
# Step 19: Most Declining Seller
# ============================================================

declining_seller = (
    trend_summary
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
    f"Seller ID             : "
    f"{declining_seller['seller_id']}"
)


print(
    f"Trend Score           : "
    f"{declining_seller['trend_score']:.2f}"
)


print(
    f"Average Growth        : "
    f"{declining_seller['average_growth_percentage']:.2f}%"
)


print(
    f"Positive Growth Months: "
    f"{int(declining_seller['positive_growth_months'])}"
)


print(
    f"Negative Growth Months: "
    f"{int(declining_seller['negative_growth_months'])}"
)


print(
    f"Trend Category        : "
    f"{declining_seller['performance_trend']}"
)


# ============================================================
# Step 20: Save Monthly Trend Data
# ============================================================

monthly_output = (
    project_root
    / "data"
    / "seller_monthly_performance_trend.csv"
)


monthly_data.to_csv(
    monthly_output,
    index=False
)


print("\nMonthly trend data saved to:")
print(monthly_output)


# ============================================================
# Step 21: Save Seller Trend Summary
# ============================================================

summary_output = (
    project_root
    / "data"
    / "seller_performance_trend_summary.csv"
)


trend_summary[
    result_columns
].to_csv(
    summary_output,
    index=False
)


print("\nSeller trend summary saved to:")
print(summary_output)


# ============================================================
# Step 22: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 74 Seller Performance Trend Analysis "
    "completed successfully."
)
print("============================================================")