import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 84: Seller Risk Category Analysis
# ============================================================

print("\n============================================================")
print("Step 84: Seller Risk Category Analysis")
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
# Step 8: Calculate Seller Risk Score
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


seller_data["revenue_risk"] = (
    seller_data["total_revenue"]
    < revenue_median * 0.50
).astype(int)


seller_data["order_risk"] = (
    seller_data["total_orders"]
    < orders_median * 0.50
).astype(int)


seller_data["customer_risk"] = (
    seller_data["unique_customers"]
    < customers_median * 0.50
).astype(int)


seller_data["profit_risk"] = (
    seller_data["profit"] <= 0
).astype(int)


seller_data["margin_risk"] = (
    seller_data["profit_margin"] < 10
).astype(int)


seller_data["risk_score"] = (
    seller_data["revenue_risk"] * 20
    +
    seller_data["order_risk"] * 20
    +
    seller_data["customer_risk"] * 15
    +
    seller_data["profit_risk"] * 25
    +
    seller_data["margin_risk"] * 20
)


# ============================================================
# Step 9: Risk Category
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
# Step 10: Risk Priority
# ============================================================

risk_priority = {
    "Critical Risk": 1,
    "High Risk": 2,
    "Medium Risk": 3,
    "Low Risk": 4,
    "Healthy": 5
}


seller_data["risk_priority"] = (
    seller_data["risk_category"]
    .map(risk_priority)
)


# ============================================================
# Step 11: Recommended Action
# ============================================================

def recommended_action(category):

    if category == "Critical Risk":
        return "Immediate intervention"

    elif category == "High Risk":
        return "Performance improvement plan"

    elif category == "Medium Risk":
        return "Close monitoring"

    elif category == "Low Risk":
        return "Periodic monitoring"

    else:
        return "No immediate action"


seller_data["recommended_action"] = (
    seller_data["risk_category"]
    .apply(recommended_action)
)


# ============================================================
# Step 12: Sort Sellers by Risk
# ============================================================

seller_data = (
    seller_data
    .sort_values(
        by=[
            "risk_priority",
            "risk_score",
            "profit"
        ],
        ascending=[
            True,
            False,
            True
        ]
    )
    .reset_index(drop=True)
)


seller_data["risk_rank"] = (
    seller_data.index + 1
)


# ============================================================
# Step 13: Display Seller Risk Categories
# ============================================================

result_columns = [
    "risk_rank",
    "seller_id",
    "total_orders",
    "unique_customers",
    "total_revenue",
    "total_freight_cost",
    "profit",
    "profit_margin",
    "risk_score",
    "risk_category",
    "recommended_action"
]


print("\n============================================================")
print("Seller Risk Category Analysis")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 14: Risk Category Summary
# ============================================================

risk_summary = (
    seller_data
    .groupby("risk_category")
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

        average_margin=(
            "profit_margin",
            "mean"
        ),

        average_risk_score=(
            "risk_score",
            "mean"
        )
    )
    .reset_index()
)


# ============================================================
# Step 15: Seller Percentage
# ============================================================

total_sellers = (
    risk_summary["seller_count"]
    .sum()
)


risk_summary["seller_percentage"] = (
    risk_summary["seller_count"]
    /
    total_sellers
) * 100


# ============================================================
# Step 16: Revenue at Risk
# ============================================================

total_revenue = (
    risk_summary["total_revenue"]
    .sum()
)


if total_revenue > 0:

    risk_summary["revenue_percentage"] = (
        risk_summary["total_revenue"]
        /
        total_revenue
    ) * 100

else:

    risk_summary["revenue_percentage"] = 0


# ============================================================
# Step 17: Round Summary Values
# ============================================================

numeric_columns = [
    "total_revenue",
    "total_profit",
    "average_revenue",
    "average_profit",
    "average_margin",
    "average_risk_score",
    "seller_percentage",
    "revenue_percentage"
]


risk_summary[numeric_columns] = (
    risk_summary[numeric_columns]
    .round(2)
)


# ============================================================
# Step 18: Sort Risk Categories
# ============================================================

category_order = [
    "Critical Risk",
    "High Risk",
    "Medium Risk",
    "Low Risk",
    "Healthy"
]


risk_summary["category_order"] = (
    risk_summary["risk_category"]
    .map(
        {
            category: index
            for index, category
            in enumerate(category_order)
        }
    )
)


risk_summary = (
    risk_summary
    .sort_values("category_order")
    .drop(columns=["category_order"])
    .reset_index(drop=True)
)


# ============================================================
# Step 19: Display Risk Summary
# ============================================================

print("\n============================================================")
print("Seller Risk Category Summary")
print("============================================================")


print(
    risk_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 20: Critical Risk Sellers
# ============================================================

critical_sellers = seller_data[
    seller_data["risk_category"]
    == "Critical Risk"
]


print("\n============================================================")
print("Critical Risk Sellers")
print("============================================================")


print(
    f"Critical Risk Sellers: "
    f"{len(critical_sellers)}"
)


if not critical_sellers.empty:

    print(
        critical_sellers[
            [
                "seller_id",
                "total_orders",
                "total_revenue",
                "profit",
                "profit_margin",
                "risk_score",
                "recommended_action"
            ]
        ]
        .to_string(index=False)
    )

else:

    print(
        "No critical-risk sellers identified."
    )


# ============================================================
# Step 21: High Risk Sellers
# ============================================================

high_risk_sellers = seller_data[
    seller_data["risk_category"]
    == "High Risk"
]


print("\n============================================================")
print("High Risk Sellers")
print("============================================================")


print(
    f"High Risk Sellers: "
    f"{len(high_risk_sellers)}"
)


if not high_risk_sellers.empty:

    print(
        high_risk_sellers[
            [
                "seller_id",
                "total_orders",
                "total_revenue",
                "profit",
                "profit_margin",
                "risk_score",
                "recommended_action"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

else:

    print(
        "No high-risk sellers identified."
    )


# ============================================================
# Step 22: Risk Statistics
# ============================================================

average_risk_score = (
    seller_data["risk_score"]
    .mean()
)

highest_risk_score = (
    seller_data["risk_score"]
    .max()
)

high_risk_count = (
    seller_data["risk_category"]
    .isin(
        [
            "Critical Risk",
            "High Risk"
        ]
    )
    .sum()
)

at_risk_revenue = (
    seller_data.loc[
        seller_data["risk_category"]
        .isin(
            [
                "Critical Risk",
                "High Risk"
            ]
        ),
        "total_revenue"
    ]
    .sum()
)


print("\n============================================================")
print("Seller Risk Statistics")
print("============================================================")


print(
    f"Average Risk Score       : "
    f"{average_risk_score:.2f}"
)

print(
    f"Highest Risk Score       : "
    f"{highest_risk_score:.2f}"
)

print(
    f"Critical/High Risk Count : "
    f"{int(high_risk_count)}"
)

print(
    f"Revenue at Risk          : "
    f"{at_risk_revenue:.2f}"
)


# ============================================================
# Step 23: Save Seller Risk Categories
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_risk_category_analysis.csv"
)


seller_data[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nSeller risk category analysis saved to:")
print(output_path)


# ============================================================
# Step 24: Save Risk Summary
# ============================================================

summary_path = (
    project_root
    / "data"
    / "seller_risk_category_summary.csv"
)


risk_summary.to_csv(
    summary_path,
    index=False
)


print("\nSeller risk category summary saved to:")
print(summary_path)


# ============================================================
# Step 25: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 84 Seller Risk Category Analysis "
    "completed successfully."
)
print("============================================================")