import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 66: Seller Performance Ranking Analysis
# ============================================================

print("\n============================================================")
print("Step 66: Seller Performance Ranking Analysis")
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
# Step 4: Load Seller Performance Data
# ============================================================

query = """
SELECT

    oi.seller_id,

    COUNT(DISTINCT oi.order_id)
        AS total_orders,

    COUNT(*) AS total_items_sold,

    COUNT(DISTINCT o.customer_id)
        AS unique_customers,

    SUM(oi.price)
        AS total_revenue,

    SUM(oi.freight_value)
        AS total_freight_cost,

    AVG(oi.price)
        AS average_item_price

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

WHERE o.order_status
NOT IN ('canceled', 'unavailable')

GROUP BY oi.seller_id
"""


seller_performance = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# Step 5: Check Data
# ============================================================

print(
    f"\nTotal sellers analyzed: "
    f"{len(seller_performance)}"
)


if seller_performance.empty:

    connection.close()

    raise RuntimeError(
        "\nERROR: No seller performance data "
        "was returned."
    )


# ============================================================
# Step 6: Calculate Profit
# ============================================================

seller_performance["profit"] = (
    seller_performance["total_revenue"]
    - seller_performance["total_freight_cost"]
)


# ============================================================
# Step 7: Calculate Profit Margin
# ============================================================

seller_performance["profit_margin"] = (
    seller_performance["profit"]
    /
    seller_performance["total_revenue"]
) * 100


seller_performance["profit_margin"] = (
    seller_performance["profit_margin"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 8: Calculate Revenue per Order
# ============================================================

seller_performance["revenue_per_order"] = (
    seller_performance["total_revenue"]
    /
    seller_performance["total_orders"]
)


seller_performance["revenue_per_order"] = (
    seller_performance["revenue_per_order"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 9: Create Normalized Performance Metrics
# ============================================================

seller_performance["revenue_score"] = (
    seller_performance["total_revenue"]
    /
    seller_performance["total_revenue"].max()
) * 100


seller_performance["order_score"] = (
    seller_performance["total_orders"]
    /
    seller_performance["total_orders"].max()
) * 100


seller_performance["profit_score"] = (
    seller_performance["profit"]
    /
    seller_performance["profit"].max()
) * 100


seller_performance["margin_score"] = (
    seller_performance["profit_margin"]
    /
    seller_performance["profit_margin"].max()
) * 100


# ============================================================
# Step 10: Calculate Overall Performance Score
# ============================================================

seller_performance["performance_score"] = (

    seller_performance["revenue_score"] * 0.30

    +

    seller_performance["order_score"] * 0.20

    +

    seller_performance["profit_score"] * 0.30

    +

    seller_performance["margin_score"] * 0.20

)


seller_performance["performance_score"] = (
    seller_performance["performance_score"]
    .round(2)
)


# ============================================================
# Step 11: Rank Sellers
# ============================================================

seller_performance = (
    seller_performance
    .sort_values(
        by="performance_score",
        ascending=False
    )
    .reset_index(drop=True)
)


seller_performance["performance_rank"] = (
    seller_performance.index + 1
)


# ============================================================
# Step 12: Performance Classification
# ============================================================

def classify_performance(score):

    if score >= 70:
        return "Excellent Performer"

    elif score >= 40:
        return "Strong Performer"

    elif score >= 20:
        return "Average Performer"

    else:
        return "Low Performer"


seller_performance["performance_category"] = (
    seller_performance["performance_score"]
    .apply(classify_performance)
)


# ============================================================
# Step 13: Display Seller Rankings
# ============================================================

result_columns = [

    "performance_rank",
    "seller_id",
    "total_orders",
    "unique_customers",
    "total_revenue",
    "profit",
    "profit_margin",
    "performance_score",
    "performance_category"

]


print("\n============================================================")
print("Seller Performance Ranking")
print("============================================================")


print(
    seller_performance[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 14: Top 10 Sellers
# ============================================================

print("\n============================================================")
print("Top 10 Performing Sellers")
print("============================================================")


print(
    seller_performance[
        result_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# Step 15: Performance Category Summary
# ============================================================

print("\n============================================================")
print("Performance Category Summary")
print("============================================================")


print(
    seller_performance[
        "performance_category"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 16: Overall Statistics
# ============================================================

average_performance_score = (
    seller_performance[
        "performance_score"
    ].mean()
)


highest_performance_score = (
    seller_performance[
        "performance_score"
    ].max()
)


lowest_performance_score = (
    seller_performance[
        "performance_score"
    ].min()
)


print("\n============================================================")
print("Performance Statistics")
print("============================================================")


print(
    f"Average Performance Score : "
    f"{average_performance_score:.2f}"
)


print(
    f"Highest Performance Score : "
    f"{highest_performance_score:.2f}"
)


print(
    f"Lowest Performance Score  : "
    f"{lowest_performance_score:.2f}"
)


# ============================================================
# Step 17: Best Performing Seller
# ============================================================

best_seller = seller_performance.iloc[0]


print("\n============================================================")
print("Best Performing Seller")
print("============================================================")


print(
    f"Performance Rank : "
    f"{int(best_seller['performance_rank'])}"
)


print(
    f"Seller ID        : "
    f"{best_seller['seller_id']}"
)


print(
    f"Total Orders     : "
    f"{int(best_seller['total_orders'])}"
)


print(
    f"Unique Customers : "
    f"{int(best_seller['unique_customers'])}"
)


print(
    f"Total Revenue    : "
    f"{best_seller['total_revenue']:.2f}"
)


print(
    f"Profit           : "
    f"{best_seller['profit']:.2f}"
)


print(
    f"Profit Margin    : "
    f"{best_seller['profit_margin']:.2f}%"
)


print(
    f"Performance Score: "
    f"{best_seller['performance_score']:.2f}"
)


print(
    f"Category         : "
    f"{best_seller['performance_category']}"
)


# ============================================================
# Step 18: Save Ranking Result
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_performance_ranking.csv"
)


seller_performance[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nRanking results saved to:")
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
    "Step 66 Seller Performance Ranking Analysis "
    "completed successfully."
)
print("============================================================")