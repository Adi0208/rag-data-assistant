-- ============================================================
-- sample_queries.sql
-- Run these in BigQuery Console to verify your data is loaded
-- and to understand the dataset before building the AI layer.
-- ============================================================


-- ── 1. Basic Counts ──────────────────────────────────────────
SELECT 'customers'   AS table_name, COUNT(*) AS row_count FROM `ecommerce.customers`
UNION ALL
SELECT 'products',   COUNT(*) FROM `ecommerce.products`
UNION ALL
SELECT 'orders',     COUNT(*) FROM `ecommerce.orders`
UNION ALL
SELECT 'order_items',COUNT(*) FROM `ecommerce.order_items`
UNION ALL
SELECT 'reviews',    COUNT(*) FROM `ecommerce.reviews`
ORDER BY table_name;


-- ── 2. Revenue by Category (Q4 2024) ─────────────────────────
SELECT
  p.category,
  COUNT(DISTINCT o.order_id)      AS total_orders,
  SUM(oi.total_price)             AS gross_revenue,
  ROUND(AVG(oi.unit_price), 2)    AS avg_unit_price
FROM `ecommerce.orders`      o
JOIN `ecommerce.order_items` oi ON o.order_id    = oi.order_id
JOIN `ecommerce.products`    p  ON oi.product_id = p.product_id
WHERE o.order_date BETWEEN '2024-10-01' AND '2024-12-31'
  AND o.status = 'Completed'
GROUP BY p.category
ORDER BY gross_revenue DESC;


-- ── 3. Top 10 Customers by Revenue ───────────────────────────
SELECT
  c.customer_id,
  CONCAT(c.first_name, ' ', c.last_name)  AS customer_name,
  c.city,
  c.segment,
  COUNT(DISTINCT o.order_id)              AS total_orders,
  ROUND(SUM(o.total_amount), 2)           AS total_spent
FROM `ecommerce.customers` c
JOIN `ecommerce.orders`    o ON c.customer_id = o.customer_id
WHERE o.status = 'Completed'
GROUP BY 1, 2, 3, 4
ORDER BY total_spent DESC
LIMIT 10;


-- ── 4. Monthly Revenue Trend (2024) ───────────────────────────
SELECT
  FORMAT_DATE('%Y-%m', order_date)   AS month,
  COUNT(DISTINCT order_id)           AS orders,
  ROUND(SUM(total_amount), 2)        AS revenue,
  ROUND(AVG(total_amount), 2)        AS avg_order_value
FROM `ecommerce.orders`
WHERE EXTRACT(YEAR FROM order_date) = 2024
  AND status = 'Completed'
GROUP BY month
ORDER BY month;


-- ── 5. Product Return Rate ────────────────────────────────────
SELECT
  p.product_name,
  p.category,
  COUNT(CASE WHEN o.status = 'Completed' THEN 1 END) AS completed,
  COUNT(CASE WHEN o.status = 'Returned'  THEN 1 END) AS returned,
  ROUND(
    100.0 * COUNT(CASE WHEN o.status = 'Returned' THEN 1 END)
          / NULLIF(COUNT(*), 0), 1
  ) AS return_rate_pct
FROM `ecommerce.products`    p
JOIN `ecommerce.order_items` oi ON p.product_id  = oi.product_id
JOIN `ecommerce.orders`      o  ON oi.order_id   = o.order_id
GROUP BY 1, 2
HAVING COUNT(*) > 5
ORDER BY return_rate_pct DESC
LIMIT 15;


-- ── 6. Average Rating by Category ────────────────────────────
SELECT
  p.category,
  COUNT(r.review_id)          AS total_reviews,
  ROUND(AVG(r.rating), 2)     AS avg_rating,
  COUNTIF(r.rating >= 4)      AS positive_reviews,
  COUNTIF(r.rating <= 2)      AS negative_reviews
FROM `ecommerce.reviews`  r
JOIN `ecommerce.products` p ON r.product_id = p.product_id
GROUP BY p.category
ORDER BY avg_rating DESC;


-- ── 7. Customer Segment Analysis ─────────────────────────────
SELECT
  c.segment,
  COUNT(DISTINCT c.customer_id)        AS customers,
  ROUND(AVG(c.lifetime_value), 2)      AS avg_ltv,
  COUNT(DISTINCT o.order_id)           AS total_orders,
  ROUND(SUM(o.total_amount), 2)        AS total_revenue,
  ROUND(AVG(o.total_amount), 2)        AS avg_order_value
FROM `ecommerce.customers` c
LEFT JOIN `ecommerce.orders` o
       ON c.customer_id = o.customer_id AND o.status = 'Completed'
GROUP BY c.segment
ORDER BY total_revenue DESC;


-- ── 8. Payment Method Distribution ───────────────────────────
SELECT
  payment_method,
  COUNT(*)                                 AS orders,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS pct_share,
  ROUND(SUM(total_amount), 2)              AS total_revenue
FROM `ecommerce.orders`
WHERE status = 'Completed'
GROUP BY payment_method
ORDER BY orders DESC;
