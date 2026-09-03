from pathlib import Path
import pandas as pd


# ============================================================
# Step 96: Final Project README & Deliverables Summary
# ============================================================

print("\n============================================================")
print("Step 96: Final Project README & Deliverables Summary")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Define Important Project Directories
# ============================================================

data_directory = project_root / "data"

final_directory = (
    data_directory
    / "final_seller_dashboard"
)

export_directory = (
    project_root
    / "final_output"
)

reports_directory = (
    project_root
    / "reports"
)


# ============================================================
# Step 3: Locate Final Files
# ============================================================

final_dataset = (
    final_directory
    / "seller_risk_action_final_dataset.csv"
)

final_excel = (
    final_directory
    / "seller_risk_action_final_dataset.xlsx"
)

risk_summary = (
    final_directory
    / "final_risk_summary.csv"
)

action_summary = (
    final_directory
    / "final_action_summary.csv"
)

validation_report = (
    final_directory
    / "seller_dashboard_validation_report.csv"
)

dashboard_excel = (
    export_directory
    / "final_seller_risk_dashboard.xlsx"
)

dashboard_csv = (
    export_directory
    / "final_seller_risk_dashboard.csv"
)

management_summary = (
    export_directory
    / "final_seller_risk_management_summary.txt"
)

export_index = (
    export_directory
    / "final_export_index.csv"
)


# ============================================================
# Step 4: Validate Final Files
# ============================================================

required_files = [
    final_dataset,
    final_excel,
    risk_summary,
    action_summary,
    validation_report,
    dashboard_excel,
    dashboard_csv,
    management_summary,
    export_index
]


missing_files = [
    file_path
    for file_path in required_files
    if not file_path.exists()
]


if missing_files:

    print("\nWARNING: Some final files are missing:")

    for file_path in missing_files:
        print(file_path)

else:

    print(
        "\nAll major final project files are available."
    )


# ============================================================
# Step 5: Load Final Dataset
# ============================================================

if not final_dataset.exists():

    raise FileNotFoundError(
        "\nERROR: Final seller dataset was not found:\n"
        f"{final_dataset}"
    )


seller_data = pd.read_csv(
    final_dataset
)


# ============================================================
# Step 6: Calculate Project Statistics
# ============================================================

total_sellers = len(
    seller_data
)

total_revenue = (
    seller_data["total_revenue"]
    .sum()
)

total_profit = (
    seller_data["profit"]
    .sum()
)

critical_sellers = (
    seller_data["risk_category"]
    .eq("Critical Risk")
    .sum()
)

high_risk_sellers = (
    seller_data["risk_category"]
    .eq("High Risk")
    .sum()
)

immediate_sellers = (
    seller_data["action_priority"]
    .eq("Immediate")
    .sum()
)

high_priority_sellers = (
    seller_data["action_priority"]
    .eq("High")
    .sum()
)


# ============================================================
# Step 7: Create Deliverables Directory
# ============================================================

deliverables_directory = (
    project_root
    / "project_deliverables"
)


deliverables_directory.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Step 8: Create Project README
# ============================================================

readme_lines = [

    "# Enterprise Customer Intelligence",

    "",

    "## Project Overview",

    (
        "This project analyzes e-commerce seller performance, "
        "revenue, profitability, risk, priority, and recommended "
        "management actions."
    ),

    "",

    "## Final Seller Risk Analysis",

    (
        "The final analysis combines seller revenue, profit, "
        "risk scoring, business impact, priority scoring, "
        "and recommended management actions."
    ),

    "",

    "## Key Project Metrics",

    f"- Total Sellers Analyzed: {total_sellers}",

    f"- Total Revenue: {total_revenue:,.2f}",

    f"- Total Profit: {total_profit:,.2f}",

    f"- Critical Risk Sellers: {critical_sellers}",

    f"- High Risk Sellers: {high_risk_sellers}",

    f"- Immediate Action Sellers: {immediate_sellers}",

    f"- High Priority Sellers: {high_priority_sellers}",

    "",

    "## Main Deliverables",

    "",

    "### Final Dashboard",

    (
        "`final_output/final_seller_risk_dashboard.xlsx`"
    ),

    (
        "Complete Excel dashboard containing seller-level "
        "analysis, risk summary, action summary, and validation."
    ),

    "",

    "### Final Dataset",

    (
        "`data/final_seller_dashboard/"
        "seller_risk_action_final_dataset.csv`"
    ),

    (
        "Final seller-level dataset containing risk scores, "
        "priority scores, categories, flags, and management actions."
    ),

    "",

    "### Risk Summary",

    (
        "`data/final_seller_dashboard/"
        "final_risk_summary.csv`"
    ),

    (
        "Summary of sellers, revenue, profit, and risk categories."
    ),

    "",

    "### Action Summary",

    (
        "`data/final_seller_dashboard/"
        "final_action_summary.csv`"
    ),

    (
        "Summary of management action priorities."
    ),

    "",

    "### Validation Report",

    (
        "`data/final_seller_dashboard/"
        "seller_dashboard_validation_report.csv`"
    ),

    (
        "Data quality and consistency validation results."
    ),

    "",

    "### Management Summary",

    (
        "`final_output/"
        "final_seller_risk_management_summary.txt`"
    ),

    (
        "Management-level conclusions and recommended actions."
    ),

    "",

    "## Business Use Cases",

    "1. Identify high-risk sellers.",

    "2. Prioritize seller interventions.",

    "3. Monitor revenue exposure.",

    "4. Identify sellers requiring immediate attention.",

    "5. Support seller performance improvement.",

    "6. Support data-driven management decisions.",

    "",

    "## Analysis Pipeline",

    "Seller Revenue Analysis",

    "→ Seller ROI Analysis",

    "→ Seller Risk Analysis",

    "→ Seller Priority Analysis",

    "→ Seller Action Recommendation",

    "→ Risk Dashboard Charts",

    "→ Dashboard Summary",

    "→ Final Dataset",

    "→ Validation",

    "→ Final Dashboard Export",

    "",

    "## Final Status",

    "The seller risk analysis pipeline has been completed.",

    "The final dataset has been validated and exported.",

]


# ============================================================
# Step 9: Save README
# ============================================================

readme_path = (
    deliverables_directory
    / "README.md"
)


with open(
    readme_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(readme_lines)
    )


print("\nREADME created:")
print(readme_path)


# ============================================================
# Step 10: Create Project Statistics CSV
# ============================================================

statistics = pd.DataFrame(
    [
        {
            "metric": "Total Sellers",
            "value": total_sellers
        },
        {
            "metric": "Total Revenue",
            "value": round(
                total_revenue,
                2
            )
        },
        {
            "metric": "Total Profit",
            "value": round(
                total_profit,
                2
            )
        },
        {
            "metric": "Critical Risk Sellers",
            "value": critical_sellers
        },
        {
            "metric": "High Risk Sellers",
            "value": high_risk_sellers
        },
        {
            "metric": "Immediate Action Sellers",
            "value": immediate_sellers
        },
        {
            "metric": "High Priority Sellers",
            "value": high_priority_sellers
        }
    ]
)


statistics_path = (
    deliverables_directory
    / "project_statistics.csv"
)


statistics.to_csv(
    statistics_path,
    index=False
)


print("\nProject statistics saved:")
print(statistics_path)


# ============================================================
# Step 11: Create Deliverables Index
# ============================================================

deliverables = pd.DataFrame(
    [
        {
            "deliverable": "README",
            "path": "project_deliverables/README.md",
            "purpose": "Project documentation"
        },
        {
            "deliverable": "Final Seller Dataset",
            "path": (
                "data/final_seller_dashboard/"
                "seller_risk_action_final_dataset.csv"
            ),
            "purpose": "Final seller-level analysis"
        },
        {
            "deliverable": "Risk Summary",
            "path": (
                "data/final_seller_dashboard/"
                "final_risk_summary.csv"
            ),
            "purpose": "Seller risk summary"
        },
        {
            "deliverable": "Action Summary",
            "path": (
                "data/final_seller_dashboard/"
                "final_action_summary.csv"
            ),
            "purpose": "Management action summary"
        },
        {
            "deliverable": "Validation Report",
            "path": (
                "data/final_seller_dashboard/"
                "seller_dashboard_validation_report.csv"
            ),
            "purpose": "Data validation"
        },
        {
            "deliverable": "Final Excel Dashboard",
            "path": (
                "final_output/"
                "final_seller_risk_dashboard.xlsx"
            ),
            "purpose": "Complete dashboard"
        },
        {
            "deliverable": "Management Summary",
            "path": (
                "final_output/"
                "final_seller_risk_management_summary.txt"
            ),
            "purpose": "Business recommendations"
        }
    ]
)


deliverables_path = (
    deliverables_directory
    / "deliverables_index.csv"
)


deliverables.to_csv(
    deliverables_path,
    index=False
)


print("\nDeliverables index saved:")
print(deliverables_path)


# ============================================================
# Step 12: Display Final Project Summary
# ============================================================

print("\n============================================================")
print("FINAL PROJECT SUMMARY")
print("============================================================")

print(
    f"Total Sellers            : {total_sellers}"
)

print(
    f"Total Revenue            : {total_revenue:,.2f}"
)

print(
    f"Total Profit             : {total_profit:,.2f}"
)

print(
    f"Critical Risk Sellers    : {critical_sellers}"
)

print(
    f"High Risk Sellers        : {high_risk_sellers}"
)

print(
    f"Immediate Action Sellers : {immediate_sellers}"
)

print(
    f"High Priority Sellers    : {high_priority_sellers}"
)


# ============================================================
# Step 13: Completion
# ============================================================

print("\n============================================================")
print(
    "Step 96 Project README & Deliverables Summary "
    "completed successfully."
)
print("============================================================")