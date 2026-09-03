from pathlib import Path
import pandas as pd


# ============================================================
# Step 97: Final Project Quality & Deliverables Check
# ============================================================

print("\n============================================================")
print("Step 97: Final Project Quality & Deliverables Check")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Define Important Directories
# ============================================================

notebooks_directory = (
    project_root / "notebooks"
)

data_directory = (
    project_root / "data"
)

final_directory = (
    data_directory
    / "final_seller_dashboard"
)

output_directory = (
    project_root / "final_output"
)

deliverables_directory = (
    project_root / "project_deliverables"
)


# ============================================================
# Step 3: Required Project Files
# ============================================================

required_files = [
    final_directory
    / "seller_risk_action_final_dataset.csv",

    final_directory
    / "seller_risk_action_final_dataset.xlsx",

    final_directory
    / "final_risk_summary.csv",

    final_directory
    / "final_action_summary.csv",

    final_directory
    / "seller_dashboard_validation_report.csv",

    final_directory
    / "seller_dashboard_validation_summary.txt",

    output_directory
    / "final_seller_risk_dashboard.xlsx",

    output_directory
    / "final_seller_risk_dashboard.csv",

    output_directory
    / "final_seller_risk_management_summary.txt",

    output_directory
    / "final_export_index.csv",

    deliverables_directory
    / "README.md",

    deliverables_directory
    / "project_statistics.csv",

    deliverables_directory
    / "deliverables_index.csv"
]


# ============================================================
# Step 4: Check Required Files
# ============================================================

file_results = []


for file_path in required_files:

    exists = file_path.exists()

    file_results.append(
        {
            "file": str(
                file_path.relative_to(
                    project_root
                )
            ),
            "status": (
                "PASSED"
                if exists
                else "FAILED"
            )
        }
    )


file_check = pd.DataFrame(
    file_results
)


# ============================================================
# Step 5: Check Final Dataset
# ============================================================

final_dataset_path = (
    final_directory
    / "seller_risk_action_final_dataset.csv"
)


final_data = pd.read_csv(
    final_dataset_path
)


dataset_checks = []


# Dataset not empty

dataset_checks.append(
    {
        "check": "Final dataset not empty",
        "status": (
            "PASSED"
            if not final_data.empty
            else "FAILED"
        ),
        "details": (
            f"{len(final_data)} seller records"
        )
    }
)


# Required columns

required_columns = [
    "seller_rank",
    "seller_id",
    "total_orders",
    "total_revenue",
    "profit",
    "profit_margin",
    "risk_score",
    "priority_score",
    "risk_category",
    "risk_flag",
    "action_priority",
    "management_action"
]


missing_columns = [
    column
    for column in required_columns
    if column not in final_data.columns
]


dataset_checks.append(
    {
        "check": "Required columns",
        "status": (
            "FAILED"
            if missing_columns
            else "PASSED"
        ),
        "details": (
            "Missing: "
            + ", ".join(missing_columns)
            if missing_columns
            else "All required columns present"
        )
    }
)


# Duplicate sellers

duplicate_count = (
    final_data["seller_id"]
    .duplicated()
    .sum()
)


dataset_checks.append(
    {
        "check": "Duplicate sellers",
        "status": (
            "FAILED"
            if duplicate_count > 0
            else "PASSED"
        ),
        "details": (
            f"{duplicate_count} duplicates"
        )
    }
)


# Null values

null_count = (
    final_data[required_columns]
    .isnull()
    .sum()
    .sum()
)


dataset_checks.append(
    {
        "check": "Required fields without nulls",
        "status": (
            "FAILED"
            if null_count > 0
            else "PASSED"
        ),
        "details": (
            f"{null_count} null values"
        )
    }
)


# ============================================================
# Step 6: Check Risk Categories
# ============================================================

valid_risk_categories = {
    "Critical Risk",
    "High Risk",
    "Medium Risk",
    "Low Risk",
    "Healthy"
}


invalid_risk_categories = (
    set(
        final_data["risk_category"]
        .dropna()
        .unique()
    )
    -
    valid_risk_categories
)


dataset_checks.append(
    {
        "check": "Risk categories",
        "status": (
            "FAILED"
            if invalid_risk_categories
            else "PASSED"
        ),
        "details": (
            "Invalid: "
            + ", ".join(
                sorted(invalid_risk_categories)
            )
            if invalid_risk_categories
            else "All categories valid"
        )
    }
)


# ============================================================
# Step 7: Check Action Priorities
# ============================================================

valid_action_priorities = {
    "Immediate",
    "High",
    "Medium",
    "Low",
    "Maintain"
}


invalid_actions = (
    set(
        final_data["action_priority"]
        .dropna()
        .unique()
    )
    -
    valid_action_priorities
)


dataset_checks.append(
    {
        "check": "Action priorities",
        "status": (
            "FAILED"
            if invalid_actions
            else "PASSED"
        ),
        "details": (
            "Invalid: "
            + ", ".join(
                sorted(invalid_actions)
            )
            if invalid_actions
            else "All action priorities valid"
        )
    }
)


# ============================================================
# Step 8: Check Risk Score Range
# ============================================================

invalid_risk_scores = (
    (
        final_data["risk_score"] < 0
    )
    |
    (
        final_data["risk_score"] > 100
    )
).sum()


dataset_checks.append(
    {
        "check": "Risk score range",
        "status": (
            "FAILED"
            if invalid_risk_scores > 0
            else "PASSED"
        ),
        "details": (
            f"{invalid_risk_scores} invalid scores"
        )
    }
)


# ============================================================
# Step 9: Check Priority Score Range
# ============================================================

invalid_priority_scores = (
    (
        final_data["priority_score"] < 0
    )
    |
    (
        final_data["priority_score"] > 100
    )
).sum()


dataset_checks.append(
    {
        "check": "Priority score range",
        "status": (
            "FAILED"
            if invalid_priority_scores > 0
            else "PASSED"
        ),
        "details": (
            f"{invalid_priority_scores} invalid scores"
        )
    }
)


# ============================================================
# Step 10: Check Revenue Values
# ============================================================

negative_revenue = (
    final_data["total_revenue"] < 0
).sum()


dataset_checks.append(
    {
        "check": "Revenue values",
        "status": (
            "FAILED"
            if negative_revenue > 0
            else "PASSED"
        ),
        "details": (
            f"{negative_revenue} negative values"
        )
    }
)


# ============================================================
# Step 11: Check Profit Margin
# ============================================================

calculated_margin = (
    final_data["profit"]
    /
    final_data["total_revenue"]
    * 100
)


calculated_margin = (
    calculated_margin
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


margin_difference = (
    calculated_margin
    -
    final_data["profit_margin"]
).abs()


incorrect_margin = (
    margin_difference > 0.1
).sum()


dataset_checks.append(
    {
        "check": "Profit margin calculation",
        "status": (
            "FAILED"
            if incorrect_margin > 0
            else "PASSED"
        ),
        "details": (
            f"{incorrect_margin} mismatches"
        )
    }
)


# ============================================================
# Step 12: Combine Quality Checks
# ============================================================

quality_checks = pd.DataFrame(
    dataset_checks
)


# ============================================================
# Step 13: Check Validation Report
# ============================================================

validation_path = (
    final_directory
    / "seller_dashboard_validation_report.csv"
)


validation_data = pd.read_csv(
    validation_path
)


validation_failures = (
    validation_data["status"]
    .eq("FAILED")
    .sum()
)


quality_checks = pd.concat(
    [
        quality_checks,
        pd.DataFrame(
            [
                {
                    "check":
                        "Previous validation report",
                    "status": (
                        "FAILED"
                        if validation_failures > 0
                        else "PASSED"
                    ),
                    "details": (
                        f"{validation_failures} "
                        "failed validation checks"
                    )
                }
            ]
        )
    ],
    ignore_index=True
)


# ============================================================
# Step 14: Overall Status
# ============================================================

failed_files = (
    file_check["status"]
    .eq("FAILED")
    .sum()
)

failed_quality_checks = (
    quality_checks["status"]
    .eq("FAILED")
    .sum()
)


total_failures = (
    failed_files
    +
    failed_quality_checks
)


overall_status = (
    "PASSED"
    if total_failures == 0
    else "FAILED"
)


# ============================================================
# Step 15: Display File Check
# ============================================================

print("\n============================================================")
print("Required File Check")
print("============================================================")

print(
    file_check.to_string(
        index=False
    )
)


# ============================================================
# Step 16: Display Quality Check
# ============================================================

print("\n============================================================")
print("Dataset Quality Check")
print("============================================================")

print(
    quality_checks.to_string(
        index=False
    )
)


# ============================================================
# Step 17: Final Statistics
# ============================================================

print("\n============================================================")
print("FINAL QUALITY STATUS")
print("============================================================")

print(
    f"Required files checked : "
    f"{len(file_check)}"
)

print(
    f"Missing files          : "
    f"{failed_files}"
)

print(
    f"Quality checks         : "
    f"{len(quality_checks)}"
)

print(
    f"Failed quality checks  : "
    f"{failed_quality_checks}"
)

print(
    f"Overall status         : "
    f"{overall_status}"
)


# ============================================================
# Step 18: Save Quality Report
# ============================================================

quality_directory = (
    project_root
    / "project_deliverables"
)


quality_report_path = (
    quality_directory
    / "final_project_quality_report.csv"
)


quality_checks.to_csv(
    quality_report_path,
    index=False
)


print("\nQuality report saved to:")
print(quality_report_path)


# ============================================================
# Step 19: Save Complete Project Check
# ============================================================

complete_check_path = (
    quality_directory
    / "complete_project_check.txt"
)


with open(
    complete_check_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "ENTERPRISE CUSTOMER INTELLIGENCE\n"
    )

    file.write(
        "FINAL PROJECT QUALITY CHECK\n"
    )

    file.write(
        "========================================\n\n"
    )

    file.write(
        f"Final seller records: "
        f"{len(final_data)}\n"
    )

    file.write(
        f"Missing files: "
        f"{failed_files}\n"
    )

    file.write(
        f"Failed quality checks: "
        f"{failed_quality_checks}\n"
    )

    file.write(
        f"Overall status: "
        f"{overall_status}\n"
    )


print("\nComplete project check saved to:")
print(complete_check_path)


# ============================================================
# Step 20: Completion
# ============================================================

print("\n============================================================")

if overall_status == "PASSED":

    print(
        "Step 97 Final Project Quality Check "
        "completed successfully."
    )

else:

    print(
        "Step 97 completed with errors. "
        "Please review the quality report."
    )

print("============================================================")