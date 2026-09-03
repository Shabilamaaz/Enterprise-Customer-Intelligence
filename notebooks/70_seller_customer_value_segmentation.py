import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 70: Seller Customer Value Segmentation Analysis
# ============================================================

print("\n============================================================")
print("Step 70: Seller Customer Value Segmentation Analysis")
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
        f"Expected location:\n{db_path}\n\n"
        "Please run 04_create_database.py first."
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

    MIN(o.order_purchase_timestamp)
        AS first_purchase,

    MAX(o.order_purchase_timestamp)
        AS last_purchase

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
# Step 5: Check Data
# ============================================================

print(
    f"\nCustomer-Seller records analyzed: "
    f"{len(customer_data)}"
)

if customer_data.empty:
    connection.close()

    raise RuntimeError(
        "\nERROR: No customer data was returned."
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
# Step 7: Calculate Customer Frequency
# ============================================================

customer_data["customer_frequency"] = (
    customer_data["total_orders"]
)


# ============================================================
# Step 8: Customer Value Score
# ============================================================

customer_data["revenue_score"] = (
    customer_data["total_revenue"]
    /
    customer_data["total_revenue"].max()
) * 100


customer_data["frequency_score"] = (
    customer_data["customer_frequency"]
    /
    customer_data["customer_frequency"].max()
) * 100


customer_data["order_value_score"] = (
    customer_data["average_order_value"]
    /
    customer_data["average_order_value"].max()
) * 100


customer_data["customer_value_score"] = (
    customer_data["revenue_score"] * 0.50
    +
    customer_data["frequency_score"] * 0.30
    +
    customer_data["order_value_score"] * 0.20
)


customer_data["customer_value_score"] = (
    customer_data["customer_value_score"]
    .clip(lower=0, upper=100)
    .round(2)
)


# ============================================================
# Step 9: Segment Customers
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
    customer_data["customer_value_score"]
    .apply(classify_customer)
)


# ============================================================
# Step 10: Rank Customer-Seller Relationships
# ============================================================

customer_data = (
    customer_data
    .sort_values(
        by="customer_value_score",
        ascending=False
    )
    .reset_index(drop=True)
)


customer_data["value_rank"] = (
    customer_data.index + 1
)


# ============================================================
# Step 11: Display Customer Segmentation
# ============================================================

result_columns = [
    "value_rank",
    "seller_id",
    "customer_id",
    "total_orders",
    "total_revenue",
    "average_order_value",
    "customer_value_score",
    "customer_segment"
]


print("\n============================================================")
print("Customer Value Segmentation")
print("============================================================")


print(
    customer_data[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 12: Segment Summary
# ============================================================

print("\n============================================================")
print("Customer Segment Summary")
print("============================================================")


segment_summary = (
    customer_data["customer_segment"]
    .value_counts()
)


print(
    segment_summary.to_string()
)


# ============================================================
# Step 13: Segment Percentages
# ============================================================

segment_percentage = (
    customer_data["customer_segment"]
    .value_counts(normalize=True)
    * 100
)


print("\n============================================================")
print("Customer Segment Percentage")
print("============================================================")


for segment, percentage in segment_percentage.items():

    print(
        f"{segment}: {percentage:.2f}%"
    )


# ============================================================
# Step 14: Segment Revenue Analysis
# ============================================================

segment_revenue = (
    customer_data
    .groupby("customer_segment")
    .agg(
        customers=(
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
        average_value_score=(
            "customer_value_score",
            "mean"
        )
    )
    .sort_values(
        by="total_revenue",
        ascending=False
    )
)


print("\n============================================================")
print("Revenue by Customer Segment")
print("============================================================")


print(
    segment_revenue
    .round(2)
    .to_string()
)


# ============================================================
# Step 15: Highest Value Customers
# ============================================================

top_customers = (
    customer_data
    .head(10)
)


print("\n============================================================")
print("Top 10 Highest Value Customer Relationships")
print("============================================================")


print(
    top_customers[
        result_columns
    ]
    .to_string(index=False)
)


# ============================================================
# Step 16: Overall Statistics
# ============================================================

total_customers = len(customer_data)

average_value_score = (
    customer_data["customer_value_score"]
    .mean()
)

highest_value_score = (
    customer_data["customer_value_score"]
    .max()
)

average_customer_revenue = (
    customer_data["total_revenue"]
    .mean()
)


print("\n============================================================")
print("Customer Value Statistics")
print("============================================================")


print(
    f"Total Customer-Seller Records : "
    f"{total_customers}"
)

print(
    f"Average Value Score           : "
    f"{average_value_score:.2f}"
)

print(
    f"Highest Value Score           : "
    f"{highest_value_score:.2f}"
)

print(
    f"Average Customer Revenue      : "
    f"{average_customer_revenue:.2f}"
)


# ============================================================
# Step 17: Top Customer Relationship
# ============================================================

top_customer = customer_data.iloc[0]


print("\n============================================================")
print("Highest Value Customer Relationship")
print("============================================================")


print(
    f"Seller ID          : "
    f"{top_customer['seller_id']}"
)

print(
    f"Customer ID        : "
    f"{top_customer['customer_id']}"
)

print(
    f"Total Orders       : "
    f"{int(top_customer['total_orders'])}"
)

print(
    f"Total Revenue      : "
    f"{top_customer['total_revenue']:.2f}"
)

print(
    f"Average Order Value: "
    f"{top_customer['average_order_value']:.2f}"
)

print(
    f"Value Score        : "
    f"{top_customer['customer_value_score']:.2f}"
)

print(
    f"Customer Segment   : "
    f"{top_customer['customer_segment']}"
)


# ============================================================
# Step 18: Save Customer Segmentation
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_customer_value_segmentation.csv"
)


customer_data[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nSegmentation results saved to:")
print(output_path)


# ============================================================
# Step 19: Save Segment Summary
# ============================================================

summary_path = (
    project_root
    / "data"
    / "customer_segment_summary.csv"
)


segment_revenue.round(2).to_csv(
    summary_path
)


print("\nSegment summary saved to:")
print(summary_path)


# ============================================================
# Step 20: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 70 Seller Customer Value Segmentation "
    "completed successfully."
)
print("============================================================")