# Data Profile — shopify-data

Generated: 2026-03-19 22:07:47

## Data Inventory

| File | Rows | Columns | Quality Score | Issues Found |
| --- | --- | --- | --- | --- |
| customers | 195 | 12 | 100.0% | None |
| orders | 903 | 19 | 96.5% | dropped null cols: ['note']; discount_code 66.7% missing |
| order_items | 2,766 | 8 | 100.0% | dropped null cols: ['variant_title'] |
| products | 25 | 9 | 100.0% | None |
| price_changes | 3 | 6 | 100.0% | None |

## Column Inventory

### customers

Columns: `customer_id`, `first_name`, `last_name`, `email`, `city`, `province`, `country`, `acquisition_channel`, `signup_date`, `accepts_marketing`, `total_orders`, `total_spent_usd`

Date columns parsed: `signup_date`

### orders

Columns: `order_id`, `order_number`, `created_at`, `customer_id`, `customer_email`, `financial_status`, `fulfillment_status`, `currency`, `subtotal`, `discount_code`, `discount_amount`, `shipping`, `taxes`, `total`, `payment_method`, `billing_city`, `billing_province`, `billing_country`, `source`

Date columns parsed: `created_at`

Fully-null columns dropped: `note`

### order_items

Columns: `order_id`, `line_item_id`, `product_sku`, `product_name`, `product_category`, `quantity`, `unit_price`, `line_total`

Fully-null columns dropped: `variant_title`

### products

Columns: `sku`, `product_name`, `category`, `current_price_usd`, `cost_usd`, `inventory_qty`, `weight_g`, `status`, `created_at`

Date columns parsed: `created_at`

### price_changes

Columns: `sku`, `product_name`, `old_price_usd`, `new_price_usd`, `change_date`, `change_reason`

Date columns parsed: `change_date`

## Date Ranges

### customers

- `signup_date`: 2025-09-01 00:00:00 → 2026-02-17 00:00:00

### orders

- `created_at`: 2025-12-01 06:36:33 → 2026-02-27 23:33:39

### products

- `created_at`: 2025-06-15 00:00:00 → 2025-06-15 00:00:00

### price_changes

- `change_date`: 2026-02-12 00:00:00 → 2026-02-12 00:00:00

## Relationships Detected

| From | To | Cardinality | Match % | Orphans |
| --- | --- | --- | --- | --- |
| orders.customer_id | customers.customer_id | many-to-one | 100.0% | 0 |
| order_items.order_id | orders.order_id | many-to-one | 100.0% | 0 |
| order_items.product_sku | products.sku | many-to-one | 100.0% | 0 |
| price_changes.sku | products.sku | many-to-one | 100.0% | 0 |

## Per-Table Column Profiles

### customers

| Column | Type | Unique | Missing | Stats / Top Values |
| --- | --- | --- | --- | --- |
| customer_id | object | 195 | 0 (0.0%) | top: CUST-1001(1), CUST-1002(1), CUST-1003(1) |
| first_name | object | 115 | 0 (0.0%) | top: Tushar(6), Jake(5), Nisha(5) |
| last_name | object | 77 | 0 (0.0%) | top: Wright(6), Thakur(6), Smith(5) |
| email | object | 195 | 0 (0.0%) | top: tanya.davis@protonmail.com(1), jordan.allen@gmail.com(1), henrywright@outlook.com(1) |
| city | object | 55 | 0 (0.0%) | top: Amsterdam(6), Berlin(6), Atlanta(6) |
| province | object | 40 | 0 (0.0%) | top: California(21), England(20), New York(11) |
| country | object | 10 | 0 (0.0%) | top: US(97), IN(39), GB(23) |
| acquisition_channel | object | 8 | 0 (0.0%) | top: Organic Search(42), Instagram Ads(38), Referral(32) |
| signup_date | datetime64[ns] | 116 | 0 (0.0%) | 2025-09-01 00:00:00 → 2026-02-17 00:00:00 |
| accepts_marketing | object | 2 | 0 (0.0%) | top: yes(147), no(48) |
| total_orders | int64 | 15 | 0 (0.0%) | min=0.0, max=16.0, mean=4.6308, median=4.0, std=2.9387 |
| total_spent_usd | float64 | 192 | 0 (0.0%) | min=0.0, max=3085.95, mean=819.5509, median=723.11, std=582.8112 |

### orders

| Column | Type | Unique | Missing | Stats / Top Values |
| --- | --- | --- | --- | --- |
| order_id | object | 903 | 0 (0.0%) | top: NB-5134(1), NB-5077(1), NB-5219(1) |
| order_number | int64 | 903 | 0 (0.0%) | min=5001.0, max=5903.0, mean=5452.0, median=5452.0, std=260.8179 |
| created_at | datetime64[ns] | 903 | 0 (0.0%) | 2025-12-01 06:36:33 → 2026-02-27 23:33:39 |
| customer_id | object | 191 | 0 (0.0%) | top: CUST-1061(16), CUST-1143(15), CUST-1119(15) |
| customer_email | object | 191 | 0 (0.0%) | top: rohit_walker@icloud.com(16), peterwilliams@protonmail.com(15), tushar_thomas@gmail.com(15) |
| financial_status | object | 1 | 0 (0.0%) | top: paid(903) |
| fulfillment_status | object | 3 | 0 (0.0%) | top: fulfilled(735), delivered(89), shipped(79) |
| currency | object | 1 | 0 (0.0%) | top: USD(903) |
| subtotal | float64 | 777 | 0 (0.0%) | min=10.92, max=901.79, mean=170.5318, median=140.95, std=118.6082 |
| discount_code | object | 4 | 602 (66.7%) | top: WELCOME10(81), LOYALTY5(75), NEWBREW20(74) |
| discount_amount | float64 | 272 | 0 (0.0%) | min=0.0, max=152.98, mean=6.9061, median=0.0, std=15.1272 |
| shipping | float64 | 3 | 0 (0.0%) | min=0.0, max=8.99, mean=0.2355, median=0.0, std=1.2515 |
| taxes | float64 | 765 | 0 (0.0%) | min=0.78, max=89.86, mean=13.1183, median=10.84, std=9.7552 |
| total | float64 | 889 | 0 (0.0%) | min=11.14, max=991.65, mean=176.9794, median=146.96, std=122.9284 |
| payment_method | object | 5 | 0 (0.0%) | top: Credit Card(399), PayPal(175), Google Pay(143) |
| billing_city | object | 55 | 0 (0.0%) | top: Los Angeles(38), Sacramento(32), Berlin(31) |
| billing_province | object | 40 | 0 (0.0%) | top: California(124), England(99), Texas(51) |
| billing_country | object | 10 | 0 (0.0%) | top: US(457), IN(193), GB(113) |
| source | object | 8 | 0 (0.0%) | top: Organic Search(198), Referral(170), Instagram Ads(142) |

### order_items

| Column | Type | Unique | Missing | Stats / Top Values |
| --- | --- | --- | --- | --- |
| order_id | object | 903 | 0 (0.0%) | top: NB-5822(6), NB-5631(6), NB-5778(6) |
| line_item_id | object | 2766 | 0 (0.0%) | top: LI-00001(1), LI-00002(1), LI-00003(1) |
| product_sku | object | 25 | 0 (0.0%) | top: EQ-001(165), CB-001(159), SUB-001(145) |
| product_name | object | 25 | 0 (0.0%) | top: Ceramic Pour-Over Dripper(165), Ethiopian Yirgacheffe Single Origin(159), Monthly Bean Box (2 bags)(145) |
| product_category | object | 4 | 0 (0.0%) | top: Coffee Beans(1014), Accessories(702), Brewing Equipment(625) |
| quantity | int64 | 4 | 0 (0.0%) | min=1.0, max=4.0, mean=1.8066, median=2.0, std=0.9677 |
| unit_price | float64 | 18 | 0 (0.0%) | min=8.99, max=89.99, mean=28.293, median=19.99, std=18.9245 |
| line_total | float64 | 71 | 0 (0.0%) | min=8.99, max=359.96, mean=50.5873, median=34.99, std=46.1913 |

### products

| Column | Type | Unique | Missing | Stats / Top Values |
| --- | --- | --- | --- | --- |
| sku | object | 25 | 0 (0.0%) | top: CB-001(1), CB-002(1), CB-003(1) |
| product_name | object | 25 | 0 (0.0%) | top: Ethiopian Yirgacheffe Single Origin(1), Colombian Supremo Blend(1), Sumatra Mandheling Dark Roast(1) |
| category | object | 4 | 0 (0.0%) | top: Coffee Beans(8), Accessories(8), Brewing Equipment(6) |
| current_price_usd | float64 | 18 | 0 (0.0%) | min=8.99, max=89.99, mean=29.13, median=19.99, std=19.1189 |
| cost_usd | float64 | 23 | 0 (0.0%) | min=2.0, max=30.0, mean=9.516, median=7.0, std=6.6431 |
| inventory_qty | int64 | 21 | 0 (0.0%) | min=45.0, max=999.0, mean=318.28, median=200.0, std=286.1125 |
| weight_g | int64 | 16 | 0 (0.0%) | min=85.0, max=2800.0, mean=590.44, median=454.0, std=527.8066 |
| status | object | 1 | 0 (0.0%) | top: active(25) |
| created_at | datetime64[ns] | 1 | 0 (0.0%) | 2025-06-15 00:00:00 → 2025-06-15 00:00:00 |

### price_changes

| Column | Type | Unique | Missing | Stats / Top Values |
| --- | --- | --- | --- | --- |
| sku | object | 3 | 0 (0.0%) | top: EQ-001(1), EQ-002(1), EQ-003(1) |
| product_name | object | 3 | 0 (0.0%) | top: Ceramic Pour-Over Dripper(1), Stainless Steel French Press (34oz)(1), Glass Cold Brew Maker (1.5L)(1) |
| old_price_usd | float64 | 3 | 0 (0.0%) | min=24.99, max=34.99, mean=29.99, median=29.99, std=5.0 |
| new_price_usd | float64 | 3 | 0 (0.0%) | min=34.99, max=44.99, mean=39.99, median=39.99, std=5.0 |
| change_date | datetime64[ns] | 1 | 0 (0.0%) | 2026-02-12 00:00:00 → 2026-02-12 00:00:00 |
| change_reason | object | 1 | 0 (0.0%) | top: Supplier cost increase — raw materials(3) |

## Data Quality Notes

- All column names standardised to `snake_case`.
- Fully-null columns removed (e.g. `note` in orders, `variant_title` in order_items).
- Date/datetime columns parsed to `datetime64[ns]`.
- Leading/trailing whitespace stripped from all string columns.
- Exact duplicate rows checked and removed where found.
- No numeric outlier removal was performed; flagged in per-column stats only.
- Missing values left in place; imputation deferred to analyst discretion.