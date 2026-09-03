import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 77: Seller Growth Opportunity Analysis
# ============================================================

print("\n============================================================")
print("Step 77: Seller Growth Opportunity Analysis")
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
# Step 4: Load Seller Monthly Performance
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
        "\nERROR: No seller performance data was returned."
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
# Step 8: Create Growth Direction
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
# Step 9: Seller-Level Summary
# ============================================================

seller_data = (
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

seller_data["growth_ratio"] = (
    seller_data["growth_months"]
    /
    seller_data["months_active"]
)


# ============================================================
# Step 11: Revenue Potential Score
# ============================================================

seller_data["revenue_score"] = (
    seller_data["total_revenue"]
    /
    seller_data["total_revenue"].max()
) * 100


# ============================================================
# Step 12: Growth Score
# ============================================================

seller_data["growth_score"] = (
    seller_data["growth_ratio"] * 70
    +
    (
        seller_data["average_growth"]
        .clip(
            lower=-100,
            upper=100
        )
        / 100
        * 30
    )
)


seller_data["growth_score"] = (
    seller_data["growth_score"]
    .clip(
        lower=0,
        upper=100
    )
)


# ============================================================
# Step 13: Opportunity Score
# ============================================================

seller_data["opportunity_score"] = (
    seller_data["revenue_score"] * 0.40
    +
    seller_data["growth_score"] * 0.60
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
# Step 14: Growth Opportunity Classification
# ============================================================

def classify_opportunity(row):

    if (
        row["opportunity_score"] >= 70
        and row["average_growth"] > 0
    ):
        return "High Opportunity"

    elif (
        row["opportunity_score"] >= 50
        and row["average_growth"] >= 0
    ):
        return "Good Opportunity"

    elif row["average_growth"] > 0:
        return "Emerging Opportunity"

    elif row["declining_months"] > row["growth_months"]:
        return "Recovery Opportunity"

    else:
        return "Stable"


seller_data["opportunity_category"] = (
    seller_data
    .apply(
        classify_opportunity,
        axis=1
    )
)


# ============================================================
# Step 15: Rank Sellers
# ============================================================

seller_data = (
    seller_data
    .sort_values(
        by="opportunity_score",
        ascending=False
    )
    .reset_index(drop=True)
)


seller_data["opportunity_rank"] = (
    seller_data.index + 1
)


# ============================================================
# Step 16: Display Top Opportunities
# ============================================================

result_columns = [
    "opportunity_rank",
    "seller_id",
    "months_active",
    "total_revenue",
    "total_orders",
    "average_monthly_revenue",
    "average_growth",
    "growth_score",
    "opportunity_score",
    "opportunity_category"
]


print("\n============================================================")
print("Top Seller Growth Opportunities")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 17: Opportunity Category Summary
# ============================================================

print("\n============================================================")
print("Growth Opportunity Category Summary")
print("============================================================")


print(
    seller_data[
        "opportunity_category"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 18: Opportunity Statistics
# ============================================================

average_opportunity_score = (
    seller_data["opportunity_score"]
    .mean()
)

high_opportunity_count = (
    seller_data[
        "opportunity_category"
    ]
    .eq("High Opportunity")
    .sum()
)

good_opportunity_count = (
    seller_data[
        "opportunity_category"
    ]
    .eq("Good Opportunity")
    .sum()
)


print("\n============================================================")
print("Opportunity Statistics")
print("============================================================")


print(
    f"Average Opportunity Score : "
    f"{average_opportunity_score:.2f}"
)

print(
    f"High Opportunity Sellers   : "
    f"{int(high_opportunity_count)}"
)

print(
    f"Good Opportunity Sellers   : "
    f"{int(good_opportunity_count)}"
)


# ============================================================
# Step 19: Best Growth Opportunity
# ============================================================

best_opportunity = seller_data.iloc[0]


print("\n============================================================")
print("Best Seller Growth Opportunity")
print("============================================================")


print(
    f"Seller ID          : "
    f"{best_opportunity['seller_id']}"
)

print(
    f"Total Revenue      : "
    f"{best_opportunity['total_revenue']:.2f}"
)

print(
    f"Average Growth     : "
    f"{best_opportunity['average_growth']:.2f}%"
)

print(
    f"Growth Score       : "
    f"{best_opportunity['growth_score']:.2f}"
)

print(
    f"Opportunity Score  : "
    f"{best_opportunity['opportunity_score']:.2f}"
)

print(
    f"Opportunity Type   : "
    f"{best_opportunity['opportunity_category']}"
)


# ============================================================
# Step 20: Identify Recovery Opportunities
# ============================================================

recovery_opportunities = (
    seller_data[
        seller_data["opportunity_category"]
        == "Recovery Opportunity"
    ]
)


print("\n============================================================")
print("Recovery Opportunities")
print("============================================================")


print(
    f"Recovery Opportunity Sellers: "
    f"{len(recovery_opportunities)}"
)


if not recovery_opportunities.empty:

    print(
        recovery_opportunities[
            result_columns
        ]
        .head(10)
        .to_string(index=False)
    )

else:

    print(
        "No recovery opportunities identified."
    )


# ============================================================
# Step 21: Save Opportunity Analysis
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_growth_opportunity_analysis.csv"
)


seller_data[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nOpportunity analysis saved to:")
print(output_path)


# ============================================================
# Step 22: Save Monthly Growth Detail
# ============================================================

monthly_output = (
    project_root
    / "data"
    / "seller_growth_opportunity_monthly_detail.csv"
)


monthly_data.to_csv(
    monthly_output,
    index=False
)


print("\nMonthly opportunity detail saved to:")
print(monthly_output)


# ============================================================
# Step 23: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 77 Seller Growth Opportunity Analysis "
    "completed successfully."
)
print("============================================================")