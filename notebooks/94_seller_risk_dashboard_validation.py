import pandas as pd
from pathlib import Path


# ============================================================
# Step 94: Seller Risk Dashboard Validation
# ============================================================

print("\n============================================================")
print("Step 94: Seller Risk Dashboard Validation")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Locate Final Dataset
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


# ============================================================
# Step 3: Validate Files
# ============================================================

required_files = [
    final_csv,
    risk_summary_csv,
    action_summary_csv
]


for file_path in required_files:

    if not file_path.exists():

        raise FileNotFoundError(
            "\nERROR: Required Step 93 file was not found:\n"
            f"{file_path}"
        )


print("\nAll required Step 93 files found.")


# ============================================================
# Step 4: Load Data
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


print(
    f"\nFinal dataset records: "
    f"{len(final_data)}"
)


# ============================================================
# Step 5: Validation Results
# ============================================================

validation_results = []


def add_result(check, status, details):

    validation_results.append(
        {
            "check": check,
            "status": status,
            "details": details
        }
    )


# ============================================================
# Step 6: Check Empty Dataset
# ============================================================

if final_data.empty:

    add_result(
        "Dataset not empty",
        "FAILED",
        "Final seller dataset contains no records."
    )

else:

    add_result(
        "Dataset not empty",
        "PASSED",
        f"{len(final_data)} seller records found."
    )


# ============================================================
# Step 7: Required Column Validation
# ============================================================

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


if missing_columns:

    add_result(
        "Required columns",
        "FAILED",
        "Missing columns: "
        + ", ".join(missing_columns)
    )

else:

    add_result(
        "Required columns",
        "PASSED",
        "All required columns are present."
    )


# ============================================================
# Step 8: Duplicate Seller Validation
# ============================================================

duplicate_sellers = (
    final_data["seller_id"]
    .duplicated()
    .sum()
)


if duplicate_sellers > 0:

    add_result(
        "Duplicate seller IDs",
        "FAILED",
        f"{duplicate_sellers} duplicate seller records found."
    )

else:

    add_result(
        "Duplicate seller IDs",
        "PASSED",
        "No duplicate seller IDs found."
    )


# ============================================================
# Step 9: Null Value Validation
# ============================================================

null_count = (
    final_data[required_columns]
    .isnull()
    .sum()
    .sum()
)


if null_count > 0:

    add_result(
        "Required fields without nulls",
        "FAILED",
        f"{null_count} null values found."
    )

else:

    add_result(
        "Required fields without nulls",
        "PASSED",
        "No null values found in required fields."
    )


# ============================================================
# Step 10: Numeric Validation
# ============================================================

numeric_columns = [
    "total_orders",
    "total_revenue",
    "profit",
    "profit_margin",
    "risk_score",
    "priority_score"
]


numeric_errors = []


for column in numeric_columns:

    converted = pd.to_numeric(
        final_data[column],
        errors="coerce"
    )

    errors = converted.isnull().sum()

    if errors > 0:

        numeric_errors.append(
            f"{column}: {errors}"
        )


if numeric_errors:

    add_result(
        "Numeric fields",
        "FAILED",
        "; ".join(numeric_errors)
    )

else:

    add_result(
        "Numeric fields",
        "PASSED",
        "All numeric fields contain valid numbers."
    )


# ============================================================
# Step 11: Revenue Validation
# ============================================================

negative_revenue = (
    final_data["total_revenue"] < 0
).sum()


if negative_revenue > 0:

    add_result(
        "Revenue values",
        "FAILED",
        f"{negative_revenue} negative revenue values found."
    )

else:

    add_result(
        "Revenue values",
        "PASSED",
        "No negative revenue values found."
    )


# ============================================================
# Step 12: Order Count Validation
# ============================================================

invalid_orders = (
    final_data["total_orders"] < 0
).sum()


if invalid_orders > 0:

    add_result(
        "Order counts",
        "FAILED",
        f"{invalid_orders} invalid order counts found."
    )

else:

    add_result(
        "Order counts",
        "PASSED",
        "All order counts are valid."
    )


# ============================================================
# Step 13: Risk Score Validation
# ============================================================

invalid_risk_scores = (
    (final_data["risk_score"] < 0)
    |
    (final_data["risk_score"] > 100)
).sum()


if invalid_risk_scores > 0:

    add_result(
        "Risk score range",
        "FAILED",
        f"{invalid_risk_scores} risk scores outside 0-100."
    )

else:

    add_result(
        "Risk score range",
        "PASSED",
        "All risk scores are within 0-100."
    )


# ============================================================
# Step 14: Priority Score Validation
# ============================================================

invalid_priority_scores = (
    (final_data["priority_score"] < 0)
    |
    (final_data["priority_score"] > 100)
).sum()


if invalid_priority_scores > 0:

    add_result(
        "Priority score range",
        "FAILED",
        f"{invalid_priority_scores} priority scores outside 0-100."
    )

else:

    add_result(
        "Priority score range",
        "PASSED",
        "All priority scores are within 0-100."
    )


# ============================================================
# Step 15: Risk Category Validation
# ============================================================

valid_risk_categories = {
    "Critical Risk",
    "High Risk",
    "Medium Risk",
    "Low Risk",
    "Healthy"
}


invalid_risk_categories = set(
    final_data["risk_category"].dropna().unique()
) - valid_risk_categories


if invalid_risk_categories:

    add_result(
        "Risk categories",
        "FAILED",
        "Invalid categories: "
        + ", ".join(
            sorted(invalid_risk_categories)
        )
    )

else:

    add_result(
        "Risk categories",
        "PASSED",
        "All risk categories are valid."
    )


# ============================================================
# Step 16: Risk Flag Validation
# ============================================================

valid_flags = {
    "RED",
    "ORANGE",
    "YELLOW",
    "BLUE",
    "GREEN"
}


invalid_flags = set(
    final_data["risk_flag"].dropna().unique()
) - valid_flags


if invalid_flags:

    add_result(
        "Risk flags",
        "FAILED",
        "Invalid flags: "
        + ", ".join(
            sorted(invalid_flags)
        )
    )

else:

    add_result(
        "Risk flags",
        "PASSED",
        "All risk flags are valid."
    )


# ============================================================
# Step 17: Action Priority Validation
# ============================================================

valid_actions = {
    "Immediate",
    "High",
    "Medium",
    "Low",
    "Maintain"
}


invalid_actions = set(
    final_data["action_priority"].dropna().unique()
) - valid_actions


if invalid_actions:

    add_result(
        "Action priorities",
        "FAILED",
        "Invalid priorities: "
        + ", ".join(
            sorted(invalid_actions)
        )
    )

else:

    add_result(
        "Action priorities",
        "PASSED",
        "All action priorities are valid."
    )


# ============================================================
# Step 18: Rank Validation
# ============================================================

expected_ranks = set(
    range(
        1,
        len(final_data) + 1
    )
)


actual_ranks = set(
    final_data["seller_rank"]
    .astype(int)
)


if actual_ranks == expected_ranks:

    add_result(
        "Seller ranking",
        "PASSED",
        "Seller ranking is continuous and unique."
    )

else:

    add_result(
        "Seller ranking",
        "FAILED",
        "Seller ranking contains gaps or duplicates."
    )


# ============================================================
# Step 19: Profit Margin Validation
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


if incorrect_margin > 0:

    add_result(
        "Profit margin calculation",
        "FAILED",
        f"{incorrect_margin} incorrect profit margins found."
    )

else:

    add_result(
        "Profit margin calculation",
        "PASSED",
        "Profit margins match calculated values."
    )


# ============================================================
# Step 20: Summary Count Validation
# ============================================================

risk_total = (
    risk_summary["seller_count"]
    .sum()
)


action_total = (
    action_summary["seller_count"]
    .sum()
)


if risk_total == len(final_data):

    add_result(
        "Risk summary count",
        "PASSED",
        "Risk summary matches final dataset."
    )

else:

    add_result(
        "Risk summary count",
        "FAILED",
        f"Risk summary count={risk_total}, "
        f"dataset count={len(final_data)}."
    )


if action_total == len(final_data):

    add_result(
        "Action summary count",
        "PASSED",
        "Action summary matches final dataset."
    )

else:

    add_result(
        "Action summary count",
        "FAILED",
        f"Action summary count={action_total}, "
        f"dataset count={len(final_data)}."
    )


# ============================================================
# Step 21: Create Validation DataFrame
# ============================================================

validation_data = pd.DataFrame(
    validation_results
)


# ============================================================
# Step 22: Overall Validation Status
# ============================================================

failed_checks = (
    validation_data["status"]
    .eq("FAILED")
    .sum()
)


passed_checks = (
    validation_data["status"]
    .eq("PASSED")
    .sum()
)


if failed_checks == 0:

    overall_status = "PASSED"

else:

    overall_status = "FAILED"


# ============================================================
# Step 23: Display Validation Results
# ============================================================

print("\n============================================================")
print("Validation Results")
print("============================================================")


print(
    validation_data.to_string(
        index=False
    )
)


print("\n============================================================")
print("Validation Summary")
print("============================================================")


print(
    f"Passed checks : {passed_checks}"
)

print(
    f"Failed checks : {failed_checks}"
)

print(
    f"Overall status: {overall_status}"
)


# ============================================================
# Step 24: Save Validation Report
# ============================================================

validation_path = (
    final_directory
    / "seller_dashboard_validation_report.csv"
)


validation_data.to_csv(
    validation_path,
    index=False
)


print("\nValidation report saved to:")
print(validation_path)


# ============================================================
# Step 25: Save Validation Summary
# ============================================================

summary_path = (
    final_directory
    / "seller_dashboard_validation_summary.txt"
)


with open(
    summary_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "Seller Risk Dashboard Validation Summary\n"
    )

    file.write(
        "========================================\n\n"
    )

    file.write(
        f"Passed checks : {passed_checks}\n"
    )

    file.write(
        f"Failed checks : {failed_checks}\n"
    )

    file.write(
        f"Overall status: {overall_status}\n"
    )


print("\nValidation summary saved to:")
print(summary_path)


# ============================================================
# Step 26: Final Status
# ============================================================

print("\n============================================================")

if overall_status == "PASSED":

    print(
        "Step 94 validation completed successfully."
    )

else:

    print(
        "Step 94 validation completed with errors."
    )

print("============================================================")