import sqlite3
import pandas as pd
from pathlib import Path


# ============================================================
# Step 82: Seller Performance Segmentation
# ============================================================

print("\n============================================================")
print("Step 82: Seller Performance Segmentation")
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
# Step 8: Calculate Profit Per Order
# ============================================================

seller_data["profit_per_order"] = (
    seller_data["profit"]
    /
    seller_data["total_orders"]
)


seller_data["profit_per_order"] = (
    seller_data["profit_per_order"]
    .replace(
        [float("inf"), -float("inf")],
        0
    )
    .fillna(0)
)


# ============================================================
# Step 9: Calculate Revenue Score
# ============================================================

max_revenue = seller_data["total_revenue"].max()


if max_revenue > 0:

    seller_data["revenue_score"] = (
        seller_data["total_revenue"]
        /
        max_revenue
    ) * 100

else:

    seller_data["revenue_score"] = 0


# ============================================================
# Step 10: Calculate Order Score
# ============================================================

max_orders = seller_data["total_orders"].max()


if max_orders > 0:

    seller_data["order_score"] = (
        seller_data["total_orders"]
        /
        max_orders
    ) * 100

else:

    seller_data["order_score"] = 0


# ============================================================
# Step 11: Calculate Customer Score
# ============================================================

max_customers = (
    seller_data["unique_customers"].max()
)


if max_customers > 0:

    seller_data["customer_score"] = (
        seller_data["unique_customers"]
        /
        max_customers
    ) * 100

else:

    seller_data["customer_score"] = 0


# ============================================================
# Step 12: Calculate Profit Score
# ============================================================

positive_profit = seller_data["profit"].clip(
    lower=0
)

max_profit = positive_profit.max()


if max_profit > 0:

    seller_data["profit_score"] = (
        positive_profit
        /
        max_profit
    ) * 100

else:

    seller_data["profit_score"] = 0


# ============================================================
# Step 13: Calculate Margin Score
# ============================================================

positive_margin = seller_data["profit_margin"].clip(
    lower=0
)

max_margin = positive_margin.max()


if max_margin > 0:

    seller_data["margin_score"] = (
        positive_margin
        /
        max_margin
    ) * 100

else:

    seller_data["margin_score"] = 0


# ============================================================
# Step 14: Overall Performance Score
# ============================================================

seller_data["performance_score"] = (
    seller_data["revenue_score"] * 0.25
    +
    seller_data["order_score"] * 0.15
    +
    seller_data["customer_score"] * 0.15
    +
    seller_data["profit_score"] * 0.30
    +
    seller_data["margin_score"] * 0.15
)


seller_data["performance_score"] = (
    seller_data["performance_score"]
    .clip(
        lower=0,
        upper=100
    )
    .round(2)
)


# ============================================================
# Step 15: Seller Performance Segmentation
# ============================================================

def classify_segment(row):

    score = row["performance_score"]
    margin = row["profit_margin"]
    profit = row["profit"]

    if (
        score >= 70
        and profit > 0
        and margin >= 30
    ):
        return "Top Performer"

    elif (
        score >= 50
        and profit > 0
        and margin >= 20
    ):
        return "Strong Performer"

    elif (
        score >= 30
        and profit > 0
    ):
        return "Average Performer"

    elif profit > 0:
        return "Low Performer"

    else:
        return "At Risk"


seller_data["performance_segment"] = (
    seller_data
    .apply(
        classify_segment,
        axis=1
    )
)


# ============================================================
# Step 16: Rank Sellers
# ============================================================

seller_data = (
    seller_data
    .sort_values(
        by=[
            "performance_score",
            "profit",
            "total_revenue"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )
    .reset_index(drop=True)
)


seller_data["performance_rank"] = (
    seller_data.index + 1
)


# ============================================================
# Step 17: Display Seller Segmentation
# ============================================================

result_columns = [
    "performance_rank",
    "seller_id",
    "total_orders",
    "unique_customers",
    "total_revenue",
    "total_freight_cost",
    "profit",
    "profit_margin",
    "profit_per_order",
    "performance_score",
    "performance_segment"
]


print("\n============================================================")
print("Seller Performance Segmentation")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# Step 18: Top 10 Performers
# ============================================================

print("\n============================================================")
print("Top 10 Seller Performers")
print("============================================================")


print(
    seller_data[
        result_columns
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# Step 19: Segment Summary
# ============================================================

segment_summary = (
    seller_data
    .groupby("performance_segment")
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

        average_revenue=(
            "total_revenue",
            "mean"
        ),

        average_profit=(
            "profit",
            "mean"
        ),

        average_profit_margin=(
            "profit_margin",
            "mean"
        ),

        average_performance_score=(
            "performance_score",
            "mean"
        )
    )
    .reset_index()
)


# ============================================================
# Step 20: Calculate Segment Percentages
# ============================================================

total_sellers = (
    segment_summary["seller_count"]
    .sum()
)


segment_summary["seller_percentage"] = (
    segment_summary["seller_count"]
    /
    total_sellers
) * 100


# ============================================================
# Step 21: Calculate Revenue Contribution
# ============================================================

total_revenue = (
    segment_summary["total_revenue"]
    .sum()
)


if total_revenue > 0:

    segment_summary["revenue_contribution"] = (
        segment_summary["total_revenue"]
        /
        total_revenue
    ) * 100

else:

    segment_summary["revenue_contribution"] = 0


# ============================================================
# Step 22: Calculate Profit Contribution
# ============================================================

total_profit = (
    segment_summary["total_profit"]
    .sum()
)


if total_profit != 0:

    segment_summary["profit_contribution"] = (
        segment_summary["total_profit"]
        /
        total_profit
    ) * 100

else:

    segment_summary["profit_contribution"] = 0


# ============================================================
# Step 23: Round Summary Values
# ============================================================

numeric_columns = [
    "total_revenue",
    "total_profit",
    "average_revenue",
    "average_profit",
    "average_profit_margin",
    "average_performance_score",
    "seller_percentage",
    "revenue_contribution",
    "profit_contribution"
]


segment_summary[numeric_columns] = (
    segment_summary[numeric_columns]
    .round(2)
)


# ============================================================
# Step 24: Sort Segments
# ============================================================

segment_order = [
    "Top Performer",
    "Strong Performer",
    "Average Performer",
    "Low Performer",
    "At Risk"
]


segment_summary["segment_order"] = (
    segment_summary["performance_segment"]
    .map(
        {
            segment: index
            for index, segment
            in enumerate(segment_order)
        }
    )
)


segment_summary = (
    segment_summary
    .sort_values("segment_order")
    .drop(columns=["segment_order"])
    .reset_index(drop=True)
)


# ============================================================
# Step 25: Display Segment Summary
# ============================================================

print("\n============================================================")
print("Seller Performance Segment Summary")
print("============================================================")


print(
    segment_summary.to_string(
        index=False
    )
)


# ============================================================
# Step 26: Segment Distribution
# ============================================================

print("\n============================================================")
print("Seller Segment Distribution")
print("============================================================")


for _, row in segment_summary.iterrows():

    print(
        f"{row['performance_segment']}: "
        f"{int(row['seller_count'])} sellers "
        f"({row['seller_percentage']:.2f}%)"
    )


# ============================================================
# Step 27: Revenue Contribution
# ============================================================

print("\n============================================================")
print("Revenue Contribution by Segment")
print("============================================================")


for _, row in segment_summary.iterrows():

    print(
        f"{row['performance_segment']}: "
        f"{row['revenue_contribution']:.2f}%"
    )


# ============================================================
# Step 28: Profit Contribution
# ============================================================

print("\n============================================================")
print("Profit Contribution by Segment")
print("============================================================")


for _, row in segment_summary.iterrows():

    print(
        f"{row['performance_segment']}: "
        f"{row['profit_contribution']:.2f}%"
    )


# ============================================================
# Step 29: Best Seller
# ============================================================

best_seller = seller_data.iloc[0]


print("\n============================================================")
print("Top Performing Seller")
print("============================================================")


print(
    f"Seller ID        : "
    f"{best_seller['seller_id']}"
)

print(
    f"Performance Rank : "
    f"{int(best_seller['performance_rank'])}"
)

print(
    f"Revenue          : "
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
    f"Segment          : "
    f"{best_seller['performance_segment']}"
)


# ============================================================
# Step 30: At-Risk Sellers
# ============================================================

at_risk = seller_data[
    seller_data["performance_segment"]
    == "At Risk"
]


print("\n============================================================")
print("At-Risk Sellers")
print("============================================================")


print(
    f"At-Risk Sellers: "
    f"{len(at_risk)}"
)


if not at_risk.empty:

    print(
        at_risk[
            [
                "seller_id",
                "total_revenue",
                "total_orders",
                "profit",
                "profit_margin",
                "performance_score"
            ]
        ]
        .sort_values(
            by="performance_score"
        )
        .head(10)
        .to_string(index=False)
    )

else:

    print(
        "No at-risk sellers identified."
    )


# ============================================================
# Step 31: Overall Statistics
# ============================================================

average_score = (
    seller_data["performance_score"]
    .mean()
)

highest_score = (
    seller_data["performance_score"]
    .max()
)

lowest_score = (
    seller_data["performance_score"]
    .min()
)


print("\n============================================================")
print("Overall Performance Statistics")
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
# Step 32: Save Seller Segmentation
# ============================================================

output_path = (
    project_root
    / "data"
    / "seller_performance_segmentation.csv"
)


seller_data[
    result_columns
].to_csv(
    output_path,
    index=False
)


print("\nSeller segmentation saved to:")
print(output_path)


# ============================================================
# Step 33: Save Segment Summary
# ============================================================

summary_path = (
    project_root
    / "data"
    / "seller_performance_segment_summary.csv"
)


segment_summary.to_csv(
    summary_path,
    index=False
)


print("\nSegment summary saved to:")
print(summary_path)


# ============================================================
# Step 34: Close Database
# ============================================================

connection.close()


# ============================================================
# Completion Message
# ============================================================

print("\n============================================================")
print(
    "Step 82 Seller Performance Segmentation "
    "completed successfully."
)
print("============================================================")