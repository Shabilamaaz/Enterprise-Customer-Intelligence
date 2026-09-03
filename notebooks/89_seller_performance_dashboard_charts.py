import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# Step 89: Seller Performance Dashboard Charts
# ============================================================

print("\n============================================================")
print("Step 89: Seller Performance Dashboard Charts")
print("============================================================")


# ============================================================
# Step 1: Find Project Root
# ============================================================

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent


# ============================================================
# Step 2: Locate Dashboard Data
# ============================================================

dashboard_path = (
    project_root
    / "data"
    / "seller_performance_dashboard.csv"
)

summary_path = (
    project_root
    / "data"
    / "seller_performance_dashboard_summary.csv"
)


print("\nDashboard data:")
print(dashboard_path)

print("\nSummary data:")
print(summary_path)


if not dashboard_path.exists():
    raise FileNotFoundError(
        "\nERROR: seller_performance_dashboard.csv "
        "was not found.\n"
        f"Expected location:\n{dashboard_path}"
    )


if not summary_path.exists():
    raise FileNotFoundError(
        "\nERROR: seller_performance_dashboard_summary.csv "
        "was not found.\n"
        f"Expected location:\n{summary_path}"
    )


# ============================================================
# Step 3: Load Data
# ============================================================

seller_data = pd.read_csv(
    dashboard_path
)

performance_summary = pd.read_csv(
    summary_path
)


print(
    f"\nSeller records loaded: "
    f"{len(seller_data)}"
)


# ============================================================
# Step 4: Create Chart Directory
# ============================================================

chart_directory = (
    project_root
    / "data"
    / "seller_dashboard_charts"
)


chart_directory.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Step 5: Top 10 Sellers by Revenue
# ============================================================

top_revenue = (
    seller_data
    .sort_values(
        "total_revenue",
        ascending=False
    )
    .head(10)
)


plt.figure(
    figsize=(12, 6)
)

plt.bar(
    top_revenue["seller_id"].astype(str),
    top_revenue["total_revenue"]
)

plt.title(
    "Top 10 Sellers by Revenue"
)

plt.xlabel(
    "Seller ID"
)

plt.ylabel(
    "Total Revenue"
)

plt.xticks(
    rotation=45
)

plt.tight_layout()


revenue_chart = (
    chart_directory
    / "top_10_sellers_by_revenue.png"
)


plt.savefig(
    revenue_chart,
    dpi=150
)

plt.close()


print(
    "\nRevenue chart saved to:"
)

print(revenue_chart)


# ============================================================
# Step 6: Top 10 Sellers by Profit
# ============================================================

top_profit = (
    seller_data
    .sort_values(
        "profit",
        ascending=False
    )
    .head(10)
)


plt.figure(
    figsize=(12, 6)
)

plt.bar(
    top_profit["seller_id"].astype(str),
    top_profit["profit"]
)

plt.title(
    "Top 10 Sellers by Profit"
)

plt.xlabel(
    "Seller ID"
)

plt.ylabel(
    "Profit"
)

plt.xticks(
    rotation=45
)

plt.tight_layout()


profit_chart = (
    chart_directory
    / "top_10_sellers_by_profit.png"
)


plt.savefig(
    profit_chart,
    dpi=150
)

plt.close()


print(
    "\nProfit chart saved to:"
)

print(profit_chart)


# ============================================================
# Step 7: Top 10 Sellers by Performance Score
# ============================================================

top_performance = (
    seller_data
    .sort_values(
        "performance_score",
        ascending=False
    )
    .head(10)
)


plt.figure(
    figsize=(12, 6)
)

plt.bar(
    top_performance["seller_id"].astype(str),
    top_performance["performance_score"]
)

plt.title(
    "Top 10 Sellers by Performance Score"
)

plt.xlabel(
    "Seller ID"
)

plt.ylabel(
    "Performance Score"
)

plt.xticks(
    rotation=45
)

plt.tight_layout()


performance_chart = (
    chart_directory
    / "top_10_sellers_by_performance_score.png"
)


plt.savefig(
    performance_chart,
    dpi=150
)

plt.close()


print(
    "\nPerformance chart saved to:"
)

print(performance_chart)


# ============================================================
# Step 8: Seller Performance Category Distribution
# ============================================================

category_counts = (
    seller_data[
        "performance_category"
    ]
    .value_counts()
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    category_counts.index,
    category_counts.values
)

plt.title(
    "Seller Performance Category Distribution"
)

plt.xlabel(
    "Performance Category"
)

plt.ylabel(
    "Number of Sellers"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()


category_chart = (
    chart_directory
    / "seller_performance_category_distribution.png"
)


plt.savefig(
    category_chart,
    dpi=150
)

plt.close()


print(
    "\nCategory chart saved to:"
)

print(category_chart)


# ============================================================
# Step 9: Revenue by Performance Category
# ============================================================

revenue_by_category = (
    seller_data
    .groupby(
        "performance_category"
    )["total_revenue"]
    .sum()
)


plt.figure(
    figsize=(10, 6)
)

plt.bar(
    revenue_by_category.index,
    revenue_by_category.values
)

plt.title(
    "Revenue by Seller Performance Category"
)

plt.xlabel(
    "Performance Category"
)

plt.ylabel(
    "Total Revenue"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()


category_revenue_chart = (
    chart_directory
    / "revenue_by_performance_category.png"
)


plt.savefig(
    category_revenue_chart,
    dpi=150
)

plt.close()


print(
    "\nCategory revenue chart saved to:"
)

print(category_revenue_chart)


# ============================================================
# Step 10: Profit Margin Distribution
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    seller_data["profit_margin"],
    bins=20
)

plt.title(
    "Seller Profit Margin Distribution"
)

plt.xlabel(
    "Profit Margin (%)"
)

plt.ylabel(
    "Number of Sellers"
)

plt.tight_layout()


margin_chart = (
    chart_directory
    / "seller_profit_margin_distribution.png"
)


plt.savefig(
    margin_chart,
    dpi=150
)

plt.close()


print(
    "\nMargin chart saved to:"
)

print(margin_chart)


# ============================================================
# Step 11: Performance Score Distribution
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    seller_data["performance_score"],
    bins=20
)

plt.title(
    "Seller Performance Score Distribution"
)

plt.xlabel(
    "Performance Score"
)

plt.ylabel(
    "Number of Sellers"
)

plt.tight_layout()


score_chart = (
    chart_directory
    / "seller_performance_score_distribution.png"
)


plt.savefig(
    score_chart,
    dpi=150
)

plt.close()


print(
    "\nScore chart saved to:"
)

print(score_chart)


# ============================================================
# Step 12: Revenue vs Profit
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.scatter(
    seller_data["total_revenue"],
    seller_data["profit"],
    alpha=0.6
)

plt.title(
    "Seller Revenue vs Profit"
)

plt.xlabel(
    "Total Revenue"
)

plt.ylabel(
    "Profit"
)

plt.tight_layout()


revenue_profit_chart = (
    chart_directory
    / "seller_revenue_vs_profit.png"
)


plt.savefig(
    revenue_profit_chart,
    dpi=150
)

plt.close()


print(
    "\nRevenue vs profit chart saved to:"
)

print(revenue_profit_chart)


# ============================================================
# Step 13: Orders vs Revenue
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.scatter(
    seller_data["total_orders"],
    seller_data["total_revenue"],
    alpha=0.6
)

plt.title(
    "Seller Orders vs Revenue"
)

plt.xlabel(
    "Total Orders"
)

plt.ylabel(
    "Total Revenue"
)

plt.tight_layout()


orders_revenue_chart = (
    chart_directory
    / "seller_orders_vs_revenue.png"
)


plt.savefig(
    orders_revenue_chart,
    dpi=150
)

plt.close()


print(
    "\nOrders vs revenue chart saved to:"
)

print(orders_revenue_chart)


# ============================================================
# Step 14: Performance Score vs Profit Margin
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.scatter(
    seller_data["performance_score"],
    seller_data["profit_margin"],
    alpha=0.6
)

plt.title(
    "Performance Score vs Profit Margin"
)

plt.xlabel(
    "Performance Score"
)

plt.ylabel(
    "Profit Margin (%)"
)

plt.tight_layout()


score_margin_chart = (
    chart_directory
    / "performance_score_vs_profit_margin.png"
)


plt.savefig(
    score_margin_chart,
    dpi=150
)

plt.close()


print(
    "\nScore vs margin chart saved to:"
)

print(score_margin_chart)


# ============================================================
# Step 15: Create Chart Index
# ============================================================

chart_index = pd.DataFrame(
    [
        {
            "chart_name": "Top 10 Sellers by Revenue",
            "file_name": "top_10_sellers_by_revenue.png"
        },
        {
            "chart_name": "Top 10 Sellers by Profit",
            "file_name": "top_10_sellers_by_profit.png"
        },
        {
            "chart_name": "Top 10 Sellers by Performance Score",
            "file_name": "top_10_sellers_by_performance_score.png"
        },
        {
            "chart_name": "Performance Category Distribution",
            "file_name": "seller_performance_category_distribution.png"
        },
        {
            "chart_name": "Revenue by Performance Category",
            "file_name": "revenue_by_performance_category.png"
        },
        {
            "chart_name": "Profit Margin Distribution",
            "file_name": "seller_profit_margin_distribution.png"
        },
        {
            "chart_name": "Performance Score Distribution",
            "file_name": "seller_performance_score_distribution.png"
        },
        {
            "chart_name": "Revenue vs Profit",
            "file_name": "seller_revenue_vs_profit.png"
        },
        {
            "chart_name": "Orders vs Revenue",
            "file_name": "seller_orders_vs_revenue.png"
        },
        {
            "chart_name": "Performance Score vs Profit Margin",
            "file_name": "performance_score_vs_profit_margin.png"
        }
    ]
)


# ============================================================
# Step 16: Save Chart Index
# ============================================================

index_path = (
    chart_directory
    / "chart_index.csv"
)


chart_index.to_csv(
    index_path,
    index=False
)


print(
    "\nChart index saved to:"
)

print(index_path)


# ============================================================
# Step 17: Close
# ============================================================

print("\n============================================================")
print(
    "Step 89 Seller Performance Dashboard Charts "
    "completed successfully."
)
print("============================================================")