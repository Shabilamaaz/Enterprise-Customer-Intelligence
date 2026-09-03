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
# Step 3: Validate Required Files
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

risk_data = pd.read_csv(risk_path)

priority_data = pd.read_csv(priority_path)

action_data = pd.read_csv(action_path)


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
# Step 5: Validate Required Columns
# ============================================================

required_risk_columns = [
    "seller_id",
    "total_revenue",
    "profit",
    "risk_score",
    "risk_category"
]

required_priority_base_columns = [
    "seller_id"
]

required_action_columns = [
    "seller_id",
    "total_revenue",
    "profit",
    "risk_score",
    "action_priority"
]


for column in required_risk_columns:

    if column not in risk_data.columns:

        raise KeyError(
            f'ERROR: Risk data column "{column}" does not exist.'
        )


for column in required_priority_base_columns:

    if column not in priority_data.columns:

        raise KeyError(
            f'ERROR: Priority data column "{column}" does not exist.'
        )


for column in required_action_columns:

    if column not in action_data.columns:

        raise KeyError(
            f'ERROR: Action data column "{column}" does not exist.'
        )


# ============================================================
# Step 6: Recover Priority Score
# ============================================================

# The previous version failed here when priority_score
# was missing from the priority CSV.
#
# This section makes Step 91 robust.


if "priority_score" not in priority_data.columns:

    print(
        "\nWARNING: priority_score is missing "
        "from priority data."
    )

    if (
        "risk_score" in priority_data.columns
        and "business_impact_score"
        in priority_data.columns
    ):

        priority_data["priority_score"] = (
            priority_data["risk_score"] * 0.70
            +
            priority_data["business_impact_score"] * 0.30
        )

    elif "risk_score" in priority_data.columns:

        priority_data["priority_score"] = (
            priority_data["risk_score"]
        )

    else:

        # Try recovering risk score from risk_data
        priority_data = priority_data.merge(
            risk_data[
                [
                    "seller_id",
                    "risk_score"
                ]
            ],
            on="seller_id",
            how="left",
            suffixes=("", "_risk")
        )

        if "risk_score" not in priority_data.columns:

            priority_data["risk_score"] = (
                priority_data["risk_score_risk"]
            )

        priority_data["priority_score"] = (
            priority_data["risk_score"]
        )


priority_data["priority_score"] = pd.to_numeric(
    priority_data["priority_score"],
    errors="coerce"
).fillna(0)


# ============================================================
# Step 7: Recover Priority Score in Action Data
# ============================================================

if "priority_score" not in action_data.columns:

    print(
        "\nWARNING: priority_score is missing "
        "from action data."
    )

    # First try to recover it from priority data
    priority_score_lookup = (
        priority_data[
            [
                "seller_id",
                "priority_score"
            ]
        ]
        .drop_duplicates(
            subset=["seller_id"]
        )
    )

    action_data = action_data.merge(
        priority_score_lookup,
        on="seller_id",
        how="left"
    )


if "priority_score" not in action_data.columns:

    action_data["priority_score"] = (
        action_data["risk_score"]
    )


action_data["priority_score"] = pd.to_numeric(
    action_data["priority_score"],
    errors="coerce"
).fillna(0)


# ============================================================
# Step 8: Create Output Directory
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
# Step 9: Overall KPI Calculation
# ============================================================

total_sellers = len(risk_data)


total_revenue = (
    pd.to_numeric(
        risk_data["total_revenue"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)


total_profit = (
    pd.to_numeric(
        risk_data["profit"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)


average_risk_score = (
    pd.to_numeric(
        risk_data["risk_score"],
        errors="coerce"
    )
    .fillna(0)
    .mean()
)


average_priority_score = (
    priority_data["priority_score"]
    .mean()
)


# ============================================================
# Step 10: Risk KPI Calculation
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
# Step 11: Action KPI Calculation
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
# Step 12: Revenue Requiring Attention
# ============================================================

attention_data = action_data[
    action_data["action_priority"]
    .isin(
        [
            "Immediate",
            "High"
        ]
    )
].copy()


attention_revenue = (
    pd.to_numeric(
        attention_data["total_revenue"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)


attention_profit = (
    pd.to_numeric(
        attention_data["profit"],
        errors="coerce"
    )
    .fillna(0)
    .sum()
)


# ============================================================
# Step 13: Attention Revenue Percentage
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
# Step 14: KPI Summary
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
# Step 15: Risk Summary
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
    .sort_values(
        "sort_order"
    )
    .drop(
        columns=["sort_order"]
    )
    .reset_index(drop=True)
)


# ============================================================
# Step 16: Risk Percentages
# ============================================================

if total_sellers > 0:

    risk_summary["seller_percentage"] = (
        risk_summary["seller_count"]
        /
        total_sellers
    ) * 100

else:

    risk_summary["seller_percentage"] = 0


if total_revenue > 0:

    risk_summary["revenue_percentage"] = (
        risk_summary["total_revenue"]
        /
        total_revenue
    ) * 100

else:

    risk_summary["revenue_percentage"] = 0


risk_numeric_columns = [

    "total_revenue",

    "total_profit",

    "average_risk_score",

    "seller_percentage",

    "revenue_percentage"
]


risk_summary[risk_numeric_columns] = (
    risk_summary[risk_numeric_columns]
    .round(2)
)


# ============================================================
# Step 17: Action Summary
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
    .sort_values(
        "sort_order"
    )
    .drop(
        columns=["sort_order"]
    )
    .reset_index(drop=True)
)


# ============================================================
# Step 18: Action Percentages
# ============================================================

if total_sellers > 0:

    action_summary["seller_percentage"] = (
        action_summary["seller_count"]
        /
        total_sellers
    ) * 100

else:

    action_summary["seller_percentage"] = 0


if total_revenue > 0:

    action_summary["revenue_percentage"] = (
        action_summary["total_revenue"]
        /
        total_revenue
    ) * 100

else:

    action_summary["revenue_percentage"] = 0


action_numeric_columns = [

    "total_revenue",

    "total_profit",

    "average_risk_score",

    "average_priority_score",

    "seller_percentage",

    "revenue_percentage"
]


action_summary[action_numeric_columns] = (
    action_summary[action_numeric_columns]
    .round(2)
)


# ============================================================
# Step 19: Top Sellers Requiring Attention
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
# Step 20: Display Dashboard Summary
# ============================================================

print("\n============================================================")
print("Seller Risk & Action Dashboard KPIs")
print("============================================================")


print(
    f"Total Sellers               : "
    f"{total_sellers}"
)


print(
    f"Total Revenue               : "
    f"{total_revenue:.2f}"
)


print(
    f"Total Profit                : "
    f"{total_profit:.2f}"
)


print(
    f"Average Risk Score          : "
    f"{average_risk_score:.2f}"
)


print(
    f"Average Priority Score      : "
    f"{average_priority_score:.2f}"
)


print(
    f"Immediate Action Sellers    : "
    f"{immediate_actions}"
)


print(
    f"High Priority Sellers       : "
    f"{high_actions}"
)


print(
    f"Revenue Requiring Attention : "
    f"{attention_revenue:.2f}"
)


print(
    f"Attention Revenue %         : "
    f"{attention_revenue_percentage:.2f}%"
)


# ============================================================
# Step 21: Display Risk Summary
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
# Step 22: Display Action Summary
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
# Step 23: Display Top Attention Sellers
# ============================================================

print("\n============================================================")
print("Top Sellers Requiring Attention")
print("============================================================")


if not top_attention_sellers.empty:

    available_attention_columns = [

        column

        for column in attention_columns

        if column in top_attention_sellers.columns
    ]


    print(
        top_attention_sellers[
            available_attention_columns
        ]
        .to_string(
            index=False
        )
    )

else:

    print(
        "No sellers currently require immediate "
        "or high-priority action."
    )


# ============================================================
# Step 24: Save KPI Summary
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
# Step 25: Save Risk Summary
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
# Step 26: Save Action Summary
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
# Step 27: Save Attention Sellers
# ============================================================

attention_path = (
    output_directory
    / "top_sellers_requiring_attention.csv"
)


top_attention_sellers[
    [
        column

        for column in attention_columns

        if column in top_attention_sellers.columns
    ]
].to_csv(
    attention_path,
    index=False
)


print("\nAttention seller data saved to:")
print(attention_path)


# ============================================================
# Step 28: Save Combined Dashboard Data
# ============================================================

combined_path = (
    output_directory
    / "seller_risk_action_dashboard_data.csv"
)


dashboard_data = action_data.copy()


dashboard_data.to_csv(
    combined_path,
    index=False
)


print("\nCombined dashboard data saved to:")
print(combined_path)


# ============================================================
# Step 29: Final Validation
# ============================================================

print("\n============================================================")
print("Final Validation")
print("============================================================")


print(
    f"Risk columns available       : "
    f"{len(risk_data.columns)}"
)


print(
    f"Priority columns available   : "
    f"{len(priority_data.columns)}"
)


print(
    f"Action columns available     : "
    f"{len(action_data.columns)}"
)


print(
    f"Priority score available     : "
    f"{'Yes' if 'priority_score' in priority_data.columns else 'No'}"
)


print(
    f"Action priority score        : "
    f"{'Yes' if 'priority_score' in action_data.columns else 'No'}"
)


# ============================================================
# Step 30: Completion
# ============================================================

print("\n============================================================")

print(
    "Step 91 Seller Risk & Action Dashboard Summary "
    "completed successfully."
)

print("============================================================")
