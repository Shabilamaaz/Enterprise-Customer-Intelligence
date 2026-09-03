import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 87: Seller Action Priority Summary
# ============================================================

print("\n============================================================")
print("Step 87: Seller Action Priority Summary")
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
# Step 8: Calculate Median Benchmarks
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


# ============================================================
# Step 9: Create Risk Indicators
# ============================================================

seller_data["low_revenue"] = (
    seller_data["total_revenue"]
    < revenue_median * 0.50
)


seller_data["low_orders"] = (
    seller_data["total_orders"]
    < orders_median * 0.50
)


seller_data["low_customers"] = (
    seller_data["unique_customers"]
    < customers_median * 0.50
)


seller_data["negative_profit"] = (
    seller_data["profit"] <= 0
)


seller_data["low_margin"] = (
    seller_data["profit_margin"] < 10
)


# ============================================================
# Step 10: Calculate Risk Score
# ============================================================

seller_data["risk_score"] = (
    seller_data["low_revenue"].astype(int) * 20
    +
    seller_data["low_orders"].astype(int) * 20
    +
    seller_data["low_customers"].astype(int) * 15
    +
    seller_data["negative_profit"].astype(int) * 25
    +
    seller_data["low_margin"].astype(int) * 20
)


# ============================================================
# Step 11: Risk Category
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
# Step 12: Generate Action
# ============================================================

def generate_action(row):

    if row["negative_profit"]:
        return (
            "Review pricing, freight cost, "
            "and operating costs"
        )

    elif row["low_margin"] and row["low_revenue"]:
        return (
            "Improve pricing and increase "
            "sales volume"
        )

    elif row["low_orders"] and row["low_customers"]:
        return (
            "Increase product visibility and "
            "customer acquisition"
        )

    elif row["low_revenue"]:
        return (
            "Increase sales volume and "
            "revenue generation"
        )

    elif row["low_orders"]:
        return (
            "Improve order volume through "
            "marketing and promotions"
        )

    elif row["low_customers"]:
        return (
            "Improve customer reach and retention"
        )

    elif row["low_margin"]:
        return (
            "Optimize pricing and operating costs"
        )

    else:
        return (
            "Maintain current performance"
        )


seller_data["recommended_action"] = (
    seller_data
    .apply(
        generate_action,
        axis=1
    )
)


# ============================================================
# Step 13: Action Priority
# ============================================================

def classify_priority(row):

    if row["risk_category"] == "Critical Risk":
        return "Immediate"

    elif row["risk_category"] == "High Risk":
        return "High"

    elif row["risk_category"] == "Medium Risk":
        return "Medium"

    elif row["risk_category"] == "Low Risk":
        return "Low"

    else:
        return "Maintain"


seller_data["action_priority"] = (
    seller_data
    .apply(
        classify_priority,
        axis=1
    )
)


# ============================================================
# Step 14: Priority Order
# ============================================================

priority_order = {
    "Immediate": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4,
    "Maintain": 5
}


seller_data["priority_order"] = (
    seller_data["action_priority"]
    .map(priority_order)
)


# ============================================================
# Step 15: Business Impact
# ============================================================

max_revenue = (
    seller_data["total_revenue"].max()
)

max_profit = (
    seller_data["profit"]
    .clip(lower=0)
    .max()
)


if max_revenue > 0:

    revenue_score = (
        seller_data["total_revenue"]
        /
        max_revenue
    ) * 100

else:

    revenue_score = 0


if max_profit > 0:

    profit_score = (
        seller_data["profit"]
        .clip(lower=0)
        /
        max_profit
    ) * 100

else:

    profit_score = 0


seller_data["business_impact_score"] = (
    revenue_score * 0.60
    +
    profit_score * 0.40
)


# ============================================================
# Step 16: Final Priority Score
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
# Step 17: Sort Sellers
# ============================================================

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


seller_data["action_rank"] = (
    seller_data.index + 1
)


# ============================================================
# Step 18: Action Summary
# ============================================================

action_summary = (
    seller_data
    .groupby("action_priority")
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

        average_revenue=(
            "total_revenue",
            "mean"
        ),

        average_profit=(
            "profit",
            "mean"
        ),

        average_profit_margin=(
            "profit_margin",
            "mean"
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
# Step 19: Seller Percentage
# ============================================================

total_sellers = (
    action_summary["seller_count"]
    .sum()
)


action_summary["seller_percentage"] = (
    action_summary["seller_count"]
    /
    total_sellers
) * 100


# ============================================================
# Step 20: Revenue Percentage
# ============================================================

total_revenue = (
    action_summary["total_revenue"]
    .sum()
)


if total_revenue > 0:

    action_summary["revenue_percentage"] = (
        action_summary["total_revenue"]
        /
        total_revenue
    ) * 100

else:

    action_summary["revenue_percentage"] = 0


# ============================================================
# Step 21: Round Values
# ============================================================

numeric_columns = [
    "total_revenue",
    "total_profit",
    "average_revenue",
    "average_profit",
    "average_profit_margin",
    "average_risk_score",
    "average_priority_score",
    "seller_percentage",
    "revenue_percentage"
]


action_summary[numeric_columns] = (
    action_summary[numeric_columns]
    .round(2)
)


# ============================================================
# Step 22: Sort Summary
# ============================================================

action_summary["priority_order"] = (
    action_summary["action_priority"]
    .map(priority_order)
)


action_summary = (
    action_summary
    .sort_values("priority_order")
    .drop(columns=["priority_order"])
    .reset_index(drop=True)
)


# ============================================================
# Step 23: Display Summary
# ============================================================

print("\n============================================================")
print("Seller Action Priority Summary")
print("============================================================")


print(
    action_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 24: Immediate Sellers
# ============================================================

immediate_sellers = seller_data[
    seller_data["action_priority"]
    == "Immediate"
]


print("\n============================================================")
print("Immediate Action Sellers")
print("============================================================")


print(
    f"Immediate Sellers: "
    f"{len(immediate_sellers)}"
)


if not immediate_sellers.empty:

    print(
        immediate_sellers[
            [
                "seller_id",
                "total_orders",
                "total_revenue",
                "profit",
                "profit_margin",
                "risk_score",
                "priority_score",
                "recommended_action"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

else:

    print(
        "No immediate-action sellers identified."
    )


# ============================================================
# Step 25: High Priority Sellers
# ============================================================

high_priority_sellers = seller_data[
    seller_data["action_priority"]
    == "High"
]


print("\n============================================================")
print("High Priority Sellers")
print("============================================================")


print(
    f"High Priority Sellers: "
    f"{len(high_priority_sellers)}"
)


if not high_priority_sellers.empty:

    print(
        high_priority_sellers[
            [
                "seller_id",
                "total_orders",
                "total_revenue",
                "profit",
                "profit_margin",
                "risk_score",
                "priority_score",
                "recommended_action"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

else:

    print(
        "No high-priority sellers identified."
    )


# ============================================================
# Step 26: Business Impact Requiring Attention
# ============================================================

attention_sellers = seller_data[
    seller_data["action_priority"]
    .isin(
        [
            "Immediate",
            "High"
        ]
    )
]


attention_revenue = (
    attention_sellers["total_revenue"]
    .sum()
)


attention_profit = (
    attention_sellers["profit"]
    .sum()
)


print("\n============================================================")
print("Business Impact Requiring Attention")
print("============================================================")


print(
    f"Sellers Requiring Attention: "
    f"{len(attention_sellers)}"
)

print(
    f"Revenue Requiring Attention: "
    f"{attention_revenue:.2f}"
)

print(
    f"Profit from These Sellers: "
    f"{attention_profit:.2f}"
)


# ============================================================
# Step 27: Overall Statistics
# ============================================================

average_priority_score = (
    seller_data["priority_score"]
    .mean()
)

highest_priority_score = (
    seller_data["priority_score"]
    .max()
)


print("\n============================================================")
print("Overall Priority Statistics")
print("============================================================")


print(
    f"Average Priority Score : "
    f"{average_priority_score:.2f}"
)

print(
    f"Highest Priority Score : "
    f"{highest_priority_score:.2f}"
)

print(
    f"Immediate Sellers       : "
    f"{len(immediate_sellers)}"
)

print(
    f"High Priority Sellers   : "
    f"{len(high_priority_sellers)}"
)


# ============================================================
# Step 28: Save Detailed Data
# ============================================================

detail_path = (
    project_root
    / "data"
    / "seller_action_priority_detail.csv"
)


seller_data[
    [
        "action_rank",
        "seller_id",
        "total_orders",
        "unique_customers",
        "total_revenue",
        "total_freight_cost",
        "profit",
        "profit_margin",
        "risk_score",
        "business_impact_score",
        "priority_score",
        "risk_category",
        "action_priority",
        "recommended_action"
    ]
].to_csv(
    detail_path,
    index=False
)


print("\nDetailed seller action data saved to:")
print(detail_path)


# ============================================================
# Step 29: Save Summary
# ============================================================

summary_path = (
    project_root
    / "data"
    / "seller_action_priority_summary.csv"
)


action_summary.to_csv(
    summary_path,
    index=False
)


print("\nAction priority summary saved to:")
print(summary_path)


# ============================================================
# Step 30: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 87 Seller Action Priority Summary "
    "completed successfully."
)
print("============================================================")