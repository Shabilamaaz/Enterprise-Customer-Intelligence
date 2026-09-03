import pandas as pd
from pathlib import Path


# ============================================================
# Step 93: Seller Risk & Action Dashboard Final Dataset
# ============================================================

print("\n============================================================")
print("Step 93: Seller Risk & Action Dashboard Final Dataset")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Locate Step 91 Dashboard Data
# ============================================================

dashboard_directory = (
    project_root
    / "data"
    / "seller_risk_action_dashboard"
)


combined_path = (
    dashboard_directory
    / "seller_risk_action_dashboard_data.csv"
)

if not combined_path.exists():
    raise FileNotFoundError(
        "\nERROR: Step 91 dashboard data was not found.\n"
        f"Expected location:\n{combined_path}"
    )


# ============================================================
# Step 3: Load Dashboard Data
# ============================================================

seller_data = pd.read_csv(
    combined_path
)


print(
    f"\nSeller records loaded: "
    f"{len(seller_data)}"
)


if seller_data.empty:
    raise RuntimeError(
        "\nERROR: Dashboard dataset is empty."
    )


# ============================================================
# Step 4: Validate Required Columns
# ============================================================

required_columns = [
    "seller_id",
    "total_orders",
    "total_revenue",
    "profit",
    "risk_score",
    "priority_score",
    "risk_category",
    "action_priority"
]


missing_columns = [
    column
    for column in required_columns
    if column not in seller_data.columns
]


if missing_columns:
    raise ValueError(
        "\nERROR: Required columns are missing:\n"
        + ", ".join(missing_columns)
    )


# ============================================================
# Step 5: Remove Duplicate Sellers
# ============================================================

before_count = len(seller_data)


seller_data = (
    seller_data
    .drop_duplicates(
        subset=["seller_id"]
    )
    .reset_index(drop=True)
)


after_count = len(seller_data)


print(
    f"\nDuplicate seller records removed: "
    f"{before_count - after_count}"
)


# ============================================================
# Step 6: Clean Numeric Columns
# ============================================================

numeric_columns = [
    "total_orders",
    "total_revenue",
    "profit",
    "risk_score",
    "priority_score"
]


for column in numeric_columns:

    seller_data[column] = pd.to_numeric(
        seller_data[column],
        errors="coerce"
    )


seller_data[numeric_columns] = (
    seller_data[numeric_columns]
    .fillna(0)
)


# ============================================================
# Step 7: Recalculate Profit Margin
# ============================================================

if "profit_margin" not in seller_data.columns:

    seller_data["profit_margin"] = (
        seller_data["profit"]
        /
        seller_data["total_revenue"]
    ) * 100


seller_data["profit_margin"] = (
    seller_data["profit_margin"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 8: Create Final Risk Flag
# ============================================================

def create_risk_flag(category):

    if category == "Critical Risk":
        return "RED"

    elif category == "High Risk":
        return "ORANGE"

    elif category == "Medium Risk":
        return "YELLOW"

    elif category == "Low Risk":
        return "BLUE"

    else:
        return "GREEN"


seller_data["risk_flag"] = (
    seller_data["risk_category"]
    .apply(create_risk_flag)
)


# ============================================================
# Step 9: Create Management Action
# ============================================================

def create_management_action(row):

    if row["action_priority"] == "Immediate":

        return (
            "Immediate management review required"
        )

    elif row["action_priority"] == "High":

        return (
            "High-priority performance improvement"
        )

    elif row["action_priority"] == "Medium":

        return (
            "Monitor and improve seller performance"
        )

    elif row["action_priority"] == "Low":

        return (
            "Routine monitoring"
        )

    else:

        return (
            "Maintain current performance"
        )


seller_data["management_action"] = (
    seller_data
    .apply(
        create_management_action,
        axis=1
    )
)


# ============================================================
# Step 10: Create Seller Rank
# ============================================================

seller_data = (
    seller_data
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
    .reset_index(drop=True)
)


seller_data["seller_rank"] = (
    seller_data.index + 1
)


# ============================================================
# Step 11: Round Metrics
# ============================================================

seller_data[
    [
        "total_revenue",
        "profit",
        "profit_margin",
        "risk_score",
        "priority_score"
    ]
] = (
    seller_data[
        [
            "total_revenue",
            "profit",
            "profit_margin",
            "risk_score",
            "priority_score"
        ]
    ]
    .round(2)
)


# ============================================================
# Step 12: Select Final Columns
# ============================================================

final_columns = [
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


final_data = seller_data[
    final_columns
].copy()


# ============================================================
# Step 13: Display Final Dataset
# ============================================================

print("\n============================================================")
print("Final Seller Risk & Action Dataset")
print("============================================================")


print(
    final_data
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 14: Final Dataset Statistics
# ============================================================

print("\n============================================================")
print("Final Dataset Statistics")
print("============================================================")


print(
    f"Total sellers : "
    f"{len(final_data)}"
)

print(
    f"Total revenue: "
    f"{final_data['total_revenue'].sum():.2f}"
)

print(
    f"Total profit : "
    f"{final_data['profit'].sum():.2f}"
)

print(
    f"Average risk : "
    f"{final_data['risk_score'].mean():.2f}"
)

print(
    f"Average priority: "
    f"{final_data['priority_score'].mean():.2f}"
)


# ============================================================
# Step 15: Risk Distribution
# ============================================================

print("\n============================================================")
print("Final Risk Distribution")
print("============================================================")


print(
    final_data["risk_category"]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 16: Action Distribution
# ============================================================

print("\n============================================================")
print("Final Action Distribution")
print("============================================================")


print(
    final_data["action_priority"]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 17: Create Final Output Directory
# ============================================================

final_directory = (
    project_root
    / "data"
    / "final_seller_dashboard"
)


final_directory.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Step 18: Save Final CSV
# ============================================================

final_csv_path = (
    final_directory
    / "seller_risk_action_final_dataset.csv"
)


final_data.to_csv(
    final_csv_path,
    index=False
)


print("\nFinal CSV saved to:")
print(final_csv_path)


# ============================================================
# Step 19: Save Excel Dataset
# ============================================================

final_excel_path = (
    final_directory
    / "seller_risk_action_final_dataset.xlsx"
)


final_data.to_excel(
    final_excel_path,
    index=False
)


print("\nFinal Excel dataset saved to:")
print(final_excel_path)


# ============================================================
# Step 20: Save Risk Summary
# ============================================================

risk_summary = (
    final_data
    .groupby(
        [
            "risk_category",
            "risk_flag"
        ]
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


risk_summary_path = (
    final_directory
    / "final_risk_summary.csv"
)


risk_summary.to_csv(
    risk_summary_path,
    index=False
)


print("\nFinal risk summary saved to:")
print(risk_summary_path)


# ============================================================
# Step 21: Save Action Summary
# ============================================================

action_summary = (
    final_data
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
        average_priority_score=(
            "priority_score",
            "mean"
        )
    )
    .reset_index()
)


action_summary_path = (
    final_directory
    / "final_action_summary.csv"
)


action_summary.to_csv(
    action_summary_path,
    index=False
)


print("\nFinal action summary saved to:")
print(action_summary_path)


# ============================================================
# Step 22: Completion
# ============================================================

print("\n============================================================")
print(
    "Step 93 Seller Risk & Action Dashboard Final Dataset "
    "completed successfully."
)
print("============================================================")