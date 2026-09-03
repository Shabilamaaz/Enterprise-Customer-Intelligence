import pandas as pd
from pathlib import Path


# ============================================================
# Step 95: Final Seller Risk Dashboard Export
# ============================================================

print("\n============================================================")
print("Step 95: Final Seller Risk Dashboard Export")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Locate Final Dashboard Files
# ============================================================

final_directory = (
    project_root
    / "data"
    / "final_seller_dashboard"
)

final_csv = (
    final_directory
    / "seller_risk_action_final_dataset.csv"
)

risk_summary_csv = (
    final_directory
    / "final_risk_summary.csv"
)

action_summary_csv = (
    final_directory
    / "final_action_summary.csv"
)

validation_csv = (
    final_directory
    / "seller_dashboard_validation_report.csv"
)


# ============================================================
# Step 3: Validate Required Files
# ============================================================

required_files = [
    final_csv,
    risk_summary_csv,
    action_summary_csv,
    validation_csv
]


for file_path in required_files:

    if not file_path.exists():

        raise FileNotFoundError(
            "\nERROR: Required file not found:\n"
            f"{file_path}"
        )


print("\nAll final dashboard files found successfully.")


# ============================================================
# Step 4: Load Final Data
# ============================================================

final_data = pd.read_csv(
    final_csv
)

risk_summary = pd.read_csv(
    risk_summary_csv
)

action_summary = pd.read_csv(
    action_summary_csv
)

validation_data = pd.read_csv(
    validation_csv
)


# ============================================================
# Step 5: Check Validation Status
# ============================================================

failed_checks = (
    validation_data["status"]
    .eq("FAILED")
    .sum()
)


if failed_checks > 0:

    raise RuntimeError(
        "\nERROR: Dashboard validation contains "
        f"{failed_checks} failed checks.\n"
        "Fix validation errors before creating "
        "the final export."
    )


print(
    "\nDashboard validation status: PASSED"
)


# ============================================================
# Step 6: Create Export Directory
# ============================================================

export_directory = (
    project_root
    / "final_output"
)


export_directory.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Step 7: Create Excel Workbook
# ============================================================

excel_path = (
    export_directory
    / "final_seller_risk_dashboard.xlsx"
)


with pd.ExcelWriter(
    excel_path,
    engine="openpyxl"
) as writer:

    final_data.to_excel(
        writer,
        sheet_name="Seller Dashboard",
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

    validation_data.to_excel(
        writer,
        sheet_name="Validation",
        index=False
    )


print(
    "\nFinal Excel dashboard saved to:"
)

print(excel_path)


# ============================================================
# Step 8: Create Final CSV Export
# ============================================================

csv_path = (
    export_directory
    / "final_seller_risk_dashboard.csv"
)


final_data.to_csv(
    csv_path,
    index=False
)


print(
    "\nFinal CSV dashboard saved to:"
)

print(csv_path)


# ============================================================
# Step 9: Create Management Summary
# ============================================================

total_sellers = len(final_data)

total_revenue = (
    final_data["total_revenue"]
    .sum()
)

total_profit = (
    final_data["profit"]
    .sum()
)

critical_sellers = (
    final_data["risk_category"]
    .eq("Critical Risk")
    .sum()
)

high_risk_sellers = (
    final_data["risk_category"]
    .eq("High Risk")
    .sum()
)

immediate_sellers = (
    final_data["action_priority"]
    .eq("Immediate")
    .sum()
)

high_priority_sellers = (
    final_data["action_priority"]
    .eq("High")
    .sum()
)


attention_data = final_data[
    final_data["action_priority"]
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


if total_revenue > 0:

    attention_percentage = (
        attention_revenue
        /
        total_revenue
    ) * 100

else:

    attention_percentage = 0


# ============================================================
# Step 10: Create Management Summary File
# ============================================================

summary_path = (
    export_directory
    / "final_seller_risk_management_summary.txt"
)


summary_lines = [
    "============================================================",
    "FINAL SELLER RISK MANAGEMENT SUMMARY",
    "============================================================",
    "",
    f"Total Sellers              : {total_sellers}",
    f"Total Revenue              : {total_revenue:,.2f}",
    f"Total Profit               : {total_profit:,.2f}",
    "",
    f"Critical Risk Sellers      : {critical_sellers}",
    f"High Risk Sellers          : {high_risk_sellers}",
    "",
    f"Immediate Action Sellers   : {immediate_sellers}",
    f"High Priority Sellers      : {high_priority_sellers}",
    "",
    f"Revenue Requiring Attention: "
    f"{attention_revenue:,.2f}",
    f"Attention Revenue %        : "
    f"{attention_percentage:.2f}%",
    "",
    "KEY RECOMMENDATIONS",
    "------------------------------------------------------------",
    "1. Review all Immediate Action sellers first.",
    "2. Prioritize High Action sellers for intervention.",
    "3. Monitor revenue exposure from high-risk sellers.",
    "4. Review seller performance regularly.",
    "5. Use the dashboard for management decision-making.",
    "",
    "Dashboard validation status: PASSED",
    "",
    "============================================================",
    "Final seller risk dashboard export completed successfully.",
    "============================================================"
]


with open(
    summary_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(summary_lines)
    )


print(
    "\nManagement summary saved to:"
)

print(summary_path)


# ============================================================
# Step 11: Create Export Index
# ============================================================

export_index = pd.DataFrame(
    [
        {
            "file_name":
                "final_seller_risk_dashboard.xlsx",
            "description":
                "Complete Excel dashboard"
        },
        {
            "file_name":
                "final_seller_risk_dashboard.csv",
            "description":
                "Final seller dashboard dataset"
        },
        {
            "file_name":
                "final_seller_risk_management_summary.txt",
            "description":
                "Management summary and recommendations"
        }
    ]
)


index_path = (
    export_directory
    / "final_export_index.csv"
)


export_index.to_csv(
    index_path,
    index=False
)


print(
    "\nFinal export index saved to:"
)

print(index_path)


# ============================================================
# Step 12: Final Statistics
# ============================================================

print("\n============================================================")
print("FINAL DASHBOARD STATISTICS")
print("============================================================")

print(
    f"Total sellers       : {total_sellers}"
)

print(
    f"Total revenue       : {total_revenue:,.2f}"
)

print(
    f"Total profit        : {total_profit:,.2f}"
)

print(
    f"Critical risk       : {critical_sellers}"
)

print(
    f"High risk           : {high_risk_sellers}"
)

print(
    f"Immediate action    : {immediate_sellers}"
)

print(
    f"High priority       : {high_priority_sellers}"
)

print(
    f"Attention revenue   : {attention_revenue:,.2f}"
)

print(
    f"Attention revenue % : {attention_percentage:.2f}%"
)


# ============================================================
# Step 13: Completion
# ============================================================

print("\n============================================================")
print(
    "Step 95 Final Seller Risk Dashboard Export "
    "completed successfully."
)
print("============================================================")