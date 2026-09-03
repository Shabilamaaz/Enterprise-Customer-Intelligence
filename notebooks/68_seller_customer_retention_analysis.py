import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 68: Seller Customer Retention Analysis
# ============================================================

print("\n============================================================")
print("Step 68: Seller Customer Retention Analysis")
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

available_tables = set(
    tables["name"].tolist()
)


required_tables = {
    "orders",
    "order_items"
}


missing_tables = (
    required_tables - available_tables
)


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
# Step 4: Load Customer-Seller Purchase Data
# ============================================================

query = """
SELECT

    oi.seller_id,

    o.customer_id,

    COUNT(DISTINCT oi.order_id)
        AS customer_orders,

    SUM(oi.price)
        AS customer_revenue,

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


customer_seller_data = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# Step 5: Check Data
# ============================================================

print(
    f"\nCustomer-Seller records analyzed: "
    f"{len(customer_seller_data)}"
)


if customer_seller_data.empty:

    connection.close()

    raise RuntimeError(
        "\nERROR: No customer-seller data "
        "was returned."
    )


# ============================================================
# Step 6: Identify Repeat Customers
# ============================================================

customer_seller_data["is_repeat_customer"] = (
    customer_seller_data["customer_orders"] > 1
).astype(int)


# ============================================================
# Step 7: Aggregate Seller Retention Metrics
# ============================================================

seller_retention = (
    customer_seller_data
    .groupby(
        "seller_id",
        as_index=False
    )
    .agg(
        unique_customers=(
            "customer_id",
            "nunique"
        ),

        repeat_customers=(
            "is_repeat_customer",
            "sum"
        ),

        total_customer_orders=(
            "customer_orders",
            "sum"
        ),

        total_customer_revenue=(
            "customer_revenue",
            "sum"
        )
    )
)


# ============================================================
# Step 8: Calculate Repeat Customer Rate
# ============================================================

seller_retention["repeat_customer_rate"] = (

    seller_retention["repeat_customers"]
    /
    seller_retention["unique_customers"]

) * 100


seller_retention["repeat_customer_rate"] = (
    seller_retention["repeat_customer_rate"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 9: Calculate Average Orders per Customer
# ============================================================

seller_retention["orders_per_customer"] = (

    seller_retention["total_customer_orders"]
    /
    seller_retention["unique_customers"]

)


seller_retention["orders_per_customer"] = (
    seller_retention["orders_per_customer"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 10: Calculate Revenue per Customer
# ============================================================

seller_retention["revenue_per_customer"] = (

    seller_retention["total_customer_revenue"]
    /
    seller_retention["unique_customers"]

)


seller_retention["revenue_per_customer"] = (
    seller_retention["revenue_per_customer"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 11: Retention Classification
# ============================================================

def classify_retention(rate):

    if rate >= 50:
        return "Excellent Retention"

    elif rate >= 30:
        return "Strong Retention"

    elif rate >= 15:
        return "Moderate Retention"

    elif rate > 0:
        return "Low Retention"

    else:
        return "No Repeat Customers"


seller_retention["retention_category"] = (
    seller_retention["repeat_customer_rate"]
    .apply(classify_retention)
)


# ============================================================
# Step 12: Sort Sellers by Retention
# ============================================================

top_retention_sellers = (
    seller_retention
    .sort_values(
        by="repeat_customer_rate",
        ascending=False
    )
    .head(10)
)


# ============================================================
# Step 13: Display Seller Retention Analysis
# ============================================================

result_columns = [

    "seller_id",
    "unique_customers",
    "repeat_customers",
    "total_customer_orders",
    "total_customer_revenue",
    "repeat_customer_rate",
    "orders_per_customer",
    "revenue_per_customer",
    "retention_category"

]


print("\n============================================================")
print("Seller Customer Retention Analysis")
print("============================================================")


print(
    seller_retention[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 14: Top 10 Sellers by Retention
# ============================================================

print("\n============================================================")
print("Top 10 Sellers by Customer Retention")
print("============================================================")


print(
    top_retention_sellers[
        result_columns
    ]
    .to_string(index=False)
)


# ============================================================
# Step 15: Retention Category Summary
# ============================================================

print("\n============================================================")
print("Retention Category Summary")
print("============================================================")


print(
    seller_retention[
        "retention_category"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 16: Overall Retention Statistics
# ============================================================

average_retention = (
    seller_retention[
        "repeat_customer_rate"
    ].mean()
)


highest_retention = (
    seller_retention[
        "repeat_customer_rate"
    ].max()
)


lowest_retention = (
    seller_retention[
        "repeat_customer_rate"
    ].min()
)


total_unique_customers = (
    seller_retention[
        "unique_customers"
    ].sum()
)


total_repeat_customers = (
    seller_retention[
        "repeat_customers"
    ].sum()
)


print("\n============================================================")
print("Retention Statistics")
print("============================================================")


print(
    f"Average Repeat Customer Rate : "
    f"{average_retention:.2f}%"
)


print(
    f"Highest Repeat Customer Rate : "
    f"{highest_retention:.2f}%"
)


print(
    f"Lowest Repeat Customer Rate  : "
    f"{lowest_retention:.2f}%"
)


print(
    f"Total Customer Records       : "
    f"{int(total_unique_customers)}"
)


print(
    f"Total Repeat Customer Records: "
    f"{int(total_repeat_customers)}"
)


# ============================================================
# Step 17: Best Retention Seller
# ============================================================

best_retention_seller = (
    seller_retention.loc[
        seller_retention[
            "repeat_customer_rate"
        ].idxmax()
    ]
)


print("\n============================================================")
print("Best Seller by Customer Retention")
print("============================================================")


print(
    f"Seller ID           : "
    f"{best_retention_seller['seller_id']}"
)


print(
    f"Unique Customers    : "
    f"{int(best_retention_seller['unique_customers'])}"
)


print(
    f"Repeat Customers    : "
    f"{int(best_retention_seller['repeat_customers'])}"
)


print(
    f"Repeat Customer Rate: "
    f"{best_retention_seller['repeat_customer_rate']:.2f}%"
)


print(
    f"Orders per Customer : "
    f"{best_retention_seller['orders_per_customer']:.2f}"
)


print(
    f"Revenue per Customer: "
    f"{best_retention_seller['revenue_per_customer']:.2f}"
)


print(
    f"Category            : "
    f"{best_retention_seller['retention_category']}"
)


# ============================================================
# Step 18: Save Results
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_customer_retention.csv"
)


seller_retention[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nResults saved to:")
print(output_path)


# ============================================================
# Step 19: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 68 Seller Customer Retention Analysis "
    "completed successfully."
)
print("============================================================")