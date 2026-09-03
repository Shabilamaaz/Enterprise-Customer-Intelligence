import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 67: Seller Customer Concentration Analysis
# ============================================================

print("\n============================================================")
print("Step 67: Seller Customer Concentration Analysis")
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
# Step 4: Load Seller Customer Data
# ============================================================

query = """
SELECT

    oi.seller_id,

    COUNT(DISTINCT o.customer_id)
        AS unique_customers,

    COUNT(DISTINCT oi.order_id)
        AS total_orders,

    COUNT(*) AS total_items_sold,

    SUM(oi.price)
        AS total_revenue

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

WHERE o.order_status
NOT IN ('canceled', 'unavailable')

GROUP BY oi.seller_id
"""


seller_customers = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# Step 5: Check Data
# ============================================================

print(
    f"\nTotal sellers analyzed: "
    f"{len(seller_customers)}"
)


if seller_customers.empty:

    connection.close()

    raise RuntimeError(
        "\nERROR: No seller customer data "
        "was returned."
    )


# ============================================================
# Step 6: Calculate Orders per Customer
# ============================================================

seller_customers["orders_per_customer"] = (
    seller_customers["total_orders"]
    /
    seller_customers["unique_customers"]
)


seller_customers["orders_per_customer"] = (
    seller_customers["orders_per_customer"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 7: Calculate Revenue per Customer
# ============================================================

seller_customers["revenue_per_customer"] = (
    seller_customers["total_revenue"]
    /
    seller_customers["unique_customers"]
)


seller_customers["revenue_per_customer"] = (
    seller_customers["revenue_per_customer"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 8: Calculate Customer Concentration
# ============================================================

seller_customers["customer_concentration"] = (

    seller_customers["unique_customers"]
    /
    seller_customers["total_orders"]

) * 100


seller_customers["customer_concentration"] = (
    seller_customers["customer_concentration"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 9: Customer Dependency Category
# ============================================================

def classify_customer_dependency(
    concentration
):

    if concentration >= 80:
        return "Low Customer Dependency"

    elif concentration >= 60:
        return "Moderate Customer Dependency"

    elif concentration >= 40:
        return "High Customer Dependency"

    else:
        return "Very High Customer Dependency"


seller_customers["customer_dependency"] = (
    seller_customers[
        "customer_concentration"
    ]
    .apply(classify_customer_dependency)
)


# ============================================================
# Step 10: Sort Sellers
# ============================================================

top_customer_base = (
    seller_customers
    .sort_values(
        by="unique_customers",
        ascending=False
    )
    .head(10)
)


top_revenue_per_customer = (
    seller_customers
    .sort_values(
        by="revenue_per_customer",
        ascending=False
    )
    .head(10)
)


# ============================================================
# Step 11: Display Analysis
# ============================================================

result_columns = [

    "seller_id",
    "unique_customers",
    "total_orders",
    "total_items_sold",
    "total_revenue",
    "orders_per_customer",
    "revenue_per_customer",
    "customer_concentration",
    "customer_dependency"

]


print("\n============================================================")
print("Seller Customer Concentration Analysis")
print("============================================================")


print(
    seller_customers[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 12: Top Sellers by Customer Base
# ============================================================

print("\n============================================================")
print("Top 10 Sellers by Customer Base")
print("============================================================")


print(
    top_customer_base[
        result_columns
    ]
    .to_string(index=False)
)


# ============================================================
# Step 13: Top Sellers by Revenue per Customer
# ============================================================

print("\n============================================================")
print("Top 10 Sellers by Revenue per Customer")
print("============================================================")


print(
    top_revenue_per_customer[
        [
            "seller_id",
            "unique_customers",
            "total_revenue",
            "revenue_per_customer",
            "customer_dependency"
        ]
    ]
    .to_string(index=False)
)


# ============================================================
# Step 14: Customer Dependency Summary
# ============================================================

print("\n============================================================")
print("Customer Dependency Summary")
print("============================================================")


print(
    seller_customers[
        "customer_dependency"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 15: Overall Statistics
# ============================================================

average_customers = (
    seller_customers[
        "unique_customers"
    ].mean()
)


average_revenue_per_customer = (
    seller_customers[
        "revenue_per_customer"
    ].mean()
)


average_orders_per_customer = (
    seller_customers[
        "orders_per_customer"
    ].mean()
)


print("\n============================================================")
print("Customer Concentration Statistics")
print("============================================================")


print(
    f"Average Customers per Seller : "
    f"{average_customers:.2f}"
)


print(
    f"Average Orders per Customer  : "
    f"{average_orders_per_customer:.2f}"
)


print(
    f"Average Revenue per Customer : "
    f"{average_revenue_per_customer:.2f}"
)


# ============================================================
# Step 16: Largest Customer Base
# ============================================================

largest_customer_base = (
    seller_customers.loc[
        seller_customers[
            "unique_customers"
        ].idxmax()
    ]
)


print("\n============================================================")
print("Seller with Largest Customer Base")
print("============================================================")


print(
    f"Seller ID        : "
    f"{largest_customer_base['seller_id']}"
)


print(
    f"Unique Customers : "
    f"{int(largest_customer_base['unique_customers'])}"
)


print(
    f"Total Orders     : "
    f"{int(largest_customer_base['total_orders'])}"
)


print(
    f"Total Revenue    : "
    f"{largest_customer_base['total_revenue']:.2f}"
)


# ============================================================
# Step 17: Highest Revenue per Customer
# ============================================================

highest_value_seller = (
    seller_customers.loc[
        seller_customers[
            "revenue_per_customer"
        ].idxmax()
    ]
)


print("\n============================================================")
print("Seller with Highest Revenue per Customer")
print("============================================================")


print(
    f"Seller ID           : "
    f"{highest_value_seller['seller_id']}"
)


print(
    f"Unique Customers    : "
    f"{int(highest_value_seller['unique_customers'])}"
)


print(
    f"Total Revenue       : "
    f"{highest_value_seller['total_revenue']:.2f}"
)


print(
    f"Revenue per Customer: "
    f"{highest_value_seller['revenue_per_customer']:.2f}"
)


# ============================================================
# Step 18: Save Results
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_customer_concentration.csv"
)


seller_customers[
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
    "Step 67 Seller Customer Concentration Analysis "
    "completed successfully."
)
print("============================================================")