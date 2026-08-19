# Data Dictionary

## Customers
- `customer_id` — Unique identifier for an order-level customer record
- `customer_unique_id` — Unique identifier for the actual customer
- `customer_zip_code_prefix` — Customer ZIP code prefix
- `customer_city` — Customer city
- `customer_state` — Customer state

## Orders
- `order_id` — Unique order identifier
- `customer_id` — Customer associated with the order
- `order_status` — Current status of the order
- `order_purchase_timestamp` — Date/time when the order was placed
- `order_approved_at` — Date/time when payment was approved
- `order_delivered_carrier_date` — Date/time handed to carrier
- `order_delivered_customer_date` — Date/time delivered to customer
- `order_estimated_delivery_date` — Estimated delivery date