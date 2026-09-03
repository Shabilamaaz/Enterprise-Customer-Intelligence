import sqlite3
import pandas as pd
from pathlib import Path

# ============================================================
# Step 63: Seller Revenue ROI Analysis
# ============================================================

print("\n============================================================")
print("Step 63: Seller Revenue ROI Analysis")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()

# notebooks folder ka parent = project root
project_root = current_file.parent.parent

# ============================================================
# Step 2: Connect to Correct Database
# ============================================================

db_path = project_root / "database" / "customer_intelligence.db"

print("\nDatabase path:")
print(db_path)


# Check database exists
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

print("\nAvailable tables in database:")
for table in sorted(available_tables):
    print(f"- {table}")


required_tables = {
    "orders",
    "order_items"
}

missing_tables = required_tables - available_tables


if missing_tables:
    connection.close()

    raise RuntimeError(
        "\nERROR: Required table(s) not found:\n"
        + "\n".join(f"- {table}" for table in sorted(missing_tables))
        + "\n\nPlease run 04_create_database.py first."
    )


# ============================================================
# Step 4: Load Seller Revenue and Cost Data
# ============================================================

query = """
SELECT
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.price) AS total_revenue,
    SUM(oi.freight_value) AS total_freight_cost,
    AVG(oi.price) AS average_order_value

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

WHERE o.order_status NOT IN ('canceled', 'unavailable')

GROUP BY oi.seller_id
"""


seller_data = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# Step 5: Check Data
# ============================================================

print(
    f"\nTotal sellers analyzed: {len(seller_data)}"
)


if seller_data.empty:
    connection.close()

    raise RuntimeError(
        "\nERROR: No seller data was returned from the database."
    )


# ============================================================
# Step 6: Calculate Total Cost
# ============================================================

seller_data["total_cost"] = (
    seller_data["total_freight_cost"]
)


# ============================================================
# Step 7: Calculate Profit
# ============================================================

seller_data["profit"] = (
    seller_data["total_revenue"]
    - seller_data["total_cost"]
)


# ============================================================
# Step 8: Calculate ROI
# ============================================================

seller_data["roi_percentage"] = seller_data.apply(
    lambda row:
        (
            row["profit"] / row["total_cost"]
        ) * 100
        if row["total_cost"] > 0
        else 0,
    axis=1
)


# ============================================================
# Step 9: Categorize ROI
# ============================================================

def classify_roi(roi):

    if roi >= 200:
        return "Excellent ROI"

    elif roi >= 100:
        return "High ROI"

    elif roi >= 50:
        return "Medium ROI"

    elif roi > 0:
        return "Low ROI"

    else:
        return "Negative ROI"


seller_data["roi_category"] = (
    seller_data["roi_percentage"]
    .apply(classify_roi)
)


# ============================================================
# Step 10: Sort Sellers by ROI
# ============================================================

top_sellers = (
    seller_data
    .sort_values(
        by="roi_percentage",
        ascending=False
    )
    .head(10)
)


# ============================================================
# Step 11: Display Seller ROI Analysis
# ============================================================

print("\n============================================================")
print("Seller Revenue ROI Analysis")
print("============================================================")


result_columns = [
    "seller_id",
    "total_orders",
    "total_revenue",
    "total_cost",
    "profit",
    "roi_percentage",
    "roi_category"
]


print(
    seller_data[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 12: Top 10 Sellers by ROI
# ============================================================

print("\n============================================================")
print("Top 10 Sellers by ROI")
print("============================================================")


print(
    top_sellers[
        result_columns
    ]
    .to_string(index=False)
)


# ============================================================
# Step 13: ROI Category Summary
# ============================================================

print("\n============================================================")
print("ROI Category Summary")
print("============================================================")


print(
    seller_data["roi_category"]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 14: ROI Statistics
# ============================================================

highest_roi = seller_data["roi_percentage"].max()

average_roi = seller_data["roi_percentage"].mean()

lowest_roi = seller_data["roi_percentage"].min()


print("\n============================================================")
print("ROI Statistics")
print("============================================================")


print(
    f"Highest ROI : {highest_roi:.2f}%"
)

print(
    f"Average ROI : {average_roi:.2f}%"
)

print(
    f"Lowest ROI  : {lowest_roi:.2f}%"
)


# ============================================================
# Step 15: Best Seller
# ============================================================

best_seller = seller_data.loc[
    seller_data["roi_percentage"].idxmax()
]


print("\n============================================================")
print("Best Seller by ROI")
print("============================================================")


print(
    f"Seller ID      : {best_seller['seller_id']}"
)

print(
    f"Total Orders   : {int(best_seller['total_orders'])}"
)

print(
    f"Total Revenue  : {best_seller['total_revenue']:.2f}"
)

print(
    f"Total Cost     : {best_seller['total_cost']:.2f}"
)

print(
    f"Profit         : {best_seller['profit']:.2f}"
)

print(
    f"ROI            : {best_seller['roi_percentage']:.2f}%"
)

print(
    f"ROI Category   : {best_seller['roi_category']}"
)


# ============================================================
# Step 16: Close Database Connection
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print("Step 63 Seller Revenue ROI Analysis completed successfully.")
print("============================================================")