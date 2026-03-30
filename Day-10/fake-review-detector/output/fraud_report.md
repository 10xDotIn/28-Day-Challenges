# Fake Review Investigation Report

**Date:** 2026-03-27
**Dataset:** data/hotel_reviews.csv

---

## Executive Summary

A total of **35,912 hotel reviews** were analysed across multiple properties.
Automated fraud signals reveal significant manipulation activity, with
**8,526 reviews (23.7%)** showing at least one suspicious
characteristic and **71 reviews (0.2%)** classified
as *Likely Fake*.

The dominant fraud pattern is **Behavior**, suggesting systematic review
manipulation via behavior-based tactics.

---

## Totals

| Category | Count | % |
|---|---|---|
| Total Analysed | 35,912 | 100% |
| Genuine (0–20) | 27,386 | 76.3% |
| Low Suspicion (21–40) | 5,936 | 16.5% |
| Moderate Suspicion (41–60) | 1,972 | 5.5% |
| High Suspicion (61–80) | 547 | 1.5% |
| Likely Fake (81–100) | 71 | 0.2% |

---

## Top 10 Most Suspicious Reviews

### #1 — Score: 100/100
**Hotel:** Harrah's Laughlin Hotel and Casino  **Rating:** 5.0
**Signals:** Extreme, Timing, Behavior, Length, Vague, Duplicate
**Text:** _Great gataway !_

### #2 — Score: 100/100
**Hotel:** Fiesta Inn and Suites  **Rating:** 1.0
**Signals:** Extreme, Timing, Behavior, Length, Vague, Duplicate
**Text:** _Worst place I have ever been. That hotel should be demolished!_

### #3 — Score: 100/100
**Hotel:** Drury Inn and Suites Columbus Convention Center  **Rating:** 5.0
**Signals:** Extreme, Exclamation, Behavior, Length, Vague, Duplicate
**Text:** _awesome hospitality!!! the best place in town!!! safe and close to everything!!!_

### #4 — Score: 100/100
**Hotel:** Drury Inn and Suites Columbus Convention Center  **Rating:** 5.0
**Signals:** Extreme, Exclamation, Behavior, Length, Vague, Duplicate
**Text:** _Awesome hospitality!!! The best place in town!!! Safe and close to everything!!!_

### #5 — Score: 95/100
**Hotel:** Springhill Suites Columbia  **Rating:** 5.0
**Signals:** Extreme, Behavior, Length, Vague, Duplicate
**Text:** _Their best employee is Jisselle in the evenings. She is so wonderful_

### #6 — Score: 95/100
**Hotel:** Springhill Suites Columbia  **Rating:** 5.0
**Signals:** Extreme, Behavior, Length, Vague, Duplicate
**Text:** _their best employee is jisselle in the evenings. she is so wonderful_

### #7 — Score: 95/100
**Hotel:** Americas Best Value Inn  **Rating:** 1.0
**Signals:** Extreme, Exclamation, Behavior, Length, Vague, Duplicate
**Text:** _Horrible!!!!_

### #8 — Score: 95/100
**Hotel:** Ip Casino Resort Spa  **Rating:** 5.0
**Signals:** Extreme, Exclamation, Behavior, Length, Vague, Duplicate
**Text:** _one of the best places in the gulf!!!_

### #9 — Score: 95/100
**Hotel:** Bayside Resort Hotel  **Rating:** 5.0
**Signals:** Extreme, Exclamation, Behavior, Length, Vague, Duplicate
**Text:** _Great hotel for the price, very clean! Recommend!!_

### #10 — Score: 95/100
**Hotel:** Quality Inn Long Beach Airport  **Rating:** 5.0
**Signals:** Extreme, Exclamation, Behavior, Length, Vague, Duplicate
**Text:** _It was great !!! Loved it...._

---

## Most Suspicious Hotels

| Hotel | Total Reviews | Flagged | % Flagged | Mean Score |
|---|---|---|---|---|
| Advance Motel | 1 | 1 | 100.0% | 45.0 |
| Holiday Inn & Suites Green Bay Stadium | 28 | 28 | 100.0% | 46.1 |
| Holiday Inn Express & Suites Willows | 1 | 1 | 100.0% | 35.0 |
| Grandison Bed Breakfast | 1 | 1 | 100.0% | 30.0 |
| Extended Stay America Princeton - West W | 2 | 2 | 100.0% | 70.0 |
| Enchanted Castle Hotel | 3 | 3 | 100.0% | 48.3 |
| Glendale Gaslight Inn | 2 | 2 | 100.0% | 25.0 |
| Fairfield Inn/suites-marriott | 1 | 1 | 100.0% | 35.0 |
| Best Western | 7 | 7 | 100.0% | 33.6 |
| Homewood Suites By Hilton | 12 | 12 | 100.0% | 42.5 |

---

## Duplicate Clusters Found

**Cluster 0** (2 reviews):
> _We stayed here for four nights in October. The hotel staff were welcoming, friendly and helpful. Assisted in booking tickets for the opera. The rooms were clean and comfortable- good shower, light and..._

**Cluster 1** (6 reviews):
> _Hotellihuone oli ullakolla, jossa ei pystynyt kvelemn suorassa. Huonekorkeus oli suurimmassa osassa n. 1,5m. Huoneestamme varastettiin rannekoru ja neuletakki. Lisksi Spa ei ollut hotellissa vaan n. k..._

**Cluster 2** (16 reviews):
> _Nyrenovert bad hevet opplevelsen...._

**Cluster 3** (199 reviews):
> _to share your opinion of this businesswith YP visitors across the United Statesand in your neighborhood..._

**Cluster 4** (105 reviews):
> _xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx..._

**Cluster 5** (169 reviews):
> _Great..._

**Cluster 6** (11 reviews):
> _Very nice for the price...._

**Cluster 7** (3 reviews):
> _Visiting family..._

**Cluster 8** (50 reviews):
> _Excellent Staff..._

**Cluster 9** (2 reviews):
> _This was a fine, clean hotel. Good-sized pool and exercise room. Rooms were clean, check-in was easy. Good breakfast with waffles, eggs, bacon, yogurt, muffins, etc., etc...._


---

## Timing Bursts Detected

| Hotel | Date | Reviews in Day |
|---|---|---|
| Homewood Suites Dallas-market Center | 2016-11-08 | 12 |
| Hampton Inn Virginia Beach Oceanfront No | 2016-02-03 | 11 |
| Bailey House Bed & Breakfast | 2010-11-30 | 10 |
| Plaza Hotel and Casino - Las Vegas | 2016-07-24 | 8 |
| Ip Casino Resort Spa | 2013-01-07 | 8 |
| Blue Boar Inn | 2015-05-19 | 7 |
| Beach Cove 411 Tower A Sierra's 1 Bedroo | 2013-06-28 | 7 |
| Hampton Inn Virginia Beach Oceanfront No | 2016-02-17 | 7 |
| Plaza Hotel and Casino - Las Vegas | 2016-07-01 | 7 |
| Holiday Inn Fond Du Lac | 2016-02-08 | 7 |

---

## Genuine vs Suspicious Language

**Genuine reviews** tend to use specific, contextual language — mentioning
exact amenities, locations, and staff interactions with moderate sentiment.

**Suspicious reviews** are characterised by vague superlatives (*amazing*,
*perfect*, *worst ever*), extreme polarity, and repetitive phrasing — often
recycled across multiple properties by the same user.

---

## Recommendations

1. **Rate-limit reviews per user per day** — cap at 3 to prevent burst campaigns.
2. **Flag vague-only reviews for manual moderation** before publishing.
3. **Cluster near-duplicate text** across the platform and auto-suppress repeats.
4. **Track reviewer rating entropy** — one-sided reviewers should be shadow-flagged.
5. **Introduce verified stay confirmation** before allowing 5-star reviews.

---

## Verdict

The dataset shows **widespread manipulation**. The Behavior signal alone
accounts for 20,867 flagged reviews. Hotels with suspiciously
high five-star concentrations represent coordinated rating inflation.
Platform trust requires immediate algorithmic intervention.

---
*Generated by detector.py — Fake Review Detector*
