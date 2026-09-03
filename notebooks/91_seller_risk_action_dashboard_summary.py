import pandas as pd
from pathlib import Path


# ============================================================
# Step 91: Seller Risk & Action Dashboard Summary
# ============================================================

print("\n============================================================")
print("Step 91: Seller Risk & Action Dashboard Summary")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Locate Required Files
# ============================================================

risk_path = (
    project_root
    / "data"
    / "seller_risk_category_analysis.csv"
)

priority_path = (
    project_root
    / "data"
    / "seller_risk_priority_analysis.csv"
)

action_path = (
    project_root
    / "data"
    / "seller_action_recommendation_analysis.csv"
)


# ============================================================
# Step 3: Validate Files
# ============================================================

required_files = [
    risk_path,
    priority_path,
    action_path
]


for file_path in required_files:

    if not file_path.exists():

        raise FileNotFoundError(
            "\nERROR: Required file was not found:\n"
            f"{file_path}"
        )


# ============================================================
# Step 4: Load Data
# ============================================================

risk_data = pd.read_csv(
    risk_path
)

priority_data = pd.read_csv(
    priority_path
)

action_data = pd.read_csv(
    action_path
)


print(
    f"\nRisk records loaded: "
    f"{len(risk_data)}"
)

print(
    f"Priority records loaded: "
    f"{len(priority_data)}"
)

print(
    f"Action records loaded: "
    f"{len(action_data)}"
)


# ============================================================
# Step 5: Create Output Directory
# ============================================================

output_directory = (
    project_root
    / "data"
    / "seller_risk_action_dashboard"
)


output_directory.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Step 6: Overall KPI Calculation
# ============================================================

total_sellers = len(risk_data)

total_revenue = (
    risk_data["total_revenue"]
    .sum()
)

total_profit = (
    risk_data["profit"]
    .sum()
)

average_risk_score = (
    risk_data["risk_score"]
    .mean()
)

average_priority_score = (
    priority_data["priority_score"]
    .mean()
)


# ============================================================
# Step 7: Risk KPI Calculation
# ============================================================

critical_risk = (
    risk_data["risk_category"]
    .eq("Critical Risk")
    .sum()
)

high_risk = (
    risk_data["risk_category"]
    .eq("High Risk")
    .sum()
)

medium_risk = (
    risk_data["risk_category"]
    .eq("Medium Risk")
    .sum()
)

low_risk = (
    risk_data["risk_category"]
    .eq("Low Risk")
    .sum()
)

healthy_sellers = (
    risk_data["risk_category"]
    .eq("Healthy")
    .sum()
)


# ============================================================
# Step 8: Action KPI Calculation
# ============================================================

immediate_actions = (
    action_data["action_priority"]
    .eq("Immediate")
    .sum()
)

high_actions = (
    action_data["action_priority"]
    .eq("High")
    .sum()
)

medium_actions = (
    action_data["action_priority"]
    .eq("Medium")
    .sum()
)

low_actions = (
    action_data["action_priority"]
    .eq("Low")
    .sum()
)

maintain_actions = (
    action_data["action_priority"]
    .eq("Maintain")
    .sum()
)


# ============================================================
# Step 9: Revenue Requiring Attention
# ============================================================

attention_data = action_data[
    action_data["action_priority"]
    .isin(
        [
            "Immediate",
            "High"
        ]
    )
]


attention_revenue = (
    attention_data["total_revenue"]
    .sum()
)

attention_profit = (
    attention_data["profit"]
    .sum()
)


# ============================================================
# Step 10: Attention Revenue Percentage
# ============================================================

if total_revenue > 0:

    attention_revenue_percentage = (
        attention_revenue
        /
        total_revenue
    ) * 100

else:

    attention_revenue_percentage = 0


# ============================================================
# Step 11: Create KPI DataFrame
# ============================================================

kpi_summary = pd.DataFrame(
    [
        {
            "metric": "Total Sellers",
            "value": total_sellers
        },
        {
            "metric": "Total Revenue",
            "value": round(total_revenue, 2)
        },
        {
            "metric": "Total Profit",
            "value": round(total_profit, 2)
        },
        {
            "metric": "Average Risk Score",
            "value": round(
                average_risk_score,
                2
            )
        },
        {
            "metric": "Average Priority Score",
            "value": round(
                average_priority_score,
                2
            )
        },
        {
            "metric": "Critical Risk Sellers",
            "value": critical_risk
        },
        {
            "metric": "High Risk Sellers",
            "value": high_risk
        },
        {
            "metric": "Medium Risk Sellers",
            "value": medium_risk
        },
        {
            "metric": "Low Risk Sellers",
            "value": low_risk
        },
        {
            "metric": "Healthy Sellers",
            "value": healthy_sellers
        },
        {
            "metric": "Immediate Action Sellers",
            "value": immediate_actions
        },
        {
            "metric": "High Priority Sellers",
            "value": high_actions
        },
        {
            "metric": "Medium Priority Sellers",
            "value": medium_actions
        },
        {
            "metric": "Low Priority Sellers",
            "value": low_actions
        },
        {
            "metric": "Maintain Sellers",
            "value": maintain_actions
        },
        {
            "metric": "Revenue Requiring Attention",
            "value": round(
                attention_revenue,
                2
            )
        },
        {
            "metric": "Profit from Attention Sellers",
            "value": round(
                attention_profit,
                2
            )
        },
        {
            "metric": "Attention Revenue Percentage",
            "value": round(
                attention_revenue_percentage,
                2
            )
        }
    ]
)


# ============================================================
# Step 12: Risk Summary
# ============================================================

risk_summary = (
    risk_data
    .groupby(
        "risk_category"
    )
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
        )
    )
    .reset_index()
)


risk_order = {
    "Critical Risk": 1,
    "High Risk": 2,
    "Medium Risk": 3,
    "Low Risk": 4,
    "Healthy": 5
}


risk_summary["sort_order"] = (
    risk_summary["risk_category"]
    .map(risk_order)
)


risk_summary = (
    risk_summary
    .sort_values("sort_order")
    .drop(columns=["sort_order"])
    .reset_index(drop=True)
)


# ============================================================
# Step 13: Risk Percentages
# ============================================================

risk_summary["seller_percentage"] = (
    risk_summary["seller_count"]
    /
    total_sellers
) * 100


if total_revenue > 0:

    risk_summary["revenue_percentage"] = (
        risk_summary["total_revenue"]
        /
        total_revenue
    ) * 100

else:

    risk_summary["revenue_percentage"] = 0


risk_summary[
    [
        "total_revenue",
        "total_profit",
        "average_risk_score",
        "seller_percentage",
        "revenue_percentage"
    ]
] = (
    risk_summary[
        [
            "total_revenue",
            "total_profit",
            "average_risk_score",
            "seller_percentage",
            "revenue_percentage"
        ]
    ]
    .round(2)
)


# ============================================================
# Step 14: Action Summary
# ============================================================

action_summary = (
    action_data
    .groupby(
        "action_priority"
    )
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


action_order = {
    "Immediate": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4,
    "Maintain": 5
}


action_summary["sort_order"] = (
    action_summary["action_priority"]
    .map(action_order)
)


action_summary = (
    action_summary
    .sort_values("sort_order")
    .drop(columns=["sort_order"])
    .reset_index(drop=True)
)


# ============================================================
# Step 15: Action Percentages
# ============================================================

action_summary["seller_percentage"] = (
    action_summary["seller_count"]
    /
    total_sellers
) * 100


if total_revenue > 0:

    action_summary["revenue_percentage"] = (
        action_summary["total_revenue"]
        /
        total_revenue
    ) * 100

else:

    action_summary["revenue_percentage"] = 0


action_summary[
    [
        "total_revenue",
        "total_profit",
        "average_risk_score",
        "average_priority_score",
        "seller_percentage",
        "revenue_percentage"
    ]
] = (
    action_summary[
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
# Step 16: Top Sellers Requiring Attention
# ============================================================

top_attention_sellers = (
    attention_data
    .sort_values(
        [
            "priority_score",
            "total_revenue"
        ],
        ascending=[
            False,
            False
        ]
    )
    .head(20)
)


attention_columns = [
    "seller_id",
    "total_orders",
    "total_revenue",
    "profit",
    "risk_score",
    "priority_score",
    "risk_category",
    "action_priority"
]


# ============================================================
# Step 17: Display Dashboard Summary
# ============================================================

print("\n============================================================")
print("Seller Risk & Action Dashboard KPIs")
print("============================================================")


print(
    f"Total Sellers              : "
    f"{total_sellers}"
)

print(
    f"Total Revenue              : "
    f"{total_revenue:.2f}"
)

print(
    f"Total Profit               : "
    f"{total_profit:.2f}"
)

print(
    f"Average Risk Score         : "
    f"{average_risk_score:.2f}"
)

print(
    f"Average Priority Score     : "
    f"{average_priority_score:.2f}"
)

print(
    f"Immediate Action Sellers   : "
    f"{immediate_actions}"
)

print(
    f"High Priority Sellers      : "
    f"{high_actions}"
)

print(
    f"Revenue Requiring Attention: "
    f"{attention_revenue:.2f}"
)

print(
    f"Attention Revenue %        : "
    f"{attention_revenue_percentage:.2f}%"
)


# ============================================================
# Step 18: Display Risk Summary
# ============================================================

print("\n============================================================")
print("Risk Summary")
print("============================================================")

print(
    risk_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 19: Display Action Summary
# ============================================================

print("\n============================================================")
print("Action Priority Summary")
print("============================================================")

print(
    action_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 20: Display Top Attention Sellers
# ============================================================

print("\n============================================================")
print("Top Sellers Requiring Attention")
print("============================================================")


if not top_attention_sellers.empty:

    print(
        top_attention_sellers[
            attention_columns
        ]
        .to_string(index=False)
    )

else:

    print(
        "No sellers currently require immediate "
        "or high-priority action."
    )


# ============================================================
# Step 21: Save KPI Summary
# ============================================================

kpi_path = (
    output_directory
    / "seller_risk_action_dashboard_kpis.csv"
)


kpi_summary.to_csv(
    kpi_path,
    index=False
)


print("\nKPI summary saved to:")
print(kpi_path)


# ============================================================
# Step 22: Save Risk Summary
# ============================================================

risk_summary_path = (
    output_directory
    / "seller_risk_dashboard_summary.csv"
)


risk_summary.to_csv(
    risk_summary_path,
    index=False
)


print("\nRisk summary saved to:")
print(risk_summary_path)


# ============================================================
# Step 23: Save Action Summary
# ============================================================

action_summary_path = (
    output_directory
    / "seller_action_dashboard_summary.csv"
)


action_summary.to_csv(
    action_summary_path,
    index=False
)


print("\nAction summary saved to:")
print(action_summary_path)


# ============================================================
# Step 24: Save Attention Sellers
# ============================================================

attention_path = (
    output_directory
    / "top_sellers_requiring_attention.csv"
)


top_attention_sellers[
    attention_columns
].to_csv(
    attention_path,
    index=False
)


print("\nAttention seller data saved to:")
print(attention_path)


# ============================================================
# Step 25: Save Combined Dashboard Data
# ============================================================

combined_path = (
    output_directory
    / "seller_risk_action_dashboard_data.csv"
)


dashboard_data = (
    action_data.copy()
)


dashboard_data.to_csv(
    combined_path,
    index=False
)


print("\nCombined dashboard data saved to:")
print(combined_path)


# ============================================================
# Step 26: Completion
# ============================================================

print("\n============================================================")
print(
    "Step 91 Seller Risk & Action Dashboard Summary "
    "completed successfully."
)
print("============================================================")