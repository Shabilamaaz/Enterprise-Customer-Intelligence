import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 85: Seller Risk Priority Analysis
# ============================================================

print("\n============================================================")
print("Step 85: Seller Risk Priority Analysis")
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
# Step 8: Calculate Risk Indicators
# ============================================================

revenue_median = (
    seller_data["total_revenue"]
    .median()
)

orders_median = (
    seller_data["total_orders"]
    .median()
)

customers_median = (
    seller_data["unique_customers"]
    .median()
)


seller_data["low_revenue_risk"] = (
    seller_data["total_revenue"]
    < revenue_median * 0.50
).astype(int)


seller_data["low_order_risk"] = (
    seller_data["total_orders"]
    < orders_median * 0.50
).astype(int)


seller_data["low_customer_risk"] = (
    seller_data["unique_customers"]
    < customers_median * 0.50
).astype(int)


seller_data["negative_profit_risk"] = (
    seller_data["profit"] <= 0
).astype(int)


seller_data["low_margin_risk"] = (
    seller_data["profit_margin"] < 10
).astype(int)


# ============================================================
# Step 9: Calculate Risk Score
# ============================================================

seller_data["risk_score"] = (
    seller_data["low_revenue_risk"] * 20
    +
    seller_data["low_order_risk"] * 20
    +
    seller_data["low_customer_risk"] * 15
    +
    seller_data["negative_profit_risk"] * 25
    +
    seller_data["low_margin_risk"] * 20
)


# ============================================================
# Step 10: Risk Category
# ============================================================

def classify_risk(score):

    if score >= 70:
        return "Critical Risk"

    elif score >= 50:
        return "High Risk"

    elif score >= 30:
        return "Medium Risk"

    elif score >= 15:
        return "Low Risk"

    else:
        return "Healthy"


seller_data["risk_category"] = (
    seller_data["risk_score"]
    .apply(classify_risk)
)


# ============================================================
# Step 11: Business Impact Score
# ============================================================

max_revenue = (
    seller_data["total_revenue"].max()
)

max_profit = (
    seller_data["profit"].clip(lower=0).max()
)


if max_revenue > 0:

    revenue_impact = (
        seller_data["total_revenue"]
        /
        max_revenue
    ) * 100

else:

    revenue_impact = 0


if max_profit > 0:

    profit_impact = (
        seller_data["profit"].clip(lower=0)
        /
        max_profit
    ) * 100

else:

    profit_impact = 0


seller_data["business_impact_score"] = (
    revenue_impact * 0.60
    +
    profit_impact * 0.40
)


# ============================================================
# Step 12: Priority Score
# ============================================================

seller_data["priority_score"] = (
    seller_data["risk_score"] * 0.70
    +
    seller_data["business_impact_score"] * 0.30
)


seller_data["priority_score"] = (
    seller_data["priority_score"]
    .clip(
        lower=0,
        upper=100
    )
    .round(2)
)


# ============================================================
# Step 13: Priority Category
# ============================================================

def classify_priority(row):

    risk = row["risk_category"]
    score = row["priority_score"]

    if (
        risk == "Critical Risk"
        or score >= 70
    ):
        return "P1 - Immediate"

    elif (
        risk == "High Risk"
        or score >= 50
    ):
        return "P2 - High"

    elif (
        risk == "Medium Risk"
        or score >= 30
    ):
        return "P3 - Medium"

    elif risk == "Low Risk":
        return "P4 - Low"

    else:
        return "P5 - Healthy"


seller_data["priority_category"] = (
    seller_data
    .apply(
        classify_priority,
        axis=1
    )
)


# ============================================================
# Step 14: Recommended Action
# ============================================================

def recommended_action(priority):

    if priority == "P1 - Immediate":
        return "Immediate management intervention"

    elif priority == "P2 - High":
        return "Create seller improvement plan"

    elif priority == "P3 - Medium":
        return "Monitor and review performance"

    elif priority == "P4 - Low":
        return "Periodic performance monitoring"

    else:
        return "No immediate action required"


seller_data["recommended_action"] = (
    seller_data["priority_category"]
    .apply(recommended_action)
)


# ============================================================
# Step 15: Rank Sellers
# ============================================================

priority_order = {
    "P1 - Immediate": 1,
    "P2 - High": 2,
    "P3 - Medium": 3,
    "P4 - Low": 4,
    "P5 - Healthy": 5
}


seller_data["priority_order"] = (
    seller_data["priority_category"]
    .map(priority_order)
)


seller_data = (
    seller_data
    .sort_values(
        by=[
            "priority_order",
            "priority_score",
            "total_revenue"
        ],
        ascending=[
            True,
            False,
            False
        ]
    )
    .reset_index(drop=True)
)


seller_data["priority_rank"] = (
    seller_data.index + 1
)


# ============================================================
# Step 16: Display Priority Analysis
# ============================================================

result_columns = [
    "priority_rank",
    "seller_id",
    "total_orders",
    "unique_customers",
    "total_revenue",
    "profit",
    "profit_margin",
    "risk_score",
    "business_impact_score",
    "priority_score",
    "risk_category",
    "priority_category",
    "recommended_action"
]


print("\n============================================================")
print("Seller Risk Priority Analysis")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 17: Immediate Priority Sellers
# ============================================================

immediate_sellers = seller_data[
    seller_data["priority_category"]
    == "P1 - Immediate"
]


print("\n============================================================")
print("P1 - Immediate Priority Sellers")
print("============================================================")


print(
    f"Immediate Priority Sellers: "
    f"{len(immediate_sellers)}"
)


if not immediate_sellers.empty:

    print(
        immediate_sellers[
            result_columns
        ]
        .head(20)
        .to_string(index=False)
    )

else:

    print(
        "No immediate-priority sellers identified."
    )


# ============================================================
# Step 18: Priority Summary
# ============================================================

priority_summary = (
    seller_data
    .groupby("priority_category")
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

        average_risk_score=(
            "risk_score",
            "mean"
        ),

        average_priority_score=(
            "priority_score",
            "mean"
        )
    )
    .reset_index()
)


# ============================================================
# Step 19: Calculate Percentages
# ============================================================

total_sellers = (
    priority_summary["seller_count"]
    .sum()
)


priority_summary["seller_percentage"] = (
    priority_summary["seller_count"]
    /
    total_sellers
) * 100


total_revenue = (
    priority_summary["total_revenue"]
    .sum()
)


if total_revenue > 0:

    priority_summary["revenue_percentage"] = (
        priority_summary["total_revenue"]
        /
        total_revenue
    ) * 100

else:

    priority_summary["revenue_percentage"] = 0


# ============================================================
# Step 20: Round Summary
# ============================================================

priority_summary[
    [
        "total_revenue",
        "total_profit",
        "average_risk_score",
        "average_priority_score",
        "seller_percentage",
        "revenue_percentage"
    ]
] = (
    priority_summary[
        [
            "total_revenue",
            "total_profit",
            "average_risk_score",
            "average_priority_score",
            "seller_percentage",
            "revenue_percentage"
        ]
    ]
    .round(2)
)


# ============================================================
# Step 21: Sort Priority Categories
# ============================================================

priority_summary["priority_order"] = (
    priority_summary["priority_category"]
    .map(priority_order)
)


priority_summary = (
    priority_summary
    .sort_values("priority_order")
    .drop(columns=["priority_order"])
    .reset_index(drop=True)
)


# ============================================================
# Step 22: Display Priority Summary
# ============================================================

print("\n============================================================")
print("Seller Priority Summary")
print("============================================================")


print(
    priority_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 23: High-Impact Risk Sellers
# ============================================================

high_impact_risk = seller_data[
    (
        seller_data["risk_score"] >= 50
    )
    &
    (
        seller_data["business_impact_score"] >= 50
    )
]


print("\n============================================================")
print("High-Impact Risk Sellers")
print("============================================================")


print(
    f"High-Impact Risk Sellers: "
    f"{len(high_impact_risk)}"
)


if not high_impact_risk.empty:

    print(
        high_impact_risk[
            [
                "seller_id",
                "total_revenue",
                "profit",
                "risk_score",
                "business_impact_score",
                "priority_score",
                "priority_category"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

else:

    print(
        "No high-impact risk sellers identified."
    )


# ============================================================
# Step 24: Overall Statistics
# ============================================================

average_priority = (
    seller_data["priority_score"]
    .mean()
)

highest_priority = (
    seller_data["priority_score"]
    .max()
)

at_risk_revenue = (
    seller_data.loc[
        seller_data["priority_category"]
        .isin(
            [
                "P1 - Immediate",
                "P2 - High"
            ]
        ),
        "total_revenue"
    ]
    .sum()
)


print("\n============================================================")
print("Overall Priority Statistics")
print("============================================================")


print(
    f"Average Priority Score : "
    f"{average_priority:.2f}"
)

print(
    f"Highest Priority Score : "
    f"{highest_priority:.2f}"
)

print(
    f"P1/P2 Seller Count     : "
    f"{len(
        seller_data[
            seller_data["priority_category"]
            .isin(
                [
                    "P1 - Immediate",
                    "P2 - High"
                ]
            )
        ]
    )}"
)

print(
    f"P1/P2 Revenue at Risk  : "
    f"{at_risk_revenue:.2f}"
)


# ============================================================
# Step 25: Save Seller Priority Analysis
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_risk_priority_analysis.csv"
)


seller_data[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nSeller priority analysis saved to:")
print(output_path)


# ============================================================
# Step 26: Save Priority Summary
# ============================================================

summary_path = (
    project_root
    / "data"
    / "seller_risk_priority_summary.csv"
)


priority_summary.to_csv(
    summary_path,
    index=False
)


print("\nSeller priority summary saved to:")
print(summary_path)


# ============================================================
# Step 27: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 85 Seller Risk Priority Analysis "
    "completed successfully."
)
print("============================================================")