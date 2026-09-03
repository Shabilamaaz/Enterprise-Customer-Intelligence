import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 88: Seller Performance Dashboard Data
# ============================================================

print("\n============================================================")
print("Step 88: Seller Performance Dashboard Data")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Find Database
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


# ============================================================
# Step 3: Connect to Database
# ============================================================

connection = sqlite3.connect(str(db_path))

print("\nDatabase connection successful.")


# ============================================================
# Step 4: Load Seller Performance Data
# ============================================================

query = """
SELECT
    oi.seller_id,

    COUNT(DISTINCT oi.order_id)
        AS total_orders,

    COUNT(DISTINCT o.customer_id)
        AS unique_customers,

    COUNT(oi.order_item_id)
        AS total_items_sold,

    SUM(oi.price)
        AS total_revenue,

    SUM(oi.freight_value)
        AS total_freight_cost,

    AVG(oi.price)
        AS average_order_value

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

WHERE
    o.order_status
    NOT IN ('canceled', 'unavailable')

GROUP BY
    oi.seller_id
"""


seller_data = pd.read_sql_query(
    query,
    connection
)


# ============================================================
# Step 5: Validate Data
# ============================================================

print(
    f"\nTotal sellers analyzed: "
    f"{len(seller_data)}"
)


if seller_data.empty:
    connection.close()

    raise RuntimeError(
        "\nERROR: No seller performance data was returned."
    )


# ============================================================
# Step 6: Calculate Profit
# ============================================================

seller_data["profit"] = (
    seller_data["total_revenue"]
    -
    seller_data["total_freight_cost"]
)


# ============================================================
# Step 7: Calculate Profit Margin
# ============================================================

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
# Step 8: Calculate Revenue Per Customer
# ============================================================

seller_data["revenue_per_customer"] = (
    seller_data["total_revenue"]
    /
    seller_data["unique_customers"]
)


seller_data["revenue_per_customer"] = (
    seller_data["revenue_per_customer"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 9: Calculate Revenue Per Order
# ============================================================

seller_data["revenue_per_order"] = (
    seller_data["total_revenue"]
    /
    seller_data["total_orders"]
)


seller_data["revenue_per_order"] = (
    seller_data["revenue_per_order"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 10: Calculate Seller Performance Score
# ============================================================

revenue_rank = (
    seller_data["total_revenue"]
    .rank(
        pct=True
    )
) * 100


orders_rank = (
    seller_data["total_orders"]
    .rank(
        pct=True
    )
) * 100


customers_rank = (
    seller_data["unique_customers"]
    .rank(
        pct=True
    )
) * 100


margin_rank = (
    seller_data["profit_margin"]
    .rank(
        pct=True
    )
) * 100


seller_data["performance_score"] = (
    revenue_rank * 0.35
    +
    orders_rank * 0.25
    +
    customers_rank * 0.20
    +
    margin_rank * 0.20
)


seller_data["performance_score"] = (
    seller_data["performance_score"]
    .round(2)
)


# ============================================================
# Step 11: Performance Category
# ============================================================

def classify_performance(score):

    if score >= 80:
        return "Top Performer"

    elif score >= 60:
        return "Strong Performer"

    elif score >= 40:
        return "Average Performer"

    elif score >= 20:
        return "Weak Performer"

    else:
        return "Underperformer"


seller_data["performance_category"] = (
    seller_data["performance_score"]
    .apply(classify_performance)
)


# ============================================================
# Step 12: Rank Sellers
# ============================================================

seller_data = (
    seller_data
    .sort_values(
        by="performance_score",
        ascending=False
    )
    .reset_index(drop=True)
)


seller_data["performance_rank"] = (
    seller_data.index + 1
)


# ============================================================
# Step 13: Dashboard KPI Values
# ============================================================

total_sellers = len(seller_data)

total_orders = (
    seller_data["total_orders"]
    .sum()
)

total_customers = (
    seller_data["unique_customers"]
    .sum()
)

total_items = (
    seller_data["total_items_sold"]
    .sum()
)

total_revenue = (
    seller_data["total_revenue"]
    .sum()
)

total_cost = (
    seller_data["total_freight_cost"]
    .sum()
)

total_profit = (
    seller_data["profit"]
    .sum()
)

overall_margin = (
    total_profit
    /
    total_revenue
) * 100 if total_revenue > 0 else 0


# ============================================================
# Step 14: Display Dashboard KPIs
# ============================================================

print("\n============================================================")
print("Seller Performance Dashboard KPIs")
print("============================================================")


print(
    f"Total Sellers       : {total_sellers}"
)

print(
    f"Total Orders        : {total_orders}"
)

print(
    f"Unique Customers    : {total_customers}"
)

print(
    f"Items Sold          : {total_items}"
)

print(
    f"Total Revenue       : {total_revenue:.2f}"
)

print(
    f"Total Freight Cost  : {total_cost:.2f}"
)

print(
    f"Total Profit        : {total_profit:.2f}"
)

print(
    f"Overall Profit Margin: {overall_margin:.2f}%"
)


# ============================================================
# Step 15: Top 10 Sellers
# ============================================================

top_sellers = seller_data.head(10)


print("\n============================================================")
print("Top 10 Sellers by Performance Score")
print("============================================================")


print(
    top_sellers[
        [
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
    ]
    .to_string(index=False)
)


# ============================================================
# Step 16: Performance Category Summary
# ============================================================

performance_summary = (
    seller_data
    .groupby("performance_category")
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

        average_score=(
            "performance_score",
            "mean"
        )
    )
    .reset_index()
)


performance_order = {
    "Top Performer": 1,
    "Strong Performer": 2,
    "Average Performer": 3,
    "Weak Performer": 4,
    "Underperformer": 5
}


performance_summary["category_order"] = (
    performance_summary[
        "performance_category"
    ]
    .map(performance_order)
)


performance_summary = (
    performance_summary
    .sort_values("category_order")
    .drop(columns=["category_order"])
    .reset_index(drop=True)
)


# ============================================================
# Step 17: Calculate Category Percentages
# ============================================================

performance_summary["seller_percentage"] = (
    performance_summary["seller_count"]
    /
    total_sellers
) * 100


performance_summary["revenue_percentage"] = (
    performance_summary["total_revenue"]
    /
    total_revenue
) * 100


performance_summary[
    [
        "total_revenue",
        "total_profit",
        "average_score",
        "seller_percentage",
        "revenue_percentage"
    ]
] = (
    performance_summary[
        [
            "total_revenue",
            "total_profit",
            "average_score",
            "seller_percentage",
            "revenue_percentage"
        ]
    ]
    .round(2)
)


# ============================================================
# Step 18: Display Performance Summary
# ============================================================

print("\n============================================================")
print("Seller Performance Category Summary")
print("============================================================")


print(
    performance_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 19: Top Revenue Seller
# ============================================================

top_revenue_seller = seller_data.loc[
    seller_data["total_revenue"].idxmax()
]


print("\n============================================================")
print("Top Revenue Seller")
print("============================================================")


print(
    f"Seller ID : "
    f"{top_revenue_seller['seller_id']}"
)

print(
    f"Revenue   : "
    f"{top_revenue_seller['total_revenue']:.2f}"
)

print(
    f"Profit    : "
    f"{top_revenue_seller['profit']:.2f}"
)


# ============================================================
# Step 20: Top Profit Seller
# ============================================================

top_profit_seller = seller_data.loc[
    seller_data["profit"].idxmax()
]


print("\n============================================================")
print("Top Profit Seller")
print("============================================================")


print(
    f"Seller ID : "
    f"{top_profit_seller['seller_id']}"
)

print(
    f"Profit    : "
    f"{top_profit_seller['profit']:.2f}"
)

print(
    f"Revenue   : "
    f"{top_profit_seller['total_revenue']:.2f}"
)


# ============================================================
# Step 21: Save Seller Dashboard Data
# ============================================================

dashboard_columns = [
    "performance_rank",
    "seller_id",
    "total_orders",
    "unique_customers",
    "total_items_sold",
    "total_revenue",
    "total_freight_cost",
    "profit",
    "profit_margin",
    "revenue_per_customer",
    "revenue_per_order",
    "performance_score",
    "performance_category"
]


dashboard_path = (
    project_root
    / "data"
    / "seller_performance_dashboard.csv"
)


seller_data[
    dashboard_columns
].to_csv(
    dashboard_path,
    index=False
)


print("\nSeller dashboard data saved to:")
print(dashboard_path)


# ============================================================
# Step 22: Save Performance Summary
# ============================================================

summary_path = (
    project_root
    / "data"
    / "seller_performance_dashboard_summary.csv"
)


performance_summary.to_csv(
    summary_path,
    index=False
)


print("\nSeller dashboard summary saved to:")
print(summary_path)


# ============================================================
# Step 23: Save KPI Summary
# ============================================================

kpi_data = pd.DataFrame(
    [
        {
            "metric": "Total Sellers",
            "value": total_sellers
        },
        {
            "metric": "Total Orders",
            "value": total_orders
        },
        {
            "metric": "Unique Customers",
            "value": total_customers
        },
        {
            "metric": "Items Sold",
            "value": total_items
        },
        {
            "metric": "Total Revenue",
            "value": round(total_revenue, 2)
        },
        {
            "metric": "Total Freight Cost",
            "value": round(total_cost, 2)
        },
        {
            "metric": "Total Profit",
            "value": round(total_profit, 2)
        },
        {
            "metric": "Overall Profit Margin",
            "value": round(overall_margin, 2)
        }
    ]
)


kpi_path = (
    project_root
    / "data"
    / "seller_performance_kpis.csv"
)


kpi_data.to_csv(
    kpi_path,
    index=False
)


print("\nSeller KPI data saved to:")
print(kpi_path)


# ============================================================
# Step 24: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 88 Seller Performance Dashboard Data "
    "completed successfully."
)
print("============================================================")