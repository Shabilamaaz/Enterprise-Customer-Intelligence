import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 69: Seller Customer Value Analysis
# ============================================================

print("\n============================================================")
print("Step 69: Seller Customer Value Analysis")
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
# Step 4: Load Customer Value by Seller
# ============================================================

query = """
SELECT

    oi.seller_id,

    o.customer_id,

    COUNT(DISTINCT oi.order_id)
        AS customer_orders,

    SUM(oi.price)
        AS customer_revenue,

    AVG(oi.price)
        AS average_order_value,

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


customer_value = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# Step 5: Check Data
# ============================================================

print(
    f"\nCustomer-Seller records analyzed: "
    f"{len(customer_value)}"
)


if customer_value.empty:

    connection.close()

    raise RuntimeError(
        "\nERROR: No customer value data "
        "was returned."
    )


# ============================================================
# Step 6: Identify Customer Type
# ============================================================

customer_value["customer_type"] = (
    customer_value["customer_orders"]
    .apply(
        lambda x:
        "Repeat Customer"
        if x > 1
        else "One-Time Customer"
    )
)


# ============================================================
# Step 7: Calculate Seller Customer Metrics
# ============================================================

seller_value = (
    customer_value
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
            "customer_type",
            lambda x:
            (x == "Repeat Customer").sum()
        ),

        total_orders=(
            "customer_orders",
            "sum"
        ),

        total_revenue=(
            "customer_revenue",
            "sum"
        ),

        average_customer_value=(
            "customer_revenue",
            "mean"
        ),

        average_order_value=(
            "average_order_value",
            "mean"
        )
    )
)


# ============================================================
# Step 8: Calculate Repeat Customer Rate
# ============================================================

seller_value["repeat_customer_rate"] = (

    seller_value["repeat_customers"]
    /
    seller_value["unique_customers"]

) * 100


seller_value["repeat_customer_rate"] = (
    seller_value["repeat_customer_rate"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 9: Calculate Revenue per Customer
# ============================================================

seller_value["revenue_per_customer"] = (

    seller_value["total_revenue"]
    /
    seller_value["unique_customers"]

)


seller_value["revenue_per_customer"] = (
    seller_value["revenue_per_customer"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 10: Calculate Customer Value Score
# ============================================================

seller_value["revenue_score"] = (

    seller_value["revenue_per_customer"]
    /
    seller_value["revenue_per_customer"].max()

) * 100


seller_value["retention_score"] = (
    seller_value["repeat_customer_rate"]
)


seller_value["customer_value_score"] = (

    seller_value["revenue_score"] * 0.60

    +

    seller_value["retention_score"] * 0.40

)


seller_value["customer_value_score"] = (
    seller_value["customer_value_score"]
    .clip(upper=100)
    .round(2)
)


# ============================================================
# Step 11: Customer Value Classification
# ============================================================

def classify_customer_value(score):

    if score >= 70:
        return "High Customer Value"

    elif score >= 40:
        return "Medium Customer Value"

    elif score >= 20:
        return "Low Customer Value"

    else:
        return "Very Low Customer Value"


seller_value["customer_value_category"] = (
    seller_value["customer_value_score"]
    .apply(classify_customer_value)
)


# ============================================================
# Step 12: Rank Sellers
# ============================================================

seller_value = (
    seller_value
    .sort_values(
        by="customer_value_score",
        ascending=False
    )
    .reset_index(drop=True)
)


seller_value["customer_value_rank"] = (
    seller_value.index + 1
)


# ============================================================
# Step 13: Display Analysis
# ============================================================

result_columns = [

    "customer_value_rank",
    "seller_id",
    "unique_customers",
    "repeat_customers",
    "total_orders",
    "total_revenue",
    "average_customer_value",
    "revenue_per_customer",
    "repeat_customer_rate",
    "customer_value_score",
    "customer_value_category"

]


print("\n============================================================")
print("Seller Customer Value Analysis")
print("============================================================")


print(
    seller_value[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 14: Top 10 Sellers by Customer Value
# ============================================================

print("\n============================================================")
print("Top 10 Sellers by Customer Value")
print("============================================================")


print(
    seller_value[
        result_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# Step 15: Customer Value Category Summary
# ============================================================

print("\n============================================================")
print("Customer Value Category Summary")
print("============================================================")


print(
    seller_value[
        "customer_value_category"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 16: Overall Statistics
# ============================================================

average_customer_value = (
    seller_value[
        "average_customer_value"
    ].mean()
)


average_revenue_per_customer = (
    seller_value[
        "revenue_per_customer"
    ].mean()
)


average_customer_value_score = (
    seller_value[
        "customer_value_score"
    ].mean()
)


highest_customer_value_score = (
    seller_value[
        "customer_value_score"
    ].max()
)


print("\n============================================================")
print("Customer Value Statistics")
print("============================================================")


print(
    f"Average Customer Value       : "
    f"{average_customer_value:.2f}"
)


print(
    f"Average Revenue per Customer: "
    f"{average_revenue_per_customer:.2f}"
)


print(
    f"Average Customer Value Score : "
    f"{average_customer_value_score:.2f}"
)


print(
    f"Highest Customer Value Score : "
    f"{highest_customer_value_score:.2f}"
)


# ============================================================
# Step 17: Best Seller by Customer Value
# ============================================================

best_seller = seller_value.iloc[0]


print("\n============================================================")
print("Best Seller by Customer Value")
print("============================================================")


print(
    f"Rank                 : "
    f"{int(best_seller['customer_value_rank'])}"
)


print(
    f"Seller ID            : "
    f"{best_seller['seller_id']}"
)


print(
    f"Unique Customers     : "
    f"{int(best_seller['unique_customers'])}"
)


print(
    f"Repeat Customers     : "
    f"{int(best_seller['repeat_customers'])}"
)


print(
    f"Total Orders         : "
    f"{int(best_seller['total_orders'])}"
)


print(
    f"Total Revenue        : "
    f"{best_seller['total_revenue']:.2f}"
)


print(
    f"Revenue per Customer : "
    f"{best_seller['revenue_per_customer']:.2f}"
)


print(
    f"Repeat Customer Rate : "
    f"{best_seller['repeat_customer_rate']:.2f}%"
)


print(
    f"Customer Value Score : "
    f"{best_seller['customer_value_score']:.2f}"
)


print(
    f"Category             : "
    f"{best_seller['customer_value_category']}"
)


# ============================================================
# Step 18: Save Results
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_customer_value.csv"
)


seller_value[
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
    "Step 69 Seller Customer Value Analysis "
    "completed successfully."
)
print("============================================================")