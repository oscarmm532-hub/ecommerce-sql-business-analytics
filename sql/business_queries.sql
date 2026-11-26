-- ============================================================================
-- QUERY 1: Monthly Revenue & Month-over-Month (MoM) Growth Rate (CTE + LAG)
-- Business Goal: Track completed sales momentum and identify growth trends.
-- ============================================================================
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
    LAG(net_revenue) OVER (ORDER BY order_month) AS prev_month_revenue,
    ROUND(
        ((net_revenue - LAG(net_revenue) OVER (ORDER BY order_month))
        / LAG(net_revenue) OVER (ORDER BY order_month)) * 100,
        2
    ) AS mom_growth_pct
FROM monthly_sales
ORDER BY order_month;

-- ============================================================================
-- QUERY 2: Top Revenue-Generating Products per Category (DENSE_RANK)
-- Business Goal: Identify flagship items within each product line.
-- ============================================================================
WITH product_performance AS (
    SELECT
        p.category,
        p.product_name,
        SUM(o.quantity) AS units_sold,
        ROUND(SUM(o.quantity * p.unit_price), 2) AS total_revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    WHERE o.status = 'Completed'
    GROUP BY p.category, p.product_name
)
SELECT
    category,
    product_name,
    units_sold,
    total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS category_rank
FROM product_performance
ORDER BY category, category_rank;

-- ============================================================================
-- QUERY 3: Customer Lifetime Value (CLV) & Tier Segmentation
-- Business Goal: Classify customers into retention tiers based on net spend.
-- ============================================================================
WITH customer_spend AS (
    SELECT
        c.customer_id,
        c.full_name,
        c.country,
        c.segment,
        COUNT(o.order_id) AS completed_orders,
        ROUND(SUM(o.quantity * p.unit_price), 2) AS lifetime_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN products p ON o.product_id = p.product_id
    WHERE o.status = 'Completed'
    GROUP BY c.customer_id, c.full_name, c.country, c.segment
)
SELECT
    customer_id,
    full_name,
    country,
    segment,
    completed_orders,
    lifetime_value,
    CASE
        WHEN lifetime_value >= 2500 THEN 'VIP Tier'
        WHEN lifetime_value >= 1200 THEN 'Core Tier'
        ELSE 'Standard Tier'
    END AS clv_tier
FROM customer_spend
ORDER BY lifetime_value DESC
LIMIT 15;
