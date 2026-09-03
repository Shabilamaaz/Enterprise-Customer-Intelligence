import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# Step 90: Seller Risk Dashboard Charts
# ============================================================

print("\n============================================================")
print("Step 90: Seller Risk Dashboard Charts")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Locate Seller Risk Data
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


print("\nRisk data:")
print(risk_path)

print("\nPriority data:")
print(priority_path)

print("\nAction data:")
print(action_path)


# ============================================================
# Step 3: Validate Required Files
# ============================================================

if not risk_path.exists():
    raise FileNotFoundError(
        "\nERROR: seller_risk_category_analysis.csv "
        "was not found.\n"
        f"Expected location:\n{risk_path}"
    )


if not priority_path.exists():
    raise FileNotFoundError(
        "\nERROR: seller_risk_priority_analysis.csv "
        "was not found.\n"
        f"Expected location:\n{priority_path}"
    )


if not action_path.exists():
    raise FileNotFoundError(
        "\nERROR: seller_action_recommendation_analysis.csv "
        "was not found.\n"
        f"Expected location:\n{action_path}"
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
    f"\nRisk records loaded: {len(risk_data)}"
)

print(
    f"Priority records loaded: {len(priority_data)}"
)

print(
    f"Action records loaded: {len(action_data)}"
)


# ============================================================
# Step 5: Create Chart Directory
# ============================================================

chart_directory = (
    project_root
    / "data"
    / "seller_risk_dashboard_charts"
)


chart_directory.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Step 6: Risk Category Distribution
# ============================================================

risk_counts = (
    risk_data["risk_category"]
    .value_counts()
)


risk_order = [
    "Critical Risk",
    "High Risk",
    "Medium Risk",
    "Low Risk",
    "Healthy"
]


risk_counts = (
    risk_counts
    .reindex(
        risk_order,
        fill_value=0
    )
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    risk_counts.index,
    risk_counts.values
)

plt.title(
    "Seller Risk Category Distribution"
)

plt.xlabel(
    "Risk Category"
)

plt.ylabel(
    "Number of Sellers"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()


risk_category_chart = (
    chart_directory
    / "seller_risk_category_distribution.png"
)


plt.savefig(
    risk_category_chart,
    dpi=150
)

plt.close()


print(
    "\nRisk category chart saved to:"
)

print(risk_category_chart)


# ============================================================
# Step 7: Risk Score Distribution
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    risk_data["risk_score"],
    bins=20
)

plt.title(
    "Seller Risk Score Distribution"
)

plt.xlabel(
    "Risk Score"
)

plt.ylabel(
    "Number of Sellers"
)

plt.tight_layout()


risk_score_chart = (
    chart_directory
    / "seller_risk_score_distribution.png"
)


plt.savefig(
    risk_score_chart,
    dpi=150
)

plt.close()


print(
    "\nRisk score chart saved to:"
)

print(risk_score_chart)


# ============================================================
# Step 8: Revenue by Risk Category
# ============================================================

revenue_by_risk = (
    risk_data
    .groupby(
        "risk_category"
    )["total_revenue"]
    .sum()
    .reindex(
        risk_order,
        fill_value=0
    )
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    revenue_by_risk.index,
    revenue_by_risk.values
)

plt.title(
    "Revenue by Seller Risk Category"
)

plt.xlabel(
    "Risk Category"
)

plt.ylabel(
    "Total Revenue"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()


revenue_risk_chart = (
    chart_directory
    / "revenue_by_risk_category.png"
)


plt.savefig(
    revenue_risk_chart,
    dpi=150
)

plt.close()


print(
    "\nRevenue by risk chart saved to:"
)

print(revenue_risk_chart)


# ============================================================
# Step 9: Profit by Risk Category
# ============================================================

profit_by_risk = (
    risk_data
    .groupby(
        "risk_category"
    )["profit"]
    .sum()
    .reindex(
        risk_order,
        fill_value=0
    )
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    profit_by_risk.index,
    profit_by_risk.values
)

plt.title(
    "Profit by Seller Risk Category"
)

plt.xlabel(
    "Risk Category"
)

plt.ylabel(
    "Total Profit"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()


profit_risk_chart = (
    chart_directory
    / "profit_by_risk_category.png"
)


plt.savefig(
    profit_risk_chart,
    dpi=150
)

plt.close()


print(
    "\nProfit by risk chart saved to:"
)

print(profit_risk_chart)


# ============================================================
# Step 10: Priority Category Distribution
# ============================================================

priority_counts = (
    priority_data["priority_category"]
    .value_counts()
)


priority_order = [
    "P1 - Immediate",
    "P2 - High",
    "P3 - Medium",
    "P4 - Low",
    "P5 - Healthy"
]


priority_counts = (
    priority_counts
    .reindex(
        priority_order,
        fill_value=0
    )
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    priority_counts.index,
    priority_counts.values
)

plt.title(
    "Seller Priority Category Distribution"
)

plt.xlabel(
    "Priority Category"
)

plt.ylabel(
    "Number of Sellers"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()


priority_chart = (
    chart_directory
    / "seller_priority_category_distribution.png"
)


plt.savefig(
    priority_chart,
    dpi=150
)

plt.close()


print(
    "\nPriority chart saved to:"
)

print(priority_chart)


# ============================================================
# Step 11: Priority Score Distribution
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    priority_data["priority_score"],
    bins=20
)

plt.title(
    "Seller Priority Score Distribution"
)

plt.xlabel(
    "Priority Score"
)

plt.ylabel(
    "Number of Sellers"
)

plt.tight_layout()


priority_score_chart = (
    chart_directory
    / "seller_priority_score_distribution.png"
)


plt.savefig(
    priority_score_chart,
    dpi=150
)

plt.close()


print(
    "\nPriority score chart saved to:"
)

print(priority_score_chart)


# ============================================================
# Step 12: Revenue by Priority Category
# ============================================================

revenue_by_priority = (
    priority_data
    .groupby(
        "priority_category"
    )["total_revenue"]
    .sum()
    .reindex(
        priority_order,
        fill_value=0
    )
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    revenue_by_priority.index,
    revenue_by_priority.values
)

plt.title(
    "Revenue by Seller Priority Category"
)

plt.xlabel(
    "Priority Category"
)

plt.ylabel(
    "Total Revenue"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()


priority_revenue_chart = (
    chart_directory
    / "revenue_by_priority_category.png"
)


plt.savefig(
    priority_revenue_chart,
    dpi=150
)

plt.close()


print(
    "\nRevenue by priority chart saved to:"
)

print(priority_revenue_chart)


# ============================================================
# Step 13: Business Impact vs Risk Score
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.scatter(
    priority_data["risk_score"],
    priority_data["business_impact_score"],
    alpha=0.6
)

plt.title(
    "Seller Risk Score vs Business Impact"
)

plt.xlabel(
    "Risk Score"
)

plt.ylabel(
    "Business Impact Score"
)

plt.tight_layout()


risk_impact_chart = (
    chart_directory
    / "risk_score_vs_business_impact.png"
)


plt.savefig(
    risk_impact_chart,
    dpi=150
)

plt.close()


print(
    "\nRisk vs impact chart saved to:"
)

print(risk_impact_chart)


# ============================================================
# Step 14: Risk Score vs Revenue
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.scatter(
    risk_data["risk_score"],
    risk_data["total_revenue"],
    alpha=0.6
)

plt.title(
    "Seller Risk Score vs Revenue"
)

plt.xlabel(
    "Risk Score"
)

plt.ylabel(
    "Total Revenue"
)

plt.tight_layout()


risk_revenue_chart = (
    chart_directory
    / "risk_score_vs_revenue.png"
)


plt.savefig(
    risk_revenue_chart,
    dpi=150
)

plt.close()


print(
    "\nRisk vs revenue chart saved to:"
)

print(risk_revenue_chart)


# ============================================================
# Step 15: Action Priority Distribution
# ============================================================

action_counts = (
    action_data["action_priority"]
    .value_counts()
)


action_order = [
    "Immediate",
    "High",
    "Medium",
    "Low",
    "Maintain"
]


action_counts = (
    action_counts
    .reindex(
        action_order,
        fill_value=0
    )
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    action_counts.index,
    action_counts.values
)

plt.title(
    "Seller Action Priority Distribution"
)

plt.xlabel(
    "Action Priority"
)

plt.ylabel(
    "Number of Sellers"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()


action_chart = (
    chart_directory
    / "seller_action_priority_distribution.png"
)


plt.savefig(
    action_chart,
    dpi=150
)

plt.close()


print(
    "\nAction priority chart saved to:"
)

print(action_chart)


# ============================================================
# Step 16: Revenue Requiring Action
# ============================================================

revenue_by_action = (
    action_data
    .groupby(
        "action_priority"
    )["total_revenue"]
    .sum()
    .reindex(
        action_order,
        fill_value=0
    )
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    revenue_by_action.index,
    revenue_by_action.values
)

plt.title(
    "Revenue by Seller Action Priority"
)

plt.xlabel(
    "Action Priority"
)

plt.ylabel(
    "Total Revenue"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()


action_revenue_chart = (
    chart_directory
    / "revenue_by_action_priority.png"
)


plt.savefig(
    action_revenue_chart,
    dpi=150
)

plt.close()


print(
    "\nRevenue by action chart saved to:"
)

print(action_revenue_chart)


# ============================================================
# Step 17: Top 10 Sellers Requiring Attention
# ============================================================

attention_sellers = (
    action_data[
        action_data["action_priority"]
        .isin(
            [
                "Immediate",
                "High"
            ]
        )
    ]
    .sort_values(
        "total_revenue",
        ascending=False
    )
    .head(10)
)


plt.figure(
    figsize=(12, 6)
)

plt.bar(
    attention_sellers["seller_id"].astype(str),
    attention_sellers["total_revenue"]
)

plt.title(
    "Top 10 High-Value Sellers Requiring Attention"
)

plt.xlabel(
    "Seller ID"
)

plt.ylabel(
    "Total Revenue"
)

plt.xticks(
    rotation=45
)

plt.tight_layout()


attention_chart = (
    chart_directory
    / "top_attention_sellers_by_revenue.png"
)


plt.savefig(
    attention_chart,
    dpi=150
)

plt.close()


print(
    "\nAttention seller chart saved to:"
)

print(attention_chart)


# ============================================================
# Step 18: Create Chart Index
# ============================================================

chart_index = pd.DataFrame(
    [
        {
            "chart_name":
                "Seller Risk Category Distribution",
            "file_name":
                "seller_risk_category_distribution.png"
        },
        {
            "chart_name":
                "Seller Risk Score Distribution",
            "file_name":
                "seller_risk_score_distribution.png"
        },
        {
            "chart_name":
                "Revenue by Risk Category",
            "file_name":
                "revenue_by_risk_category.png"
        },
        {
            "chart_name":
                "Profit by Risk Category",
            "file_name":
                "profit_by_risk_category.png"
        },
        {
            "chart_name":
                "Seller Priority Category Distribution",
            "file_name":
                "seller_priority_category_distribution.png"
        },
        {
            "chart_name":
                "Seller Priority Score Distribution",
            "file_name":
                "seller_priority_score_distribution.png"
        },
        {
            "chart_name":
                "Revenue by Priority Category",
            "file_name":
                "revenue_by_priority_category.png"
        },
        {
            "chart_name":
                "Risk Score vs Business Impact",
            "file_name":
                "risk_score_vs_business_impact.png"
        },
        {
            "chart_name":
                "Risk Score vs Revenue",
            "file_name":
                "risk_score_vs_revenue.png"
        },
        {
            "chart_name":
                "Seller Action Priority Distribution",
            "file_name":
                "seller_action_priority_distribution.png"
        },
        {
            "chart_name":
                "Revenue by Action Priority",
            "file_name":
                "revenue_by_action_priority.png"
        },
        {
            "chart_name":
                "Top Attention Sellers by Revenue",
            "file_name":
                "top_attention_sellers_by_revenue.png"
        }
    ]
)


# ============================================================
# Step 19: Save Chart Index
# ============================================================

index_path = (
    chart_directory
    / "chart_index.csv"
)


chart_index.to_csv(
    index_path,
    index=False
)


print(
    "\nChart index saved to:"
)

print(index_path)


# ============================================================
# Step 20: Completion
# ============================================================

print("\n============================================================")
print(
    "Step 90 Seller Risk Dashboard Charts "
    "completed successfully."
)
print("============================================================")