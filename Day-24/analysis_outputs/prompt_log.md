# Prompt Log

---

## Step 4 — 2026-04-16
**Prompt summary:** Build interactive HTML dashboard from stored analysis memory.

**Action taken:**
- Read all three memory files (insights_registry.md, dashboard_data.json, prompt_log.md)
- Generated standalone dashboard.html at output/dashboard.html
- Dashboard includes: KPI cards, 4 Chart.js charts, leakage audit table, segment analysis table, 8 insight cards
- All data sourced directly from dashboard_data.json and insights_registry.md — no re-analysis needed

**Files updated:**
- `output/dashboard.html` — created (standalone, no server required)
- `prompt_log.md` — this entry

**Result summary:**
Dashboard covers: label balance KPIs, duplicate content rate, leakage column count, source distribution chart, word count by group chart, complexity score randomness chart, full leakage audit table, segment analysis table, and all 8 confirmed insights from memory.

---

## Step 3 — 2026-04-16
**Prompt summary:** Leakage detection — is this real intelligence or a shortcut?

**Action taken:**
- Scanned all columns for label leakage
- Checked `content` for explicit AI string markers
- Checked `ai_model` null pattern
- Checked `source` correlation (already known)
- Checked prompt phrasing for systematic differences
- Checked language keywords in prompts

**Files updated:**
- `insights_registry.md` — Insights 8, 9, 10 added (dataset-breaking leakage findings)
- `dashboard_data.json` — leakage_audit section added
- `prompt_log.md` — this entry

**Result summary:**
THREE independent columns achieve 100% label prediction: source, ai_model, content text marker.
The string "AI-generated" is literally embedded in 100% of AI content rows.
This dataset cannot support genuine AI detection analysis — every signal is a metadata shortcut.
Only `prompt` first-verb is clean (no leakage). Complexity score is random noise.

---

## Step 2 — 2026-04-16
**Prompt summary:** Structured vs unstructured content analysis — do all AI outputs behave the same?

**Action taken:**
- Segmented dataset into 4 groups: code_human, code_ai, text_human, text_ai
- Compared word count, char count, complexity score, multiline flag, language, topic per group
- Validated findings against Step 1 memory before storing

**Files updated:**
- `insights_registry.md` — Insight 4 updated (confirmed, not provisional); Insights 6 and 7 added
- `dashboard_data.json` — segment_analysis section populated
- `prompt_log.md` — this entry

**Result summary:**
AI does NOT behave uniformly. Code AI is measurably more verbose than human code. Text AI is indistinguishable from human text on all surface metrics. Complexity score is uniform random noise across all groups — confirmed useless.

---

## Step 1 — 2026-04-16
**Prompt summary:** Data quality check — should we trust human vs AI comparison immediately?

**Action taken:**
- Inspected full dataset (20,000 rows, 13 columns)
- Computed label distribution, source distribution, source×label cross, type×label cross
- Checked missing values, duplicate content, complexity scores, word counts
- Initialized all three memory files

**Files updated:**
- `insights_registry.md` — 5 validated insights written
- `dashboard_data.json` — KPIs, category comparisons, distributions, outliers populated
- `prompt_log.md` — this entry

**Result summary:**
Dataset has 3 critical data quality issues:
1. Source perfectly predicts label (no real detection challenge if source is used)
2. 58.8% duplicate content (mostly templated code)
3. Complexity score is identical for human vs AI (not a useful signal)

Word count shows a small difference but it is type-driven, not style-driven.
Next step should be: type-controlled comparison of human vs AI within code and text separately.
