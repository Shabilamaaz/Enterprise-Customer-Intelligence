import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 83: Seller Performance Risk Analysis
# ============================================================

print("\n============================================================")
print("Step 83: Seller Performance Risk Analysis")
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
# Step 8: Calculate Profit Per Order
# ============================================================

seller_data["profit_per_order"] = (
    seller_data["profit"]
    /
    seller_data["total_orders"]
)


seller_data["profit_per_order"] = (
    seller_data["profit_per_order"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 9: Calculate Revenue Risk Score
# ============================================================

revenue_median = (
    seller_data["total_revenue"]
    .median()
)


seller_data["revenue_risk"] = (
    seller_data["total_revenue"]
    < revenue_median * 0.50
).astype(int)


# ============================================================
# Step 10: Calculate Order Risk
# ============================================================

order_median = (
    seller_data["total_orders"]
    .median()
)


seller_data["order_risk"] = (
    seller_data["total_orders"]
    < order_median * 0.50
).astype(int)


# ============================================================
# Step 11: Calculate Profit Risk
# ============================================================

seller_data["profit_risk"] = (
    seller_data["profit"] <= 0
).astype(int)


# ============================================================
# Step 12: Calculate Margin Risk
# ============================================================

seller_data["margin_risk"] = (
    seller_data["profit_margin"] < 10
).astype(int)


# ============================================================
# Step 13: Calculate Customer Concentration Risk
# ============================================================

customer_median = (
    seller_data["unique_customers"]
    .median()
)


seller_data["customer_risk"] = (
    seller_data["unique_customers"]
    < customer_median * 0.50
).astype(int)


# ============================================================
# Step 14: Calculate Total Risk Score
# ============================================================

seller_data["risk_score"] = (
    seller_data["revenue_risk"] * 20
    +
    seller_data["order_risk"] * 20
    +
    seller_data["profit_risk"] * 25
    +
    seller_data["margin_risk"] * 20
    +
    seller_data["customer_risk"] * 15
)


# ============================================================
# Step 15: Risk Category
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
# Step 16: Risk Recommendation
# ============================================================

def generate_recommendation(row):

    if row["risk_category"] == "Critical Risk":
        return "Immediate seller review required"

    elif row["risk_category"] == "High Risk":
        return "Performance improvement plan recommended"

    elif row["risk_category"] == "Medium Risk":
        return "Monitor seller performance closely"

    elif row["risk_category"] == "Low Risk":
        return "Periodic monitoring recommended"

    else:
        return "No immediate action required"


seller_data["risk_recommendation"] = (
    seller_data
    .apply(
        generate_recommendation,
        axis=1
    )
)


# ============================================================
# Step 17: Risk Rank
# ============================================================

seller_data = (
    seller_data
    .sort_values(
        by=[
            "risk_score",
            "profit",
            "total_revenue"
        ],
        ascending=[
            False,
            True,
            True
        ]
    )
    .reset_index(drop=True)
)


seller_data["risk_rank"] = (
    seller_data.index + 1
)


# ============================================================
# Step 18: Display Seller Risk Analysis
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
    "risk_recommendation"
]


print("\n============================================================")
print("Seller Performance Risk Analysis")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 19: Highest Risk Sellers
# ============================================================

print("\n============================================================")
print("Top 10 Highest Risk Sellers")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# Step 20: Risk Category Summary
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

        average_risk_score=(
            "risk_score",
            "mean"
        ),

        average_profit_margin=(
            "profit_margin",
            "mean"
        )
    )
    .reset_index()
)


# ============================================================
# Step 21: Seller Percentage
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
# Step 22: Revenue at Risk
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
# Step 23: Round Summary
# ============================================================

risk_summary[
    [
        "total_revenue",
        "total_profit",
        "average_risk_score",
        "average_profit_margin",
        "seller_percentage",
        "revenue_percentage"
    ]
] = (
    risk_summary[
        [
            "total_revenue",
            "total_profit",
            "average_risk_score",
            "average_profit_margin",
            "seller_percentage",
            "revenue_percentage"
        ]
    ]
    .round(2)
)


# ============================================================
# Step 24: Sort Risk Categories
# ============================================================

risk_order = [
    "Critical Risk",
    "High Risk",
    "Medium Risk",
    "Low Risk",
    "Healthy"
]


risk_summary["risk_order"] = (
    risk_summary["risk_category"]
    .map(
        {
            category: index
            for index, category
            in enumerate(risk_order)
        }
    )
)


risk_summary = (
    risk_summary
    .sort_values("risk_order")
    .drop(columns=["risk_order"])
    .reset_index(drop=True)
)


# ============================================================
# Step 25: Display Risk Summary
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
# Step 26: Critical and High Risk Sellers
# ============================================================

high_risk_sellers = seller_data[
    seller_data["risk_category"].isin(
        [
            "Critical Risk",
            "High Risk"
        ]
    )
]


print("\n============================================================")
print("Critical / High Risk Sellers")
print("============================================================")


print(
    f"Critical / High Risk Sellers: "
    f"{len(high_risk_sellers)}"
)


if not high_risk_sellers.empty:

    print(
        high_risk_sellers[
            [
                "seller_id",
                "total_revenue",
                "total_orders",
                "profit",
                "profit_margin",
                "risk_score",
                "risk_category",
                "risk_recommendation"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

else:

    print(
        "No critical or high-risk sellers identified."
    )


# ============================================================
# Step 27: Overall Risk Statistics
# ============================================================

average_risk = (
    seller_data["risk_score"]
    .mean()
)

highest_risk = (
    seller_data["risk_score"]
    .max()
)

total_at_risk_revenue = (
    high_risk_sellers["total_revenue"]
    .sum()
)


print("\n============================================================")
print("Overall Seller Risk Statistics")
print("============================================================")


print(
    f"Average Risk Score       : "
    f"{average_risk:.2f}"
)

print(
    f"Highest Risk Score       : "
    f"{highest_risk:.2f}"
)

print(
    f"High/Critical Risk Count : "
    f"{len(high_risk_sellers)}"
)

print(
    f"Revenue at High/Critical Risk: "
    f"{total_at_risk_revenue:.2f}"
)


# ============================================================
# Step 28: Save Seller Risk Analysis
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_performance_risk_analysis.csv"
)


seller_data[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nSeller risk analysis saved to:")
print(output_path)


# ============================================================
# Step 29: Save Risk Summary
# ============================================================

summary_path = (
    project_root
    / "data"
    / "seller_performance_risk_summary.csv"
)


risk_summary.to_csv(
    summary_path,
    index=False
)


print("\nSeller risk summary saved to:")
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
    "Step 83 Seller Performance Risk Analysis "
    "completed successfully."
)
print("============================================================")