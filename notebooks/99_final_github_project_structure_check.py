from pathlib import Path
import pandas as pd


# ============================================================
# Step 99: Final GitHub Project Structure Check
# ============================================================

print("\n============================================================")
print("Step 99: Final GitHub Project Structure Check")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent

print("\nProject root:")
print(project_root)


# ============================================================
# Step 2: Expected Project Structure
# ============================================================

expected_directories = [
    "data",
    "notebooks",
    "project_deliverables",
    "final_output"
]


expected_files = [
    "README.md",
    "project_deliverables/README.md",
    "project_deliverables/project_statistics.csv",
    "project_deliverables/deliverables_index.csv",
    "project_deliverables/final_project_quality_report.csv",
    "project_deliverables/github_readiness_report.csv",
    "project_deliverables/github_upload_checklist.csv",
    "final_output/final_seller_risk_dashboard.xlsx",
    "final_output/final_seller_risk_dashboard.csv",
    "final_output/final_seller_risk_management_summary.txt",
    "final_output/final_export_index.csv"
]


# ============================================================
# Step 3: Check Directories
# ============================================================

directory_results = []

for directory in expected_directories:

    directory_path = (
        project_root / directory
    )

    directory_results.append(
        {
            "directory": directory,
            "status": (
                "PASSED"
                if directory_path.exists()
                else "FAILED"
            )
        }
    )


directory_data = pd.DataFrame(
    directory_results
)


# ============================================================
# Step 4: Check Files
# ============================================================

file_results = []

for relative_file in expected_files:

    file_path = (
        project_root / relative_file
    )

    file_results.append(
        {
            "file": relative_file,
            "status": (
                "PASSED"
                if file_path.exists()
                else "FAILED"
            )
        }
    )


file_data = pd.DataFrame(
    file_results
)


# ============================================================
# Step 5: Check Notebook Count
# ============================================================

notebook_directory = (
    project_root / "notebooks"
)

python_files = list(
    notebook_directory.glob("*.py")
)


print(
    f"\nPython analysis files found: "
    f"{len(python_files)}"
)


if len(python_files) > 0:

    notebook_status = "PASSED"

    notebook_details = (
        f"{len(python_files)} Python files found"
    )

else:

    notebook_status = "FAILED"

    notebook_details = (
        "No Python analysis files found"
    )


# ============================================================
# Step 6: Check Final Dashboard
# ============================================================

dashboard_path = (
    project_root
    / "final_output"
    / "final_seller_risk_dashboard.xlsx"
)


if dashboard_path.exists():

    dashboard_size = (
        dashboard_path.stat().st_size
    )

    dashboard_status = "PASSED"

    dashboard_details = (
        f"{dashboard_size:,} bytes"
    )

else:

    dashboard_status = "FAILED"

    dashboard_details = (
        "Dashboard not found"
    )


# ============================================================
# Step 7: Check Final Dataset
# ============================================================

dataset_path = (
    project_root
    / "final_output"
    / "final_seller_risk_dashboard.csv"
)


if dataset_path.exists():

    final_data = pd.read_csv(
        dataset_path
    )

    if final_data.empty:

        dataset_status = "FAILED"

        dataset_details = (
            "Final dataset is empty"
        )

    else:

        dataset_status = "PASSED"

        dataset_details = (
            f"{len(final_data)} seller records"
        )

else:

    dataset_status = "FAILED"

    dataset_details = (
        "Final dataset not found"
    )


# ============================================================
# Step 8: Create Structure Summary
# ============================================================

structure_checks = []


structure_checks.append(
    {
        "check": "Project directories",
        "status": (
            "PASSED"
            if (
                directory_data["status"]
                .eq("FAILED")
                .sum()
                == 0
            )
            else "FAILED"
        ),
        "details": (
            f"{len(directory_data)} directories checked"
        )
    }
)


structure_checks.append(
    {
        "check": "Project files",
        "status": (
            "PASSED"
            if (
                file_data["status"]
                .eq("FAILED")
                .sum()
                == 0
            )
            else "FAILED"
        ),
        "details": (
            f"{len(file_data)} files checked"
        )
    }
)


structure_checks.append(
    {
        "check": "Python analysis files",
        "status": notebook_status,
        "details": notebook_details
    }
)


structure_checks.append(
    {
        "check": "Final Excel dashboard",
        "status": dashboard_status,
        "details": dashboard_details
    }
)


structure_checks.append(
    {
        "check": "Final CSV dataset",
        "status": dataset_status,
        "details": dataset_details
    }
)


structure_data = pd.DataFrame(
    structure_checks
)


# ============================================================
# Step 9: Display Directory Check
# ============================================================

print("\n============================================================")
print("Directory Check")
print("============================================================")

print(
    directory_data.to_string(
        index=False
    )
)


# ============================================================
# Step 10: Display File Check
# ============================================================

print("\n============================================================")
print("Required File Check")
print("============================================================")

print(
    file_data.to_string(
        index=False
    )
)


# ============================================================
# Step 11: Display Final Structure Check
# ============================================================

print("\n============================================================")
print("Final Structure Check")
print("============================================================")

print(
    structure_data.to_string(
        index=False
    )
)


# ============================================================
# Step 12: Calculate Overall Status
# ============================================================

failed_directories = (
    directory_data["status"]
    .eq("FAILED")
    .sum()
)

failed_files = (
    file_data["status"]
    .eq("FAILED")
    .sum()
)

failed_structure_checks = (
    structure_data["status"]
    .eq("FAILED")
    .sum()
)


total_failures = (
    failed_directories
    +
    failed_files
    +
    failed_structure_checks
)


if total_failures == 0:

    overall_status = "READY"

else:

    overall_status = "CHECK REQUIRED"


# ============================================================
# Step 13: Save Structure Report
# ============================================================

report_directory = (
    project_root
    / "project_deliverables"
)

report_directory.mkdir(
    parents=True,
    exist_ok=True
)


report_path = (
    report_directory
    / "final_github_project_structure_report.csv"
)


structure_data.to_csv(
    report_path,
    index=False
)


print("\nStructure report saved to:")
print(report_path)


# ============================================================
# Step 14: Save Final GitHub Status
# ============================================================

status_path = (
    report_directory
    / "final_github_status.txt"
)


with open(
    status_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "ENTERPRISE CUSTOMER INTELLIGENCE\n"
    )

    file.write(
        "FINAL GITHUB PROJECT STATUS\n"
    )

    file.write(
        "========================================\n\n"
    )

    file.write(
        f"Directories checked : "
        f"{len(directory_data)}\n"
    )

    file.write(
        f"Files checked       : "
        f"{len(file_data)}\n"
    )

    file.write(
        f"Python files        : "
        f"{len(python_files)}\n"
    )

    file.write(
        f"Failed checks       : "
        f"{total_failures}\n"
    )

    file.write(
        f"Final status        : "
        f"{overall_status}\n"
    )


print("\nFinal GitHub status saved to:")
print(status_path)


# ============================================================
# Step 15: Final Output
# ============================================================

print("\n============================================================")
print("FINAL GITHUB STATUS")
print("============================================================")

print(
    f"Directories checked : {len(directory_data)}"
)

print(
    f"Files checked       : {len(file_data)}"
)

print(
    f"Python files        : {len(python_files)}"
)

print(
    f"Failed checks       : {total_failures}"
)

print(
    f"Final status        : {overall_status}"
)


# ============================================================
# Step 16: Completion
# ============================================================

print("\n============================================================")

if overall_status == "READY":

    print(
        "Step 99 Final GitHub Project Structure Check "
        "completed successfully."
    )

    print(
        "\nProject structure is ready for GitHub."
    )

else:

    print(
        "Step 99 completed with issues."
    )

    print(
        "Please review the structure report."
    )

print("============================================================")