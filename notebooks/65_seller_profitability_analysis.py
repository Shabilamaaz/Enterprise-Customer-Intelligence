import sqlite3
import pandas as pd
from pathlib import Path

# ============================================================
# Step 65: Seller Profitability Analysis
# ============================================================

print("\n============================================================")
print("Step 65: Seller Profitability Analysis")
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
# Step 4: Load Seller Profitability Data
# ============================================================

query = """
SELECT
    oi.seller_id,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    COUNT(*) AS total_items_sold,

    ROUND(
        SUM(oi.price),
        2
    ) AS total_revenue,

    ROUND(
        SUM(oi.freight_value),
        2
    ) AS total_freight_cost,

    ROUND(
        AVG(oi.price),
        2
    ) AS average_item_price

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

WHERE o.order_status
NOT IN ('canceled', 'unavailable')

GROUP BY oi.seller_id
"""


seller_profitability = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# Step 5: Check Data
# ============================================================

print(
    f"\nTotal sellers analyzed: "
    f"{len(seller_profitability)}"
)


if seller_profitability.empty:
    connection.close()

    raise RuntimeError(
        "\nERROR: No seller profitability data "
        "was returned."
    )


# ============================================================
# Step 6: Calculate Profit
# ============================================================

seller_profitability["profit"] = (
    seller_profitability["total_revenue"]
    - seller_profitability["total_freight_cost"]
)


# ============================================================
# Step 7: Calculate Profit Margin
# ============================================================

seller_profitability["profit_margin"] = (
    seller_profitability["profit"]
    /
    seller_profitability["total_revenue"]
) * 100


seller_profitability["profit_margin"] = (
    seller_profitability["profit_margin"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 8: Calculate Revenue per Order
# ============================================================

seller_profitability["revenue_per_order"] = (
    seller_profitability["total_revenue"]
    /
    seller_profitability["total_orders"]
)


seller_profitability["revenue_per_order"] = (
    seller_profitability["revenue_per_order"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 9: Calculate Profit per Order
# ============================================================

seller_profitability["profit_per_order"] = (
    seller_profitability["profit"]
    /
    seller_profitability["total_orders"]
)


seller_profitability["profit_per_order"] = (
    seller_profitability["profit_per_order"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 10: Profitability Classification
# ============================================================

def classify_profitability(margin):

    if margin >= 70:
        return "Highly Profitable"

    elif margin >= 40:
        return "Profitable"

    elif margin >= 20:
        return "Moderately Profitable"

    elif margin > 0:
        return "Low Profitability"

    else:
        return "Unprofitable"


seller_profitability["profitability_category"] = (
    seller_profitability["profit_margin"]
    .apply(classify_profitability)
)


# ============================================================
# Step 11: Sort by Profit
# ============================================================

top_profit_sellers = (
    seller_profitability
    .sort_values(
        by="profit",
        ascending=False
    )
    .head(10)
)


# ============================================================
# Step 12: Display Seller Profitability
# ============================================================

result_columns = [

    "seller_id",
    "total_orders",
    "total_items_sold",
    "total_revenue",
    "total_freight_cost",
    "profit",
    "profit_margin",
    "revenue_per_order",
    "profit_per_order",
    "profitability_category"

]


print("\n============================================================")
print("Seller Profitability Analysis")
print("============================================================")


print(
    seller_profitability[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 13: Top 10 Most Profitable Sellers
# ============================================================

print("\n============================================================")
print("Top 10 Most Profitable Sellers")
print("============================================================")


print(
    top_profit_sellers[
        result_columns
    ]
    .to_string(index=False)
)


# ============================================================
# Step 14: Profitability Category Summary
# ============================================================

print("\n============================================================")
print("Profitability Category Summary")
print("============================================================")


print(
    seller_profitability[
        "profitability_category"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 15: Overall Statistics
# ============================================================

total_revenue = (
    seller_profitability["total_revenue"]
    .sum()
)

total_profit = (
    seller_profitability["profit"]
    .sum()
)

average_profit_margin = (
    seller_profitability["profit_margin"]
    .mean()
)

highest_profit = (
    seller_profitability["profit"]
    .max()
)

lowest_profit = (
    seller_profitability["profit"]
    .min()
)


print("\n============================================================")
print("Profitability Statistics")
print("============================================================")


print(
    f"Total Revenue         : "
    f"{total_revenue:.2f}"
)

print(
    f"Total Profit          : "
    f"{total_profit:.2f}"
)

print(
    f"Average Profit Margin : "
    f"{average_profit_margin:.2f}%"
)

print(
    f"Highest Seller Profit : "
    f"{highest_profit:.2f}"
)

print(
    f"Lowest Seller Profit  : "
    f"{lowest_profit:.2f}"
)


# ============================================================
# Step 16: Most Profitable Seller
# ============================================================

best_seller = seller_profitability.loc[
    seller_profitability["profit"].idxmax()
]


print("\n============================================================")
print("Most Profitable Seller")
print("============================================================")


print(
    f"Seller ID          : "
    f"{best_seller['seller_id']}"
)

print(
    f"Total Orders       : "
    f"{int(best_seller['total_orders'])}"
)

print(
    f"Total Revenue      : "
    f"{best_seller['total_revenue']:.2f}"
)

print(
    f"Total Freight Cost : "
    f"{best_seller['total_freight_cost']:.2f}"
)

print(
    f"Profit             : "
    f"{best_seller['profit']:.2f}"
)

print(
    f"Profit Margin      : "
    f"{best_seller['profit_margin']:.2f}%"
)

print(
    f"Category           : "
    f"{best_seller['profitability_category']}"
)


# ============================================================
# Step 17: Close Database Connection
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 65 Seller Profitability Analysis "
    "completed successfully."
)
print("============================================================")