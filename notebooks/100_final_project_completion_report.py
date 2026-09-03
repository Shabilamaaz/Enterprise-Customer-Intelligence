from pathlib import Path
import pandas as pd
from datetime import datetime


# ============================================================
# Step 100: Final Project Completion Report
# ============================================================

print("\n============================================================")
print("Step 100: Final Project Completion Report")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Define Important Paths
# ============================================================

final_output = project_root / "final_output"
deliverables = project_root / "project_deliverables"
final_dashboard = final_output / "final_seller_risk_dashboard.xlsx"
final_csv = final_output / "final_seller_risk_dashboard.csv"
readme = project_root / "README.md"


# ============================================================
# Step 3: Check Final Deliverables
# ============================================================

required_files = {
    "README": readme,
    "Final Excel Dashboard": final_dashboard,
    "Final CSV Dashboard": final_csv,
    "Management Summary":
        final_output / "final_seller_risk_management_summary.txt",
    "Export Index":
        final_output / "final_export_index.csv",
    "Quality Report":
        deliverables / "final_project_quality_report.csv",
    "GitHub Readiness Report":
        deliverables / "github_readiness_report.csv",
    "GitHub Structure Report":
        deliverables / "final_github_project_structure_report.csv",
    "GitHub Status":
        deliverables / "final_github_status.txt"
}


results = []

for name, path in required_files.items():

    results.append(
        {
            "deliverable": name,
            "status": (
                "PASSED"
                if path.exists()
                else "FAILED"
            ),
            "path": str(
                path.relative_to(project_root)
            )
        }
    )


results_df = pd.DataFrame(results)


# ============================================================
# Step 4: Load Final Dataset
# ============================================================

if not final_csv.exists():

    raise FileNotFoundError(
        "\nERROR: Final CSV dashboard not found:\n"
        f"{final_csv}"
    )


final_data = pd.read_csv(
    final_csv
)


# ============================================================
# Step 5: Calculate Final Business Metrics
# ============================================================

total_sellers = len(final_data)

total_orders = (
    final_data["total_orders"]
    .sum()
)

total_revenue = (
    final_data["total_revenue"]
    .sum()
)

total_profit = (
    final_data["profit"]
    .sum()
)

average_risk = (
    final_data["risk_score"]
    .mean()
)

average_priority = (
    final_data["priority_score"]
    .mean()
)

critical_risk = (
    final_data["risk_category"]
    .eq("Critical Risk")
    .sum()
)

high_risk = (
    final_data["risk_category"]
    .eq("High Risk")
    .sum()
)

immediate_action = (
    final_data["action_priority"]
    .eq("Immediate")
    .sum()
)

high_action = (
    final_data["action_priority"]
    .eq("High")
    .sum()
)


# ============================================================
# Step 6: Determine Project Status
# ============================================================

failed_deliverables = (
    results_df["status"]
    .eq("FAILED")
    .sum()
)


if failed_deliverables == 0:

    project_status = "COMPLETED"

else:

    project_status = "INCOMPLETE"


# ============================================================
# Step 7: Display Deliverable Status
# ============================================================

print("\n============================================================")
print("FINAL DELIVERABLE STATUS")
print("============================================================")

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# Step 8: Display Business Summary
# ============================================================

print("\n============================================================")
print("FINAL BUSINESS SUMMARY")
print("============================================================")

print(
    f"Total Sellers       : {total_sellers}"
)

print(
    f"Total Orders        : {total_orders}"
)

print(
    f"Total Revenue       : {total_revenue:,.2f}"
)

print(
    f"Total Profit        : {total_profit:,.2f}"
)

print(
    f"Average Risk Score  : {average_risk:.2f}"
)

print(
    f"Average Priority    : {average_priority:.2f}"
)

print(
    f"Critical Risk       : {critical_risk}"
)

print(
    f"High Risk           : {high_risk}"
)

print(
    f"Immediate Action    : {immediate_action}"
)

print(
    f"High Action         : {high_action}"
)


# ============================================================
# Step 9: Create Completion Report
# ============================================================

completion_report = (
    deliverables
    / "FINAL_PROJECT_COMPLETION_REPORT.md"
)


report = f"""# Enterprise Customer Intelligence

## Final Project Completion Report

**Project Status:** {project_status}

**Generated On:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Final Business Metrics

| Metric | Value |
|---|---:|
| Total Sellers | {total_sellers} |
| Total Orders | {total_orders} |
| Total Revenue | {total_revenue:,.2f} |
| Total Profit | {total_profit:,.2f} |
| Average Risk Score | {average_risk:.2f} |
| Average Priority Score | {average_priority:.2f} |
| Critical Risk Sellers | {critical_risk} |
| High Risk Sellers | {high_risk} |
| Immediate Action Sellers | {immediate_action} |
| High Priority Sellers | {high_action} |

---

## Final Deliverables

All major project deliverables were checked automatically.

{chr(10).join(
    f"- **{row['deliverable']}** — {row['status']}"
    for _, row in results_df.iterrows()
)}

---

## Final Dashboard

The final seller risk dashboard contains:

- Seller-level performance
- Revenue analysis
- Profit analysis
- Risk scoring
- Priority scoring
- Risk categories
- Risk flags
- Management actions
- Risk summary
- Action summary
- Validation results

---

## Business Objective

The project provides a data-driven framework to identify seller risks,
prioritize interventions, and support management decision-making.

---

## Final Status

**{project_status}**

The project completion report was generated automatically by Step 100.
"""


with open(
    completion_report,
    "w",
    encoding="utf-8"
) as file:

    file.write(report)


# ============================================================
# Step 10: Save Completion CSV
# ============================================================

completion_csv = (
    deliverables
    / "final_project_completion_status.csv"
)


results_df.to_csv(
    completion_csv,
    index=False
)


# ============================================================
# Step 11: Final Output
# ============================================================

print("\n============================================================")
print("FINAL PROJECT STATUS")
print("============================================================")

print(
    f"Failed deliverables : {failed_deliverables}"
)

print(
    f"Project status      : {project_status}"
)

print("\nCompletion report:")
print(completion_report)

print("\nCompletion CSV:")
print(completion_csv)


# ============================================================
# Step 12: Completion Message
# ============================================================

print("\n============================================================")

if project_status == "COMPLETED":

    print(
        "STEP 100 COMPLETED SUCCESSFULLY."
    )

    print(
        "\n🎉 Enterprise Customer Intelligence "
        "project is COMPLETE."
    )

else:

    print(
        "STEP 100 FOUND MISSING DELIVERABLES."
    )

print("============================================================")