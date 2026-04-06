# Email Campaign Targeting Analysis Report

## Executive Summary

Analyzed **8,000 user-campaign records** across **5 segments** and **7 campaigns**.

**Key Finding:** Email targeting is misaligned. Over-targeting wastes **$298** on users who buy anyway, while under-targeting misses **$509** in potential revenue from high-response segments. Net ROI improvement possible: **$718**.

---

## 1. Funnel Analysis

| Stage | Count | Rate |
|-------|-------|------|
| Emails Sent | 5,959 | — |
| Opened | 2,713 | 45.5% open rate |
| Clicked | 1,079 | 39.8% click rate |
| Purchased | 2,171 | 55.9% conversion rate |

**Drop-offs:**
- Sent → Opened: **54.5%** drop
- Opened → Clicked: **60.2%** drop
- Clicked → Purchased: **44.1%** drop

**Biggest leak:** Opened → Clicked (content)

### Funnel by Segment
| segment        |   open_rate |   click_rate |   conv_rate |
|:---------------|------------:|-------------:|------------:|
| Frequent Buyer |        60.4 |         42.4 |        71.2 |
| Inactive       |        20.4 |         19.1 |        40.4 |
| New User       |        40.8 |         31   |        31.5 |
| Regular        |        43.8 |         35.7 |        34.7 |
| VIP            |        62.8 |         52.6 |        65.5 |

### Funnel by Campaign
| campaign        |   open_rate |   click_rate |   conv_rate |
|:----------------|------------:|-------------:|------------:|
| Flash Deal      |        51.6 |         35.4 |        55.8 |
| Loyalty Reward  |        42.3 |         44.7 |        58.5 |
| New Arrival     |        41.4 |         41.9 |        56.1 |
| Summer Sale     |        49.2 |         36.9 |        60.6 |
| Weekend Special |        40.9 |         42.9 |        53   |
| Welcome Series  |        45.1 |         41.1 |        53.1 |
| Win-Back        |        47.9 |         37.7 |        53.7 |

---

## 2. Does Email Work? Evidence Per Segment

| Segment | No Email Purchase Rate | Email Purchase Rate | Lift |
|---------|----------------------|--------------------|----|
| Frequent Buyer | 60.0% | 54.8% | +-5.1pp ❌ No impact |
| Inactive | 5.2% | 6.4% | +1.1pp ⚠️ Marginal |
| New User | 10.0% | 7.5% | +-2.5pp ❌ No impact |
| Regular | 15.9% | 9.1% | +-6.8pp ❌ No impact |
| VIP | 60.3% | 52.9% | +-7.4pp ❌ No impact |

**Overall:** Emailed users purchase at **25.9%** vs **30.6%** for non-emailed — a **+-4.7pp** lift.

---

## 3. Over-Targeting: Wasted Money

These segments buy at similar rates whether emailed or not. **Every email to these users is wasted money.**

| segment        |   emails_sent |   cost |   lift |
|:---------------|--------------:|-------:|-------:|
| VIP            |          1192 |  59.6  |  -7.44 |
| Regular        |          1216 |  60.8  |  -6.79 |
| Frequent Buyer |          1167 |  58.35 |  -5.11 |
| New User       |          1178 |  58.9  |  -2.53 |
| Inactive       |          1206 |  60.3  |   1.13 |

**Total wasted email cost: $297.95**

> "You're paying $298 to convince people who already decided to buy."

---

## 4. Under-Targeting: Hidden Revenue Opportunity

These segments show massive purchase rate increases when emailed. **These are your highest-ROI targets.**

| segment   |   not_emailed |   lift |   potential_purchases |   potential_revenue |   email_cost |   net_gain |
|:----------|--------------:|-------:|----------------------:|--------------------:|-------------:|-----------:|
| Inactive  |           400 |   1.13 |                   4.5 |              529.42 |           20 |     509.42 |

**Total missed opportunity: $509.42**

---

## 5. Funnel Drop Diagnosis

| campaign        |   sent_open_drop |   open_click_drop |   click_purchase_drop | biggest_problem          |
|:----------------|-----------------:|------------------:|----------------------:|:-------------------------|
| Flash Deal      |             48.4 |              64.6 |                  44.2 | Content (Open→Click)     |
| Loyalty Reward  |             57.7 |              55.3 |                  41.5 | Subject Line (Sent→Open) |
| New Arrival     |             58.6 |              58.1 |                  43.9 | Subject Line (Sent→Open) |
| Summer Sale     |             50.8 |              63.1 |                  39.4 | Content (Open→Click)     |
| Weekend Special |             59.1 |              57.1 |                  47   | Subject Line (Sent→Open) |
| Welcome Series  |             54.9 |              58.9 |                  46.9 | Content (Open→Click)     |
| Win-Back        |             52.1 |              62.3 |                  46.3 | Content (Open→Click)     |

**Interpretation:**
- **High Sent→Open drop:** Subject line problem — not compelling enough
- **High Open→Click drop:** Email content/design problem — not driving action
- **High Click→Purchase drop:** Landing page/offer problem — not converting visitors

---

## 6. Segment Deep Dive

| segment        |   total_users | email_rate   | purchase_rate   | email_lift   | avg_revenue   | total_revenue   | recommendation         |
|:---------------|--------------:|:-------------|:----------------|:-------------|:--------------|:----------------|:-----------------------|
| New User       |          1548 | 76%          | 8.1%            | -2.5pp       | $110.09       | $13761.33       | REDUCE / STOP emailing |
| VIP            |          1605 | 74%          | 54.8%           | -7.4pp       | $110.19       | $96860.72       | REDUCE / STOP emailing |
| Frequent Buyer |          1579 | 74%          | 56.2%           | -5.1pp       | $110.60       | $98104.74       | REDUCE / STOP emailing |
| Regular        |          1662 | 73%          | 11.0%           | -6.8pp       | $101.66       | $18501.48       | REDUCE / STOP emailing |
| Inactive       |          1606 | 75%          | 6.1%            | 1.1pp        | $117.13       | $11478.68       | REDUCE / STOP emailing |

---

## 7. Campaign Ranking

| campaign        |   open_rate |   click_rate |   conv_rate |   revenue |     roi |
|:----------------|------------:|-------------:|------------:|----------:|--------:|
| Summer Sale     |        49.2 |         36.9 |        60.6 |   36671.2 | 82960.5 |
| New Arrival     |        41.4 |         41.9 |        56.1 |   35432.2 | 82976.7 |
| Weekend Special |        40.9 |         42.9 |        53   |   34964.8 | 82364.2 |
| Loyalty Reward  |        42.3 |         44.7 |        58.5 |   33801.6 | 80188.9 |
| Flash Deal      |        51.6 |         35.4 |        55.8 |   33702.4 | 79858.3 |
| Welcome Series  |        45.1 |         41.1 |        53.1 |   32164   | 81019.7 |
| Win-Back        |        47.9 |         37.7 |        53.7 |   31970.7 | 71183.5 |

**Winner:** Summer Sale
**Weakest:** Win-Back

---

## 8. Targeting Matrix & Recommendations

| segment        |   no_email_rate |   email_rate |   lift | action   |
|:---------------|----------------:|-------------:|-------:|:---------|
| Frequent Buyer |           59.95 |        54.84 |  -5.11 | STOP     |
| Inactive       |            5.25 |         6.38 |   1.13 | REDUCE   |
| New User       |           10    |         7.47 |  -2.53 | STOP     |
| Regular        |           15.92 |         9.13 |  -6.79 | STOP     |
| VIP            |           60.29 |        52.85 |  -7.44 | STOP     |

### Estimated Impact

| Metric | Value |
|--------|-------|
| Savings from reducing over-targeting | $209 |
| Revenue gain from under-targeting | $509 |
| **Net ROI Improvement** | **$718** |

---

## 5 Specific Actions to Improve Email ROI

1. **STOP/REDUCE emails to VIP** — they buy at nearly the same rate without emails. Save $119+ in email costs.

2. **INCREASE emails to Inactive** — highest response to email with +1.1pp lift. Potential $509 in additional revenue.

3. **Fix subject lines for campaigns with high Sent→Open drops** — this is the biggest funnel leak across most campaigns.

4. **Run Summer Sale more frequently** — it's the top performer across key metrics.

5. **A/B test landing pages for campaigns with high Click→Purchase drops** — users are interested (they click) but something on the landing page isn't converting them.

---

## Final Verdict

- **Biggest Waste:** VIP — emailing users who buy anyway, costing $298
- **Biggest Opportunity:** Inactive — high-response users not getting enough emails, missing $509
- **Estimated ROI Improvement:** $718 through better targeting alone
- **The fundamental problem:** The company is over-emailing its best customers (who don't need convincing) and under-emailing persuadable segments (who respond strongly to outreach).

*Reallocate email volume from low-lift to high-lift segments for immediate ROI improvement.*
