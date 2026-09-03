import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 78: Seller Growth Opportunity Summary Analysis
# ============================================================

print("\n============================================================")
print("Step 78: Seller Growth Opportunity Summary Analysis")
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
# Step 6: Calculate Revenue Score
# ============================================================

seller_data["revenue_score"] = (
    seller_data["total_revenue"]
    /
    seller_data["total_revenue"].max()
) * 100


# ============================================================
# Step 7: Calculate Order Score
# ============================================================

seller_data["order_score"] = (
    seller_data["total_orders"]
    /
    seller_data["total_orders"].max()
) * 100


# ============================================================
# Step 8: Calculate Customer Score
# ============================================================

seller_data["customer_score"] = (
    seller_data["unique_customers"]
    /
    seller_data["unique_customers"].max()
) * 100


# ============================================================
# Step 9: Calculate AOV Score
# ============================================================

seller_data["aov_score"] = (
    seller_data["average_order_value"]
    /
    seller_data["average_order_value"].max()
) * 100


# ============================================================
# Step 10: Overall Seller Opportunity Score
# ============================================================

seller_data["opportunity_score"] = (
    seller_data["revenue_score"] * 0.40
    +
    seller_data["order_score"] * 0.25
    +
    seller_data["customer_score"] * 0.20
    +
    seller_data["aov_score"] * 0.15
)


seller_data["opportunity_score"] = (
    seller_data["opportunity_score"]
    .clip(
        lower=0,
        upper=100
    )
    .round(2)
)


# ============================================================
# Step 11: Opportunity Classification
# ============================================================

def classify_opportunity(score):

    if score >= 70:
        return "High Opportunity"

    elif score >= 50:
        return "Good Opportunity"

    elif score >= 30:
        return "Moderate Opportunity"

    elif score >= 15:
        return "Low Opportunity"

    else:
        return "Minimal Opportunity"


seller_data["opportunity_category"] = (
    seller_data["opportunity_score"]
    .apply(classify_opportunity)
)


# ============================================================
# Step 12: Rank Sellers
# ============================================================

seller_data = (
    seller_data
    .sort_values(
        by="opportunity_score",
        ascending=False
    )
    .reset_index(drop=True)
)


seller_data["opportunity_rank"] = (
    seller_data.index + 1
)


# ============================================================
# Step 13: Create Category Summary
# ============================================================

category_summary = (
    seller_data
    .groupby("opportunity_category")
    .agg(
        seller_count=(
            "seller_id",
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

        average_customers=(
            "unique_customers",
            "mean"
        ),

        average_order_value=(
            "average_order_value",
            "mean"
        ),

        average_opportunity_score=(
            "opportunity_score",
            "mean"
        )
    )
    .reset_index()
)


# ============================================================
# Step 14: Seller Percentage
# ============================================================

total_sellers = (
    category_summary["seller_count"]
    .sum()
)


category_summary["seller_percentage"] = (
    category_summary["seller_count"]
    /
    total_sellers
) * 100


# ============================================================
# Step 15: Revenue Contribution
# ============================================================

total_revenue = (
    category_summary["total_revenue"]
    .sum()
)


category_summary["revenue_contribution"] = (
    category_summary["total_revenue"]
    /
    total_revenue
) * 100


# ============================================================
# Step 16: Round Numeric Values
# ============================================================

numeric_columns = [
    "total_revenue",
    "average_revenue",
    "average_orders",
    "average_customers",
    "average_order_value",
    "average_opportunity_score",
    "seller_percentage",
    "revenue_contribution"
]


category_summary[numeric_columns] = (
    category_summary[numeric_columns]
    .round(2)
)


# ============================================================
# Step 17: Sort Categories
# ============================================================

category_order = [
    "High Opportunity",
    "Good Opportunity",
    "Moderate Opportunity",
    "Low Opportunity",
    "Minimal Opportunity"
]


category_summary["category_order"] = (
    category_summary["opportunity_category"]
    .map(
        {
            category: index
            for index, category
            in enumerate(category_order)
        }
    )
)


category_summary = (
    category_summary
    .sort_values("category_order")
    .drop(columns=["category_order"])
    .reset_index(drop=True)
)


# ============================================================
# Step 18: Display Category Summary
# ============================================================

print("\n============================================================")
print("Seller Growth Opportunity Summary")
print("============================================================")


print(
    category_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 19: Opportunity Distribution
# ============================================================

print("\n============================================================")
print("Opportunity Distribution")
print("============================================================")


for _, row in category_summary.iterrows():

    print(
        f"{row['opportunity_category']}: "
        f"{int(row['seller_count'])} sellers "
        f"({row['seller_percentage']:.2f}%)"
    )


# ============================================================
# Step 20: Revenue Contribution
# ============================================================

print("\n============================================================")
print("Revenue Contribution by Opportunity")
print("============================================================")


for _, row in category_summary.iterrows():

    print(
        f"{row['opportunity_category']}: "
        f"{row['revenue_contribution']:.2f}%"
    )


# ============================================================
# Step 21: Highest Opportunity Category
# ============================================================

highest_category = (
    category_summary.loc[
        category_summary[
            "average_opportunity_score"
        ].idxmax()
    ]
)


print("\n============================================================")
print("Highest Opportunity Category")
print("============================================================")


print(
    f"Category       : "
    f"{highest_category['opportunity_category']}"
)

print(
    f"Seller Count   : "
    f"{int(highest_category['seller_count'])}"
)

print(
    f"Average Score  : "
    f"{highest_category['average_opportunity_score']:.2f}"
)

print(
    f"Total Revenue  : "
    f"{highest_category['total_revenue']:.2f}"
)


# ============================================================
# Step 22: Best Opportunity Seller
# ============================================================

best_seller = seller_data.iloc[0]


print("\n============================================================")
print("Best Seller Growth Opportunity")
print("============================================================")


print(
    f"Rank             : "
    f"{int(best_seller['opportunity_rank'])}"
)

print(
    f"Seller ID        : "
    f"{best_seller['seller_id']}"
)

print(
    f"Total Revenue    : "
    f"{best_seller['total_revenue']:.2f}"
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
    f"Opportunity Score: "
    f"{best_seller['opportunity_score']:.2f}"
)

print(
    f"Category         : "
    f"{best_seller['opportunity_category']}"
)


# ============================================================
# Step 23: Top 10 Opportunities
# ============================================================

print("\n============================================================")
print("Top 10 Seller Opportunities")
print("============================================================")


top_columns = [
    "opportunity_rank",
    "seller_id",
    "total_orders",
    "unique_customers",
    "total_revenue",
    "average_order_value",
    "opportunity_score",
    "opportunity_category"
]


print(
    seller_data[
        top_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# Step 24: Overall Statistics
# ============================================================

average_score = (
    seller_data["opportunity_score"]
    .mean()
)

high_opportunity = (
    seller_data[
        "opportunity_category"
    ]
    .eq("High Opportunity")
    .sum()
)

good_opportunity = (
    seller_data[
        "opportunity_category"
    ]
    .eq("Good Opportunity")
    .sum()
)


print("\n============================================================")
print("Overall Opportunity Statistics")
print("============================================================")


print(
    f"Average Opportunity Score : "
    f"{average_score:.2f}"
)

print(
    f"High Opportunity Sellers  : "
    f"{int(high_opportunity)}"
)

print(
    f"Good Opportunity Sellers  : "
    f"{int(good_opportunity)}"
)


# ============================================================
# Step 25: Save Category Summary
# ============================================================

summary_path = (
    project_root
    / "data"
    / "seller_growth_opportunity_summary.csv"
)


category_summary.to_csv(
    summary_path,
    index=False
)


print("\nOpportunity summary saved to:")
print(summary_path)


# ============================================================
# Step 26: Save Detailed Seller Analysis
# ============================================================

detail_path = (
    project_root
    / "data"
    / "seller_growth_opportunity_detail.csv"
)


seller_data[
    [
        "opportunity_rank",
        "seller_id",
        "total_orders",
        "unique_customers",
        "total_revenue",
        "average_order_value",
        "revenue_score",
        "order_score",
        "customer_score",
        "aov_score",
        "opportunity_score",
        "opportunity_category"
    ]
].to_csv(
    detail_path,
    index=False
)


print("\nDetailed opportunity analysis saved to:")
print(detail_path)


# ============================================================
# Step 27: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 78 Seller Growth Opportunity Summary "
    "completed successfully."
)
print("============================================================")