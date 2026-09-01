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
# Step 1: Find Database Automatically
# ============================================================

current_file = Path(__file__).resolve()

# Project root = parent folder of notebooks
project_root = current_file.parent.parent

expected_db = project_root / "data" / "database" / "olist.db"


# Search database if expected location does not exist
if expected_db.exists():

    db_path = expected_db

else:

    db_files = list(project_root.rglob("olist.db"))

    if not db_files:
        raise FileNotFoundError(
            "\nERROR: olist.db database file was not found.\n"
            f"Project folder searched: {project_root}\n"
            "Please make sure olist.db exists inside the project."
        )

    db_path = db_files[0]


print("\nDatabase found at:")
print(db_path)


# ============================================================
# Step 2: Connect to Database
# ============================================================

connection = sqlite3.connect(str(db_path))

print("\nDatabase connection successful.")


# ============================================================
# Step 3: Check Available Tables
# ============================================================

tables_query = """
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name
"""

tables_df = pd.read_sql_query(
    tables_query,
    connection
)

available_tables = tables_df["name"].tolist()

print("\nAvailable tables in database:")

for table in available_tables:
    print(" -", table)


# ============================================================
# Step 4: Detect Orders Table
# ============================================================

orders_candidates = [
    "orders",
    "olist_orders_dataset"
]

orders_table = None

for table in orders_candidates:

    if table in available_tables:
        orders_table = table
        break


if orders_table is None:

    connection.close()

    raise RuntimeError(
        "\nERROR: Orders table was not found.\n"
        "Expected one of:\n"
        " - orders\n"
        " - olist_orders_dataset"
    )


# ============================================================
# Step 5: Detect Order Items Table
# ============================================================

order_items_candidates = [
    "order_items",
    "olist_order_items_dataset"
]

order_items_table = None

for table in order_items_candidates:

    if table in available_tables:
        order_items_table = table
        break


if order_items_table is None:

    connection.close()

    raise RuntimeError(
        "\nERROR: Order items table was not found.\n"
        "Expected one of:\n"
        " - order_items\n"
        " - olist_order_items_dataset"
    )


print("\nOrders table detected:")
print(orders_table)

print("\nOrder Items table detected:")
print(order_items_table)


# ============================================================
# Step 6: Load Seller Revenue and Cost Data
# ============================================================

query = f"""
SELECT
    oi.seller_id,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    SUM(oi.price) AS total_revenue,

    SUM(oi.freight_value) AS total_freight_cost,

    AVG(oi.price) AS average_order_value

FROM "{order_items_table}" oi

JOIN "{orders_table}" o
    ON oi.order_id = o.order_id

WHERE o.order_status NOT IN (
    'canceled',
    'unavailable'
)

GROUP BY oi.seller_id
"""


seller_data = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# Step 7: Check Seller Data
# ============================================================

print("\nTotal sellers analyzed:")
print(len(seller_data))


if seller_data.empty:

    connection.close()

    raise RuntimeError(
        "\nERROR: No seller data was returned from the database."
    )


# ============================================================
# Step 8: Calculate Total Cost
# ============================================================

seller_data["total_cost"] = (
    seller_data["total_freight_cost"]
)


# ============================================================
# Step 9: Calculate Profit
# ============================================================

seller_data["profit"] = (
    seller_data["total_revenue"]
    - seller_data["total_cost"]
)


# ============================================================
# Step 10: Calculate ROI
# ============================================================

seller_data["roi_percentage"] = seller_data.apply(
    lambda row:
        (
            row["profit"]
            / row["total_cost"]
        ) * 100
        if row["total_cost"] > 0
        else 0,
    axis=1
)


# ============================================================
# Step 11: Categorize ROI
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
# Step 12: Sort Sellers by ROI
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
# Step 13: Define Result Columns
# ============================================================

result_columns = [
    "seller_id",
    "total_orders",
    "total_revenue",
    "total_cost",
    "profit",
    "roi_percentage",
    "roi_category"
]


# ============================================================
# Step 14: Display Seller ROI Analysis
# ============================================================

print("\n============================================================")
print("Seller Revenue ROI Analysis")
print("============================================================")

print(
    seller_data[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 15: Top 10 Sellers by ROI
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
# Step 16: ROI Category Summary
# ============================================================

print("\n============================================================")
print("ROI Category Summary")
print("============================================================")

print(
    seller_data[
        "roi_category"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 17: ROI Statistics
# ============================================================

highest_roi = seller_data[
    "roi_percentage"
].max()

average_roi = seller_data[
    "roi_percentage"
].mean()

lowest_roi = seller_data[
    "roi_percentage"
].min()


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
# Step 18: Best Seller by ROI
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
# Step 19: Close Database Connection
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 63 Seller Revenue ROI Analysis "
    "completed successfully."
)
print("============================================================")