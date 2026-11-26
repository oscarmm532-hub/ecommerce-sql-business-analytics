import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from build_db import build_ecommerce_db

DB_PATH = "data/ecommerce.db"


def run_business_analysis():
  if not os.path.exists(DB_PATH):
    build_ecommerce_db(DB_PATH)

  conn = sqlite3.connect(DB_PATH)

  # 1. Consulta SQL: Ingresos mensuales y crecimiento MoM (CTE + LAG)
  mom_query = """
    WITH monthly_sales AS (
        SELECT
            strftime('%Y-%m', o.order_date) AS order_month,
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(SUM(o.quantity * p.unit_price), 2) AS net_revenue
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE o.status = 'Completed'
        GROUP BY strftime('%Y-%m', o.order_date)
    )
    SELECT
        order_month,
        total_orders,
        net_revenue,
        ROUND(
            ((net_revenue - LAG(net_revenue) OVER (ORDER BY order_month))
            / LAG(net_revenue) OVER (ORDER BY order_month)) * 100,
            2
        ) AS mom_growth_pct
    FROM monthly_sales
    ORDER BY order_month;
    """
  df_monthly = pd.read_sql_query(mom_query, conn)

  # 2. Consulta SQL: Ingresos por categoría y segmento de cliente
  category_query = """
    SELECT
        p.category,
        c.segment,
        ROUND(SUM(o.quantity * p.unit_price), 2) AS revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'Completed'
    GROUP BY p.category, c.segment
    ORDER BY revenue DESC;
    """
  df_cat = pd.read_sql_query(category_query, conn)
  conn.close()

  print("=== Monthly Revenue & MoM Growth ===")
  print(df_monthly.to_string(index=False))

  # 3. Generar tablero visual ejecutivo (2 paneles)
  fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=150)

  # Panel izquierdo: Tendencia de ingresos mensuales
  axes[0].plot(
      df_monthly["order_month"],
      df_monthly["net_revenue"],
      marker="o",
      linewidth=2.5,
      color="#2563eb",
  )
  axes[0].set_title(
      "Monthly Net Revenue Trend (2026)", fontsize=12, fontweight="bold", pad=10
  )
  axes[0].set_ylabel("Net Revenue ($ USD)", fontsize=10)
  axes[0].tick_params(axis="x", rotation=45)
  axes[0].grid(True, linestyle="--", alpha=0.5)

  # Panel derecho: Ingresos por categoría y segmento
  pivot_cat = df_cat.pivot(
      index="category", columns="segment", values="revenue"
  ).fillna(0)
  pivot_cat.plot(
      kind="bar",
      stacked=True,
      ax=axes[1],
      color=["#1e40af", "#3b82f6", "#93c5fd"],
  )
  axes[1].set_title(
      "Net Revenue by Category & Customer Segment",
      fontsize=12,
      fontweight="bold",
      pad=10,
  )
  axes[1].set_ylabel("Net Revenue ($ USD)", fontsize=10)
  axes[1].set_xlabel("")
  axes[1].tick_params(axis="x", rotation=0)
  axes[1].grid(axis="y", linestyle="--", alpha=0.5)
  axes[1].legend(title="Segment")

  plt.tight_layout()
  plt.savefig("revenue_kpis.png")
  print("\nExecutive chart saved successfully as: revenue_kpis.png")


if __name__ == "__main__":
  run_business_analysis()
