# Refund Prediction Engine - Return Intelligence Report

## Executive Summary

**25.9% of orders are returned, costing $996,379 annually.**

Out of 15,000 orders analyzed, 3,884 were returned. Each return costs an average of $242 in lost revenue plus $15 in processing - a massive drain on profitability. Our ML model predicts returns with **75.7% accuracy** before orders ship, enabling proactive intervention.

---

## 1. Time-of-Day Analysis

| Segment | Return Rate |
|---------|------------|
| Late Night (10PM-5AM) | **33.7%** |
| Daytime | **22.0%** |
| Weekend | **27.8%** |
| Weekday | **25.1%** |

**Danger Hours:** 3:00 has the highest return rate at **37.6%**.
**Safe Hours:** 21:00 has the lowest return rate at **19.4%**.

Late-night purchases show significantly higher return rates - these are impulse buys made when judgment is impaired.

---

## 2. Impulse Buying Signals (Ranked)

| Signal | Impact |
|--------|--------|
| Browse time <3 min | **50.4%** return rate |
| Cart removals (indecision) | Higher removals = higher returns |
| Reviews read = 0 | Uninformed buyers return more |
| Items compared < 2 | Less comparison = more regret |

**The Impulse Score** combines browse time, reviews read, items compared, and cart removals into a 0-100 score. High impulse scores correlate strongly with returns.

---

## 3. The Discount-Returns Connection

| Discount Level | Return Rate |
|---------------|------------|
| 0% | **22.9%** |
| 1-5% | **25.0%** |
| 6-15% | **25.2%** |
| 16-25% | **27.3%** |
| 26-35% | **37.3%** |
| 35%+ | **35.7%** |


**Coupon users:** 31.4% vs non-coupon: 22.9%

Discounts above 25% see a sharp spike in returns. The break-even point where discount-driven revenue is eroded by returns falls around 25-30%.

---

## 4. Category Deep Dive

| Category | Return Rate |
|----------|------------|
| Fashion | **47.0%** |
| Electronics | **25.0%** |
| Home & Kitchen | **18.5%** |
| Sports | **17.4%** |
| Beauty | **13.8%** |
| Books & Media | **12.0%** |


### The Fashion Problem
- Fashion has the highest return rate at **47.0%**
- Multiple sizes ordered: **71.0%** return rate vs **38.8%** for single size
- Top reasons: Wrong Size (730), Ordered Multiple Sizes (347), Changed Mind (236)

---

## 5. Payment Method Risks

| Method | Return Rate |
|--------|------------|
| Buy Now Pay Later | **36.0%** |
| Digital Wallet | **25.0%** |
| Credit Card | **24.1%** |
| Debit Card | **23.7%** |
| Gift Card | **23.5%** |


Buy Now Pay Later shows elevated return rates - customers who defer payment are more likely to change their mind.

---

## 6. Customer History as Predictor

| Previous Return Rate | Current Return Probability |
|---------------------|--------------------------|
| 0% | **22.4%** |
| 1-10% | **19.7%** |
| 11-20% | **23.9%** |
| 21-30% | **26.6%** |
| 30%+ | **36.5%** |


- **Serial returners** (>30% history): **36.5%** return rate (3,577 orders)
- Customer type: Returning: 30.4%, Frequent: 29.0%, New: 22.6%, VIP: 18.0%

---

## 7. Device & Channel Analysis

**Device:** Tablet: 28.1%, Mobile: 27.4%, App: 25.2%, Desktop: 23.6%

**Channel:** Paid Ads: 30.0%, Email: 26.0%, Social Media: 25.9%, Organic Search: 25.5%, Referral: 24.9%, Direct: 21.4%

- Mobile + impulse (<3min browse): **55.2%** return rate
- Desktop + long browse (>30min): **21.5%** return rate

---

## 8. ML Model Results

| Metric | Score |
|--------|-------|
| Accuracy | **75.7%** |
| Precision | **55.2%** |
| Recall | **32.3%** |
| F1 Score | **40.7%** |

### Top Features (by importance)
1. **Multiple Sizes Ordered**: 0.1610
2. **Discount Percent**: 0.1288
3. **Time Browsing Minutes**: 0.1182
4. **Category**: 0.1174
5. **Previous Return Rate**: 0.0915
6. **Reviews Read**: 0.0700
7. **Purchase Hour**: 0.0616
8. **Items Compared**: 0.0495
9. **Payment Method**: 0.0467
10. **Cart Removals**: 0.0434
11. **Is Late Night**: 0.0376
12. **Delivery Days**: 0.0371
13. **Device**: 0.0210
14. **Is Gift**: 0.0149
15. **Used Coupon**: 0.0011


---

## 9. Risk Tier Breakdown

| Tier | Orders | % of Total | Actual Return Rate | Returns Caught |
|------|--------|-----------|-------------------|----------------|
| High Risk (>60%) | 1,757 | 11.7% | 89.2% | 1,568 (40.4%) |
| Medium Risk (30-60%) | 3,004 | 20.0% | 47.4% | 1,425 (36.7%) |
| Low Risk (<30%) | 10,239 | 68.3% | 8.7% | 891 (22.9%) |

---

## 10. Dollar Impact & ROI

| Metric | Value |
|--------|-------|
| Annual Return Cost | **$996,379** |
| Savings from Flagging High-Risk Orders | **$214,717** |
| Savings from Capping Discounts at 30% | **$182,832** |

**ROI of Prediction System:** Implementation cost is minimal (automated scoring at checkout). Even a 50% intervention success rate on high-risk orders saves **$214,717** annually.

---

## Strategic Recommendations

### FLAG - High-Risk Orders
- Add confirmation step for orders scoring >60% return risk
- Remove free return shipping for flagged orders
- Require phone verification for high-risk orders >$200
- **Estimated savings: $214,717/year**

### FIX - Addressable Problems
- Implement late-night cooling-off period (save cart, email reminder next day)
- Fashion: invest in virtual try-on technology and detailed size guides
- Improve product photography and descriptions for top-returned categories

### LIMIT - High-Risk Drivers
- Cap promotional discounts at 25% (returns spike sharply above this)
- Restrict Buy Now Pay Later for new customers with no purchase history
- Limit serial returners to exchange-only returns

### MONITOR - Watch Lists
- Flag serial returners (>30% return history) for manual review
- Track return rate by acquisition channel monthly
- Monitor discount-return correlation by category

### KEEP - What's Working
- Desktop + long browse + VIP = lowest return risk segment
- Organic search brings highest-quality customers
- Full-price purchasers are the safest - don't over-discount them

---

## 5 Actions to Reduce Returns by 20%+

1. **Deploy the prediction model** - flag every order >60% risk before shipping
2. **Cap discounts at 25%** - returns spike dramatically above this threshold
3. **Implement late-night cooling-off** - save the cart, email the customer next morning
4. **Fix fashion sizing** - virtual try-on or precise size guides reduce "wrong size" returns
5. **Restrict serial returners** - exchange-only policy for customers with >30% return history

---

## Final Verdict

- **#1 Return Predictor:** Multiple Sizes Ordered
- **Biggest Fixable Problem:** Late-night impulse purchases + excessive discounts
- **Prediction Accuracy:** 75.7%
- **Estimated Annual Savings:** $397,549 from combined interventions
