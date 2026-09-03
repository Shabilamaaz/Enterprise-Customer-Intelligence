import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 72: Seller Performance Ranking Analysis
# ============================================================

print("\n============================================================")
print("Step 72: Seller Performance Ranking Analysis")
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

    SUM(oi.price)
        AS total_revenue,

    SUM(oi.freight_value)
        AS total_freight,

    AVG(oi.price)
        AS average_order_value

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

WHERE o.order_status
NOT IN ('canceled', 'unavailable')

GROUP BY oi.seller_id
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
# Step 6: Calculate Revenue per Customer
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
# Step 7: Calculate Seller Performance Scores
# ============================================================

seller_data["revenue_score"] = (
    seller_data["total_revenue"]
    /
    seller_data["total_revenue"].max()
) * 100


seller_data["order_score"] = (
    seller_data["total_orders"]
    /
    seller_data["total_orders"].max()
) * 100


seller_data["customer_score"] = (
    seller_data["unique_customers"]
    /
    seller_data["unique_customers"].max()
) * 100


seller_data["aov_score"] = (
    seller_data["average_order_value"]
    /
    seller_data["average_order_value"].max()
) * 100


# ============================================================
# Step 8: Overall Seller Performance Score
# ============================================================

seller_data["performance_score"] = (
    seller_data["revenue_score"] * 0.40
    +
    seller_data["order_score"] * 0.25
    +
    seller_data["customer_score"] * 0.20
    +
    seller_data["aov_score"] * 0.15
)


seller_data["performance_score"] = (
    seller_data["performance_score"]
    .clip(lower=0, upper=100)
    .round(2)
)


# ============================================================
# Step 9: Performance Classification
# ============================================================

def classify_performance(score):

    if score >= 70:
        return "Excellent Performer"

    elif score >= 50:
        return "Strong Performer"

    elif score >= 30:
        return "Average Performer"

    elif score >= 15:
        return "Weak Performer"

    else:
        return "Low Performer"


seller_data["performance_category"] = (
    seller_data["performance_score"]
    .apply(classify_performance)
)


# ============================================================
# Step 10: Rank Sellers
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
# Step 11: Display Seller Performance
# ============================================================

result_columns = [
    "performance_rank",
    "seller_id",
    "total_orders",
    "unique_customers",
    "total_revenue",
    "average_order_value",
    "revenue_per_customer",
    "performance_score",
    "performance_category"
]


print("\n============================================================")
print("Seller Performance Ranking")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 12: Top 10 Sellers
# ============================================================

print("\n============================================================")
print("Top 10 Sellers by Performance")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# Step 13: Performance Category Summary
# ============================================================

print("\n============================================================")
print("Performance Category Summary")
print("============================================================")


print(
    seller_data[
        "performance_category"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# Step 14: Performance Statistics
# ============================================================

average_score = (
    seller_data["performance_score"].mean()
)

highest_score = (
    seller_data["performance_score"].max()
)

lowest_score = (
    seller_data["performance_score"].min()
)


print("\n============================================================")
print("Performance Statistics")
print("============================================================")


print(
    f"Average Performance Score : "
    f"{average_score:.2f}"
)

print(
    f"Highest Performance Score : "
    f"{highest_score:.2f}"
)

print(
    f"Lowest Performance Score  : "
    f"{lowest_score:.2f}"
)


# ============================================================
# Step 15: Best Performing Seller
# ============================================================

best_seller = seller_data.iloc[0]


print("\n============================================================")
print("Best Performing Seller")
print("============================================================")


print(
    f"Rank              : "
    f"{int(best_seller['performance_rank'])}"
)

print(
    f"Seller ID         : "
    f"{best_seller['seller_id']}"
)

print(
    f"Total Orders      : "
    f"{int(best_seller['total_orders'])}"
)

print(
    f"Unique Customers  : "
    f"{int(best_seller['unique_customers'])}"
)

print(
    f"Total Revenue     : "
    f"{best_seller['total_revenue']:.2f}"
)

print(
    f"Average Order     : "
    f"{best_seller['average_order_value']:.2f}"
)

print(
    f"Performance Score : "
    f"{best_seller['performance_score']:.2f}"
)

print(
    f"Category          : "
    f"{best_seller['performance_category']}"
)


# ============================================================
# Step 16: Save Results
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_performance_ranking.csv"
)


seller_data[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nResults saved to:")
print(output_path)


# ============================================================
# Step 17: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 72 Seller Performance Ranking "
    "completed successfully."
)
print("============================================================")