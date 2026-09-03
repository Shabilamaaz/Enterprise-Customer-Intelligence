import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 71: Seller Customer Segmentation Summary
# ============================================================

print("\n============================================================")
print("Step 71: Seller Customer Segmentation Summary")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Connect to Correct Database
# ============================================================

db_path = (
    project_root
    / "database"
    / "customer_intelligence.db"
)

print("\nDatabase path:")
print(db_path)


if not db_path.exists():
    raise FileNotFoundError(
        "\nERROR: customer_intelligence.db was not found.\n"
        f"Expected location:\n{db_path}"
    )


connection = sqlite3.connect(str(db_path))

print("\nDatabase connection successful.")


# ============================================================
# Step 3: Check Required Tables
# ============================================================

tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
    """,
    connection
)

available_tables = set(tables["name"].tolist())

required_tables = {
    "orders",
    "order_items"
}

missing_tables = required_tables - available_tables

if missing_tables:
    connection.close()

    raise RuntimeError(
        "\nERROR: Required table(s) not found:\n"
        + "\n".join(
            f"- {table}"
            for table in sorted(missing_tables)
        )
    )


print("\nRequired tables found:")
print("- orders")
print("- order_items")


# ============================================================
# Step 4: Load Customer-Seller Data
# ============================================================

query = """
SELECT

    oi.seller_id,

    o.customer_id,

    COUNT(DISTINCT oi.order_id)
        AS total_orders,

    SUM(oi.price)
        AS total_revenue,

    AVG(oi.price)
        AS average_order_value

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

WHERE o.order_status
NOT IN ('canceled', 'unavailable')

GROUP BY
    oi.seller_id,
    o.customer_id
"""


customer_data = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# Step 5: Validate Data
# ============================================================

print(
    f"\nCustomer-Seller records analyzed: "
    f"{len(customer_data)}"
)


if customer_data.empty:
    connection.close()

    raise RuntimeError(
        "\nERROR: No customer-seller data was returned."
    )


# ============================================================
# Step 6: Calculate Customer Metrics
# ============================================================

customer_data["average_order_value"] = (
    customer_data["total_revenue"]
    /
    customer_data["total_orders"]
)


customer_data["average_order_value"] = (
    customer_data["average_order_value"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 7: Calculate Normalized Scores
# ============================================================

customer_data["revenue_score"] = (
    customer_data["total_revenue"]
    /
    customer_data["total_revenue"].max()
) * 100


customer_data["frequency_score"] = (
    customer_data["total_orders"]
    /
    customer_data["total_orders"].max()
) * 100


customer_data["order_value_score"] = (
    customer_data["average_order_value"]
    /
    customer_data["average_order_value"].max()
) * 100


# ============================================================
# Step 8: Calculate Overall Customer Score
# ============================================================

customer_data["customer_score"] = (
    customer_data["revenue_score"] * 0.50
    +
    customer_data["frequency_score"] * 0.30
    +
    customer_data["order_value_score"] * 0.20
)


customer_data["customer_score"] = (
    customer_data["customer_score"]
    .clip(lower=0, upper=100)
    .round(2)
)


# ============================================================
# Step 9: Create Customer Segments
# ============================================================

def classify_customer(score):

    if score >= 70:
        return "VIP Customer"

    elif score >= 40:
        return "High Value Customer"

    elif score >= 20:
        return "Medium Value Customer"

    else:
        return "Low Value Customer"


customer_data["customer_segment"] = (
    customer_data["customer_score"]
    .apply(classify_customer)
)


# ============================================================
# Step 10: Segment Summary
# ============================================================

segment_summary = (
    customer_data
    .groupby(
        "customer_segment"
    )
    .agg(
        customer_count=(
            "customer_id",
            "count"
        ),

        total_revenue=(
            "total_revenue",
            "sum"
        ),

        average_revenue=(
            "total_revenue",
            "mean"
        ),

        average_orders=(
            "total_orders",
            "mean"
        ),

        average_order_value=(
            "average_order_value",
            "mean"
        ),

        average_score=(
            "customer_score",
            "mean"
        )
    )
    .reset_index()
)


# ============================================================
# Step 11: Calculate Segment Percentage
# ============================================================

total_records = (
    segment_summary["customer_count"]
    .sum()
)


segment_summary["customer_percentage"] = (
    segment_summary["customer_count"]
    /
    total_records
) * 100


# ============================================================
# Step 12: Calculate Revenue Contribution
# ============================================================

total_revenue = (
    segment_summary["total_revenue"]
    .sum()
)


segment_summary["revenue_contribution"] = (
    segment_summary["total_revenue"]
    /
    total_revenue
) * 100


# ============================================================
# Step 13: Round Values
# ============================================================

numeric_columns = [
    "total_revenue",
    "average_revenue",
    "average_orders",
    "average_order_value",
    "average_score",
    "customer_percentage",
    "revenue_contribution"
]


segment_summary[numeric_columns] = (
    segment_summary[numeric_columns]
    .round(2)
)


# ============================================================
# Step 14: Sort Segments
# ============================================================

segment_summary = (
    segment_summary
    .sort_values(
        by="total_revenue",
        ascending=False
    )
    .reset_index(drop=True)
)


# ============================================================
# Step 15: Display Segment Summary
# ============================================================

print("\n============================================================")
print("Customer Segment Summary")
print("============================================================")


print(
    segment_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 16: Segment Counts
# ============================================================

print("\n============================================================")
print("Customer Segment Counts")
print("============================================================")


for _, row in segment_summary.iterrows():

    print(
        f"{row['customer_segment']}: "
        f"{int(row['customer_count'])} customers "
        f"({row['customer_percentage']:.2f}%)"
    )


# ============================================================
# Step 17: Revenue Contribution
# ============================================================

print("\n============================================================")
print("Revenue Contribution by Segment")
print("============================================================")


for _, row in segment_summary.iterrows():

    print(
        f"{row['customer_segment']}: "
        f"{row['revenue_contribution']:.2f}%"
    )


# ============================================================
# Step 18: Highest Revenue Segment
# ============================================================

highest_revenue_segment = (
    segment_summary.loc[
        segment_summary[
            "total_revenue"
        ].idxmax()
    ]
)


print("\n============================================================")
print("Highest Revenue Customer Segment")
print("============================================================")


print(
    f"Segment              : "
    f"{highest_revenue_segment['customer_segment']}"
)

print(
    f"Customer Count       : "
    f"{int(highest_revenue_segment['customer_count'])}"
)

print(
    f"Total Revenue        : "
    f"{highest_revenue_segment['total_revenue']:.2f}"
)

print(
    f"Revenue Contribution : "
    f"{highest_revenue_segment['revenue_contribution']:.2f}%"
)


# ============================================================
# Step 19: Highest Value Segment
# ============================================================

highest_value_segment = (
    segment_summary.loc[
        segment_summary[
            "average_score"
        ].idxmax()
    ]
)


print("\n============================================================")
print("Highest Value Customer Segment")
print("============================================================")


print(
    f"Segment        : "
    f"{highest_value_segment['customer_segment']}"
)

print(
    f"Average Score  : "
    f"{highest_value_segment['average_score']:.2f}"
)

print(
    f"Average Revenue: "
    f"{highest_value_segment['average_revenue']:.2f}"
)


# ============================================================
# Step 20: Save Segment Summary
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_customer_segmentation_summary.csv"
)


segment_summary.to_csv(
    output_path,
    index=False
)


print("\nSegment summary saved to:")
print(output_path)


# ============================================================
# Step 21: Save Detailed Customer Segmentation
# ============================================================

detail_path = (
    project_root
    / "data"
    / "seller_customer_segmentation_detail.csv"
)


customer_data[
    [
        "seller_id",
        "customer_id",
        "total_orders",
        "total_revenue",
        "average_order_value",
        "customer_score",
        "customer_segment"
    ]
].to_csv(
    detail_path,
    index=False
)


print("\nDetailed segmentation saved to:")
print(detail_path)


# ============================================================
# Step 22: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 71 Seller Customer Segmentation Summary "
    "completed successfully."
)
print("============================================================")