# FRAUD DETECTIVE — Investigation Report

## Executive Summary

> **Detected 5901 anomalies** across 14157 transactions, representing an estimated **$4,604,948 in financial impact**. Fraud rate: **41.7%** of all transactions.

---

## Crime-by-Crime Breakdown

### 1. Stolen Cards (Impossible Geography)
- **19 cards** used in multiple countries within 2-hour windows
- These represent physically impossible travel scenarios
- Card ****1961: Manchester, UK -> Sydney, AU in 90.0 minutes
- Card ****2038: Toronto, CA -> Sydney, AU in 70.0 minutes
- Card ****2329: Various, UK -> Various, IN in 94.7 minutes
- Card ****2754: London, UK -> Sydney, AU in 69.0 minutes
- Card ****3491: Manchester, UK -> Berlin, DE in 90.0 minutes
- Card ****4487: Toronto, CA -> Sydney, AU in 53.0 minutes
- Card ****4852: Mumbai, IN -> New York, US in 47.0 minutes
- Card ****5535: London, UK -> Sydney, AU in 17.0 minutes
- Card ****5535: London, UK -> New York, US in 30.0 minutes
- Card ****5535: London, UK -> Mumbai, IN in 38.0 minutes

### 2. Card Testing Fraud
- **1 IPs** identified with rapid-fire small transactions
- Pattern: many sub-$5 charges in quick succession = testing stolen card numbers
- IP 10.132.241.173: 34 transactions/hour, avg $1.74

### 3. Employee Anomalies
- **2 suspicious employees** identified
- Average refund rate: 4.3% | Average discount: 7.7%
- Ghost refunds (no valid original transaction): 0

| Employee | Refund Rate | Avg Discount | Ghost Refunds | Suspicion Score |
|----------|------------|-------------|---------------|-----------------|
| EMP-007 | 3.8% | 13.8% | 0 | 5.0 |
| EMP-012 | 12.9% | 7.0% | 52 | 4.8 |
| EMP-021 | 1.4% | 7.4% | 0 | 1.7 |
| EMP-ONLINE | 3.9% | 6.1% | 0 | 1.4 |
| EMP-015 | 2.6% | 7.3% | 0 | 1.1 |
| EMP-005 | 2.9% | 7.4% | 0 | 0.9 |
| EMP-024 | 3.4% | 7.2% | 0 | 0.8 |
| EMP-014 | 5.4% | 7.4% | 0 | 0.8 |
| EMP-016 | 3.2% | 7.4% | 0 | 0.8 |
| EMP-018 | 2.9% | 7.7% | 0 | 0.7 |

### 4. Bot Traffic
- **168 transactions** with sub-1-second processing times
- **1 IPs** with suspiciously uniform processing patterns
- Human processing times cluster around 3-5 seconds; bots spike below 1 second

### 5. Price Glitches
- **2876 transactions** priced far below category norms
- Estimated revenue lost: **$330,705**

### 6. Data Corruption
- Negative item counts: 6
- Extreme outlier amounts: 2
- Future timestamps: 7

### 7. Discount Abuse
- **38 transactions** with discounts > 50%
- Estimated loss from unauthorized discounts: **$23,363**

### 8. Account Takeovers
- **594 customers** show signs of account compromise
- CUST-10005: SPENDING_SPIKE|DEVICE_CHANGE (spending $10.49 -> $116.86)
- CUST-10035: MULTI_NEW_CARDS|DEVICE_CHANGE|NEW_CITY (spending $46.94 -> $29.05)
- CUST-10039: SPENDING_SPIKE|NEW_CITY (spending $24.28 -> $243.74)
- CUST-10050: MULTI_NEW_CARDS|DEVICE_CHANGE (spending $82.6 -> $232.25)
- CUST-10062: DEVICE_CHANGE|NEW_CITY (spending $31.23 -> $335.84)

---

## Hotspot Analysis

### Peak Anomaly Hours
- 22:00 — 379 anomalies
- 0:00 — 330 anomalies
- 1:00 — 279 anomalies
- 2:00 — 271 anomalies
- 23:00 — 267 anomalies

### Top Anomaly Stores
- Online: 1437 anomalies
- Store-Downtown: 932 anomalies
- Store-Mall: 917 anomalies
- Store-Westside: 868 anomalies
- Store-North: 856 anomalies

---

## Top 50 Most Suspicious Transactions

| Rank | Transaction ID | Amount | Score | Flags |
|------|---------------|--------|-------|-------|
| 1 | TX-713664 | $28.21 | 100 | STOLEN_CARD|BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEO |
| 2 | TX-713773 | $12.00 | 78 | STOLEN_CARD|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 3 | TX-713785 | $12.00 | 78 | STOLEN_CARD|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 4 | TX-701329 | $32.99 | 78 | STOLEN_CARD|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 5 | TX-701956 | $15.06 | 78 | STOLEN_CARD|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 6 | TX-713505 | $2.00 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 7 | TX-713530 | $2.04 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 8 | TX-707117 | $23.88 | 68 | HIGH_REFUND_RATE|GHOST_REFUNDS|PRICE_GLITCH|ACCOUN |
| 9 | TX-713725 | $17.18 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 10 | TX-713657 | $29.32 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 11 | TX-705902 | $21.61 | 68 | HIGH_REFUND_RATE|GHOST_REFUNDS|PRICE_GLITCH|ACCOUN |
| 12 | TX-713679 | $25.48 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 13 | TX-713607 | $24.91 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 14 | TX-714076 | $134.66 | 68 | HIGH_DISCOUNT|DISCOUNT_ABUSE|ACCOUNT_TAKEOVER |
| 15 | TX-713508 | $1.38 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 16 | TX-713652 | $28.53 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 17 | TX-713714 | $36.74 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 18 | TX-704124 | $40.68 | 68 | HIGH_DISCOUNT|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 19 | TX-713700 | $32.21 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 20 | TX-713522 | $2.52 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 21 | TX-713711 | $23.72 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 22 | TX-713525 | $1.04 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 23 | TX-713524 | $2.22 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 24 | TX-714068 | $111.12 | 68 | HIGH_DISCOUNT|DISCOUNT_ABUSE|ACCOUNT_TAKEOVER |
| 25 | TX-713716 | $16.10 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 26 | TX-713624 | $23.79 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 27 | TX-713514 | $0.89 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 28 | TX-713612 | $15.90 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 29 | TX-713707 | $26.01 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 30 | TX-713513 | $2.09 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 31 | TX-713668 | $18.00 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 32 | TX-713528 | $0.83 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 33 | TX-713526 | $2.24 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 34 | TX-713708 | $18.15 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 35 | TX-713516 | $2.77 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 36 | TX-713674 | $28.50 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 37 | TX-713686 | $25.15 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 38 | TX-713533 | $1.46 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 39 | TX-702134 | $11.29 | 68 | HIGH_REFUND_RATE|GHOST_REFUNDS|PRICE_GLITCH|ACCOUN |
| 40 | TX-713642 | $25.49 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 41 | TX-714062 | $104.83 | 68 | HIGH_DISCOUNT|DISCOUNT_ABUSE|ACCOUNT_TAKEOVER |
| 42 | TX-713693 | $23.42 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 43 | TX-709708 | $17.36 | 68 | HIGH_DISCOUNT|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 44 | TX-713523 | $1.13 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 45 | TX-713510 | $2.06 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |
| 46 | TX-714077 | $126.92 | 68 | HIGH_DISCOUNT|DISCOUNT_ABUSE|ACCOUNT_TAKEOVER |
| 47 | TX-704696 | $30.69 | 68 | HIGH_REFUND_RATE|GHOST_REFUNDS|PRICE_GLITCH|ACCOUN |
| 48 | TX-713655 | $40.56 | 68 | BOT_TRAFFIC|PRICE_GLITCH|ACCOUNT_TAKEOVER |
| 49 | TX-714066 | $140.15 | 68 | HIGH_DISCOUNT|DISCOUNT_ABUSE|ACCOUNT_TAKEOVER |
| 50 | TX-713512 | $1.03 | 68 | CARD_TESTING|BOT_TRAFFIC|PRICE_GLITCH |

---

## Detection Accuracy (vs Ground Truth)

| Anomaly Type | Total Planted | Detected | Missed | Recall |
|-------------|--------------|----------|--------|--------|
| price_glitch | 294 | 294 | 0 | 100% |
| bot_traffic | 134 | 134 | 0 | 100% |
| round_number_fraud | 60 | 60 | 0 | 100% |
| employee_refund_fraud | 52 | 52 | 0 | 100% |
| discount_abuse | 38 | 38 | 0 | 100% |
| card_testing_fraud | 34 | 34 | 0 | 100% |
| data_entry_error | 20 | 18 | 2 | 90% |
| account_takeover | 17 | 17 | 0 | 100% |
| stolen_card | 8 | 8 | 0 | 100% |

| **OVERALL** | **657** | **655** | **2** | **100%** |

Precision: **11%** (of flagged transactions, how many were actual anomalies)

---

## 5 Immediate Actions

1. **Block stolen cards** — Immediately flag cards ****4487, ****8335, ****7960 and investigate recent charges
2. **Investigate EMP-007** — This employee has the highest anomaly suspicion score; review their transaction history and refund authorization
3. **Rate-limit card testing IPs** — Implement velocity checks: block IPs with >10 sub-$5 transactions per hour
4. **Fix price glitch vulnerability** — 2876 transactions exploited pricing errors; audit product price validation
5. **Add bot detection** — 168 transactions processed in <1 second; add CAPTCHA or processing time floor

---

## Summary

| Metric | Value |
|--------|-------|
| Total Transactions | 14,157 |
| Anomalies Detected | 5,901 |
| Financial Impact | $4,604,948 |
| Fraud Rate | 41.7% |
| Most Dangerous Type | data_entry_error |
| Highest Risk Employee | EMP-007 |
| Detection Recall | 100% |
| Detection Precision | 11% |
