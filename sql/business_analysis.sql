-- =========================================================
-- E-commerce Customer Analytics
-- SQL Business Analysis
-- =========================================================


-- =========================================================
-- 1. Total Orders
-- =========================================================

SELECT
    COUNT(DISTINCT order_id) AS total_orders
FROM orders;


-- =========================================================
-- 2. Total Customers
-- =========================================================

SELECT
    COUNT(DISTINCT customer_unique_id) AS total_customers
FROM customers;


-- =========================================================
-- 3. Total Revenue
-- =========================================================

SELECT
    ROUND(SUM(price), 2) AS total_revenue
FROM order_items;


-- =========================================================
-- 4. Average Order Value
-- =========================================================

SELECT
    ROUND(
        SUM(price) / COUNT(DISTINCT order_id),
        2
    ) AS average_order_value
FROM order_items;


-- =========================================================
-- 5. Monthly Revenue
-- =========================================================

SELECT
    strftime('%Y-%m', o.order_purchase_timestamp) AS order_month,
    ROUND(SUM(oi.price), 2) AS monthly_revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY strftime('%Y-%m', o.order_purchase_timestamp)
ORDER BY order_month;

-- =========================================================
-- 6. Top 10 Products by Revenue
-- =========================================================

SELECT
    product_id,
    ROUND(SUM(price), 2) AS total_revenue
FROM order_items
GROUP BY product_id
ORDER BY total_revenue DESC
LIMIT 10;


-- =========================================================
-- 7. Payment Method Usage
-- =========================================================

SELECT
    payment_type,
    COUNT(*) AS payment_count
FROM payments
GROUP BY payment_type
ORDER BY payment_count DESC;


-- =========================================================
-- 8. Average Review Score
-- =========================================================

SELECT
    ROUND(AVG(review_score), 2) AS average_review_score
FROM reviews;


-- =========================================================
-- 9. Order Status Distribution
-- =========================================================

SELECT
    order_status,
    COUNT(*) AS order_count
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;


-- =========================================================
-- 10. Top 10 Sellers by Revenue
-- =========================================================

SELECT
    seller_id,
    ROUND(SUM(price), 2) AS total_revenue
FROM order_items
GROUP BY seller_id
ORDER BY total_revenue DESC
LIMIT 10;


-- =========================================================
-- 11. Product Category Performance
-- =========================================================

SELECT
    p.product_category_name,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_revenue DESC;


-- =========================================================
-- 12. Customer Purchase Frequency
-- =========================================================

SELECT
    customer_unique_id,
    COUNT(DISTINCT order_id) AS order_count
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY customer_unique_id
ORDER BY order_count DESC;


-- =========================================================
-- 13. Repeat Customers
-- =========================================================

SELECT
    COUNT(*) AS repeat_customers
FROM (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
    HAVING COUNT(DISTINCT o.order_id) > 1
) AS repeat_customer_data;


-- =========================================================
-- 14. Revenue by Customer
-- =========================================================

SELECT
    c.customer_unique_id,
    ROUND(SUM(oi.price), 2) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY c.customer_unique_id
ORDER BY total_spending DESC
LIMIT 10;

-- =========================================================
-- 15. Customer Spending Rank (CTE + Window Function)
-- =========================================================

WITH customer_spending AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(SUM(oi.price), 2) AS total_spending
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    GROUP BY c.customer_unique_id
)
SELECT
    customer_unique_id,
    order_count,
    total_spending,
    RANK() OVER (ORDER BY total_spending DESC) AS spending_rank
FROM customer_spending
ORDER BY spending_rank
LIMIT 10;


-- =========================================================
-- 16. Month-over-Month Revenue Growth (CTE + LAG)
-- =========================================================

WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', o.order_purchase_timestamp) AS order_month,
        ROUND(SUM(oi.price), 2) AS revenue
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    GROUP BY strftime('%Y-%m', o.order_purchase_timestamp)
)
SELECT
    order_month,
    revenue,
    LAG(revenue) OVER (ORDER BY order_month) AS previous_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY order_month)) * 100.0
        / LAG(revenue) OVER (ORDER BY order_month),
        2
    ) AS growth_percent
FROM monthly_revenue
ORDER BY order_month;


