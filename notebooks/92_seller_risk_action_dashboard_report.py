import pandas as pd
from pathlib import Path


# ============================================================
# Step 92: Seller Risk & Action Dashboard Report
# ============================================================

print("\n============================================================")
print("Step 92: Seller Risk & Action Dashboard Report")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Locate Step 91 Output
# ============================================================

dashboard_directory = (
    project_root
    / "data"
    / "seller_risk_action_dashboard"
)


kpi_path = (
    dashboard_directory
    / "seller_risk_action_dashboard_kpis.csv"
)

risk_path = (
    dashboard_directory
    / "seller_risk_dashboard_summary.csv"
)

action_path = (
    dashboard_directory
    / "seller_action_dashboard_summary.csv"
)

attention_path = (
    dashboard_directory
    / "top_sellers_requiring_attention.csv"
)


# ============================================================
# Step 3: Validate Files
# ============================================================

required_files = [
    kpi_path,
    risk_path,
    action_path,
    attention_path
]


for file_path in required_files:

    if not file_path.exists():

        raise FileNotFoundError(
            "\nERROR: Required Step 91 file was not found:\n"
            f"{file_path}"
        )


# ============================================================
# Step 4: Load Data
# ============================================================

kpi_data = pd.read_csv(
    kpi_path
)

risk_summary = pd.read_csv(
    risk_path
)

action_summary = pd.read_csv(
    action_path
)

attention_data = pd.read_csv(
    attention_path
)


print("\nAll Step 91 dashboard files loaded successfully.")


# ============================================================
# Step 5: Helper Function
# ============================================================

def get_kpi(metric_name):

    result = kpi_data.loc[
        kpi_data["metric"] == metric_name,
        "value"
    ]

    if result.empty:
        return 0

    return result.iloc[0]


# ============================================================
# Step 6: Extract KPIs
# ============================================================

total_sellers = get_kpi(
    "Total Sellers"
)

total_revenue = get_kpi(
    "Total Revenue"
)

total_profit = get_kpi(
    "Total Profit"
)

average_risk_score = get_kpi(
    "Average Risk Score"
)

average_priority_score = get_kpi(
    "Average Priority Score"
)

critical_risk = get_kpi(
    "Critical Risk Sellers"
)

high_risk = get_kpi(
    "High Risk Sellers"
)

immediate_actions = get_kpi(
    "Immediate Action Sellers"
)

high_actions = get_kpi(
    "High Priority Sellers"
)

attention_revenue = get_kpi(
    "Revenue Requiring Attention"
)

attention_revenue_percentage = get_kpi(
    "Attention Revenue Percentage"
)


# ============================================================
# Step 7: Create Report Directory
# ============================================================

report_directory = (
    project_root
    / "reports"
)


report_directory.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Step 8: Create Dashboard Report
# ============================================================

report_lines = []


report_lines.append(
    "============================================================"
)

report_lines.append(
    "SELLER RISK & ACTION DASHBOARD REPORT"
)

report_lines.append(
    "============================================================"
)

report_lines.append("")


# ============================================================
# Executive Summary
# ============================================================

report_lines.append(
    "EXECUTIVE SUMMARY"
)

report_lines.append(
    "------------------------------------------------------------"
)

report_lines.append(
    f"Total Sellers: {int(total_sellers)}"
)

report_lines.append(
    f"Total Revenue: {float(total_revenue):,.2f}"
)

report_lines.append(
    f"Total Profit: {float(total_profit):,.2f}"
)

report_lines.append(
    f"Average Risk Score: "
    f"{float(average_risk_score):.2f}"
)

report_lines.append(
    f"Average Priority Score: "
    f"{float(average_priority_score):.2f}"
)

report_lines.append("")


# ============================================================
# Risk Overview
# ============================================================

report_lines.append(
    "RISK OVERVIEW"
)

report_lines.append(
    "------------------------------------------------------------"
)

report_lines.append(
    f"Critical Risk Sellers: "
    f"{int(critical_risk)}"
)

report_lines.append(
    f"High Risk Sellers: "
    f"{int(high_risk)}"
)

report_lines.append("")


# ============================================================
# Action Overview
# ============================================================

report_lines.append(
    "ACTION OVERVIEW"
)

report_lines.append(
    "------------------------------------------------------------"
)

report_lines.append(
    f"Immediate Action Sellers: "
    f"{int(immediate_actions)}"
)

report_lines.append(
    f"High Priority Sellers: "
    f"{int(high_actions)}"
)

report_lines.append(
    f"Revenue Requiring Attention: "
    f"{float(attention_revenue):,.2f}"
)

report_lines.append(
    f"Attention Revenue Percentage: "
    f"{float(attention_revenue_percentage):.2f}%"
)

report_lines.append("")


# ============================================================
# Risk Category Details
# ============================================================

report_lines.append(
    "RISK CATEGORY DETAILS"
)

report_lines.append(
    "------------------------------------------------------------"
)


for _, row in risk_summary.iterrows():

    report_lines.append(
        f"{row['risk_category']}: "
        f"{int(row['seller_count'])} sellers | "
        f"Revenue: {row['total_revenue']:,.2f} | "
        f"Profit: {row['total_profit']:,.2f}"
    )


report_lines.append("")


# ============================================================
# Action Priority Details
# ============================================================

report_lines.append(
    "ACTION PRIORITY DETAILS"
)

report_lines.append(
    "------------------------------------------------------------"
)


for _, row in action_summary.iterrows():

    report_lines.append(
        f"{row['action_priority']}: "
        f"{int(row['seller_count'])} sellers | "
        f"Revenue: {row['total_revenue']:,.2f} | "
        f"Profit: {row['total_profit']:,.2f}"
    )


report_lines.append("")


# ============================================================
# Top Sellers Requiring Attention
# ============================================================

report_lines.append(
    "TOP SELLERS REQUIRING ATTENTION"
)

report_lines.append(
    "------------------------------------------------------------"
)


if attention_data.empty:

    report_lines.append(
        "No sellers currently require immediate "
        "or high-priority action."
    )

else:

    top_attention = attention_data.head(10)

    for _, row in top_attention.iterrows():

        report_lines.append(
            f"Seller: {row['seller_id']} | "
            f"Priority: {row['action_priority']} | "
            f"Risk Score: {row['risk_score']} | "
            f"Priority Score: {row['priority_score']} | "
            f"Revenue: {row['total_revenue']:,.2f}"
        )


report_lines.append("")


# ============================================================
# Business Recommendations
# ============================================================

report_lines.append(
    "BUSINESS RECOMMENDATIONS"
)

report_lines.append(
    "------------------------------------------------------------"
)


if int(immediate_actions) > 0:

    report_lines.append(
        "1. Immediately review sellers classified as "
        "Immediate Action."
    )

else:

    report_lines.append(
        "1. No immediate seller intervention is required."
    )


if int(high_actions) > 0:

    report_lines.append(
        "2. Prioritize High Action sellers for "
        "performance improvement."
    )

else:

    report_lines.append(
        "2. No high-priority seller intervention "
        "is currently required."
    )


if float(attention_revenue_percentage) > 0:

    report_lines.append(
        "3. Focus management attention on the revenue "
        "exposed to high-risk sellers."
    )

else:

    report_lines.append(
        "3. Revenue exposure requiring attention is minimal."
    )


report_lines.append(
    "4. Review seller pricing, freight costs, "
    "order volume, and customer reach."
)

report_lines.append(
    "5. Monitor seller risk and performance periodically."
)

report_lines.append("")


# ============================================================
# Final Conclusion
# ============================================================

report_lines.append(
    "CONCLUSION"
)

report_lines.append(
    "------------------------------------------------------------"
)

report_lines.append(
    "The seller risk and action analysis provides a "
    "prioritized view of seller performance."
)

report_lines.append(
    "The dashboard can be used to identify high-risk "
    "sellers, estimate business impact, and prioritize "
    "management actions."
)

report_lines.append("")


# ============================================================
# Step 9: Save TXT Report
# ============================================================

txt_path = (
    report_directory
    / "seller_risk_action_dashboard_report.txt"
)


with open(
    txt_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(report_lines)
    )


print("\nText report saved to:")
print(txt_path)


# ============================================================
# Step 10: Save Excel Report
# ============================================================

excel_path = (
    report_directory
    / "seller_risk_action_dashboard_report.xlsx"
)


with pd.ExcelWriter(
    excel_path,
    engine="openpyxl"
) as writer:

    kpi_data.to_excel(
        writer,
        sheet_name="KPI Summary",
        index=False
    )

    risk_summary.to_excel(
        writer,
        sheet_name="Risk Summary",
        index=False
    )

    action_summary.to_excel(
        writer,
        sheet_name="Action Summary",
        index=False
    )

    attention_data.to_excel(
        writer,
        sheet_name="Attention Sellers",
        index=False
    )


print("\nExcel report saved to:")
print(excel_path)


# ============================================================
# Step 11: Completion
# ============================================================

print("\n============================================================")
print(
    "Step 92 Seller Risk & Action Dashboard Report "
    "completed successfully."
)
print("============================================================")