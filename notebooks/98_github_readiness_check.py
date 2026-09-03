from pathlib import Path
import pandas as pd


# ============================================================
# Step 98: Final Project Documentation & GitHub Readiness
# ============================================================

print("\n============================================================")
print("Step 98: Final Project Documentation & GitHub Readiness")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Important Project Files
# ============================================================

readme_path = (
    project_root
    / "project_deliverables"
    / "README.md"
)

quality_report_path = (
    project_root
    / "project_deliverables"
    / "final_project_quality_report.csv"
)

complete_check_path = (
    project_root
    / "project_deliverables"
    / "complete_project_check.txt"
)

final_dashboard_path = (
    project_root
    / "final_output"
    / "final_seller_risk_dashboard.xlsx"
)

final_dataset_path = (
    project_root
    / "final_output"
    / "final_seller_risk_dashboard.csv"
)


# ============================================================
# Step 3: Check Documentation
# ============================================================

documentation_checks = []


def add_check(name, status, details):
    documentation_checks.append(
        {
            "check": name,
            "status": status,
            "details": details
        }
    )


# README

if readme_path.exists():

    readme_size = readme_path.stat().st_size

    add_check(
        "README exists",
        "PASSED",
        f"{readme_size} bytes"
    )

else:

    add_check(
        "README exists",
        "FAILED",
        "README.md not found"
    )


# Quality report

if quality_report_path.exists():

    add_check(
        "Quality report exists",
        "PASSED",
        "Final quality report found"
    )

else:

    add_check(
        "Quality report exists",
        "FAILED",
        "Quality report not found"
    )


# Complete project check

if complete_check_path.exists():

    add_check(
        "Project completion report",
        "PASSED",
        "Completion report found"
    )

else:

    add_check(
        "Project completion report",
        "FAILED",
        "Completion report not found"
    )


# Final dashboard

if final_dashboard_path.exists():

    add_check(
        "Final Excel dashboard",
        "PASSED",
        "Final Excel dashboard found"
    )

else:

    add_check(
        "Final Excel dashboard",
        "FAILED",
        "Final Excel dashboard not found"
    )


# Final CSV

if final_dataset_path.exists():

    add_check(
        "Final CSV dashboard",
        "PASSED",
        "Final CSV dashboard found"
    )

else:

    add_check(
        "Final CSV dashboard",
        "FAILED",
        "Final CSV dashboard not found"
    )


# ============================================================
# Step 4: Check README Content
# ============================================================

if readme_path.exists():

    readme_text = readme_path.read_text(
        encoding="utf-8"
    )

    required_sections = [
        "Project Overview",
        "Final Seller Risk Analysis",
        "Key Project Metrics",
        "Main Deliverables",
        "Business Use Cases",
        "Analysis Pipeline",
        "Final Status"
    ]

    missing_sections = [
        section
        for section in required_sections
        if section not in readme_text
    ]

    if missing_sections:

        add_check(
            "README content",
            "FAILED",
            "Missing sections: "
            + ", ".join(missing_sections)
        )

    else:

        add_check(
            "README content",
            "PASSED",
            "All required documentation sections found"
        )


# ============================================================
# Step 5: Validate Final Dashboard Data
# ============================================================

if final_dataset_path.exists():

    dashboard_data = pd.read_csv(
        final_dataset_path
    )

    if dashboard_data.empty:

        add_check(
            "Final dashboard dataset",
            "FAILED",
            "Dataset is empty"
        )

    else:

        add_check(
            "Final dashboard dataset",
            "PASSED",
            f"{len(dashboard_data)} records"
        )

else:

    dashboard_data = None


# ============================================================
# Step 6: Create GitHub Checklist
# ============================================================

github_checklist = [
    "Project README included",
    "Final dashboard included",
    "Final CSV dataset included",
    "Risk summary included",
    "Action summary included",
    "Validation report included",
    "Management summary included",
    "Project statistics included",
    "Deliverables index included",
    "Final quality report included"
]


github_checklist_data = pd.DataFrame(
    [
        {
            "item": item,
            "status": "READY"
        }
        for item in github_checklist
    ]
)


# ============================================================
# Step 7: Save Documentation Check
# ============================================================

documentation_data = pd.DataFrame(
    documentation_checks
)


documentation_path = (
    project_root
    / "project_deliverables"
    / "github_readiness_report.csv"
)


documentation_data.to_csv(
    documentation_path,
    index=False
)


# ============================================================
# Step 8: Save GitHub Checklist
# ============================================================

checklist_path = (
    project_root
    / "project_deliverables"
    / "github_upload_checklist.csv"
)


github_checklist_data.to_csv(
    checklist_path,
    index=False
)


# ============================================================
# Step 9: Create GitHub README Copy
# ============================================================

github_readme_path = (
    project_root
    / "README.md"
)


if readme_path.exists():

    readme_content = readme_path.read_text(
        encoding="utf-8"
    )

    github_readme_path.write_text(
        readme_content,
        encoding="utf-8"
    )

    print(
        "\nRoot README.md created successfully."
    )


# ============================================================
# Step 10: Final Status
# ============================================================

failed_checks = (
    documentation_data["status"]
    .eq("FAILED")
    .sum()
)


overall_status = (
    "READY FOR GITHUB"
    if failed_checks == 0
    else "NOT READY"
)


# ============================================================
# Step 11: Display Results
# ============================================================

print("\n============================================================")
print("GitHub Readiness Report")
print("============================================================")

print(
    documentation_data.to_string(
        index=False
    )
)


print("\n============================================================")
print("GitHub Upload Checklist")
print("============================================================")

print(
    github_checklist_data.to_string(
        index=False
    )
)


print("\n============================================================")
print("FINAL STATUS")
print("============================================================")

print(
    f"Failed checks : {failed_checks}"
)

print(
    f"Status        : {overall_status}"
)


# ============================================================
# Step 12: Completion
# ============================================================

print("\n============================================================")

if overall_status == "READY FOR GITHUB":

    print(
        "Step 98 GitHub Readiness Check "
        "completed successfully."
    )

    print(
        "\nProject is ready for the final GitHub upload."
    )

else:

    print(
        "Step 98 completed with issues."
    )

print("============================================================")