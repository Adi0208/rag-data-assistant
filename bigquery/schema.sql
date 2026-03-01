-- ============================================================
-- RAG Data Assistant — E-Commerce Schema
-- Project: rag-data-assistant
-- Dataset: ecommerce
-- ============================================================

-- 1. CUSTOMERS TABLE
CREATE TABLE IF NOT EXISTS `ecommerce.customers` (
  customer_id       STRING NOT NULL,
  first_name        STRING,
  last_name         STRING,
  email             STRING,
  city              STRING,
  country           STRING,
  signup_date       DATE,
  segment           STRING,   -- 'Premium', 'Regular', 'At-Risk'
  lifetime_value    FLOAT64
);

-- 2. PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS `ecommerce.products` (
  product_id        STRING NOT NULL,
  product_name      STRING,
  category          STRING,   -- 'Electronics', 'Clothing', 'Home', 'Sports'
  subcategory       STRING,
  unit_price        FLOAT64,
  cost_price        FLOAT64,
  stock_quantity    INT64,
  supplier          STRING
);

-- 3. ORDERS TABLE
CREATE TABLE IF NOT EXISTS `ecommerce.orders` (
  order_id          STRING NOT NULL,
  customer_id       STRING,
  order_date        DATE,
  status            STRING,   -- 'Completed', 'Returned', 'Cancelled', 'Pending'
  total_amount      FLOAT64,
  discount_applied  FLOAT64,
  shipping_city     STRING,
  shipping_country  STRING,
  payment_method    STRING    -- 'Credit Card', 'UPI', 'Net Banking', 'Wallet'
);

-- 4. ORDER ITEMS TABLE
CREATE TABLE IF NOT EXISTS `ecommerce.order_items` (
  item_id           STRING NOT NULL,
  order_id          STRING,
  product_id        STRING,
  quantity          INT64,
  unit_price        FLOAT64,
  total_price       FLOAT64
);

-- 5. REVIEWS TABLE
CREATE TABLE IF NOT EXISTS `ecommerce.reviews` (
  review_id         STRING NOT NULL,
  product_id        STRING,
  customer_id       STRING,
  rating            INT64,    -- 1 to 5
  review_text       STRING,
  review_date       DATE,
  helpful_votes     INT64
);
