# Insights Registry

---

## Insight 1: Source Column Perfectly Predicts Label — No Real Detection Challenge
**What was found:**
`source` and `label` have a 100% deterministic relationship:
- `generated` source → always `ai` (10,004 rows)
- `blog`, `news`, `github` sources → always `human` (9,996 rows)

**Evidence basis:** Cross-tabulation of source × label across all 20,000 rows.

**Why it matters:**
Any model or analysis that includes `source` as a feature will trivially "detect" AI vs human. The detection problem is artificially easy. Real-world detection cannot rely on source metadata.

**Status: Confirmed**

---

## Insight 2: Massive Content Duplication — 58.8% of Rows Are Duplicates
**What was found:**
11,758 out of 20,000 rows share duplicate content with at least one other row.
Top repeated content are identical Java/C++ class skeletons (e.g., `public class graph_traversal`) repeated 340–360 times each.

**Evidence basis:** `len(set(content)) vs len(content)` check across all rows.

**Why it matters:**
The dataset is largely synthetic/templated. Patterns learned from it may reflect template repetition, not genuine human vs AI writing style. Any insight derived from content features should be treated with caution.

**Status: Confirmed**

---

## Insight 3: Complexity Score Is Not a Useful Differentiator
**What was found:**
Mean complexity score is virtually identical across labels:
- Human: mean = 5.50, median = 6.0
- AI: mean = 5.51, median = 6.0

**Evidence basis:** Per-label aggregation of `complexity_score`.

**Why it matters:**
`complexity_score` cannot be used to distinguish human from AI content in this dataset. It may have been assigned by the same synthetic generation process for both groups.

**Status: Confirmed**

---

## Insight 4: Word Count Signal Exists Only in Code, Not in Text
**What was found:**
Type-controlled comparison reveals a split behavior:
- **Code** — AI is consistently longer: human mean=12.0 vs AI mean=14.1 words; human median=11 vs AI median=13
- **Text** — virtually identical: human mean=43.2 vs AI mean=44.0; medians 44 vs 43

The overall word count difference (Insight 4 original) was entirely driven by the code segment. Text AI outputs are indistinguishable from human text by word count alone.

**Evidence basis:** Per-(type × label) aggregation of `word_count` across all 20,000 rows.

**Why it matters:**
AI-generated code tends to be more verbose than human code snippets. But for prose/text, AI and human output lengths converge completely. Word count is only a partial signal, not a universal one.

**Status: Confirmed (replaces provisional finding)**

---

## Insight 6: Complexity Score Is Randomly Assigned — Not Computed
**What was found:**
Complexity score is uniformly distributed across 1–10 in ALL four groups (code_human, code_ai, text_human, text_ai). Each value appears roughly ~490–552 times per group with no meaningful skew.

**Evidence basis:** Full distribution of `complexity_score` per group shows flat uniform distribution.

**Why it matters:**
A real complexity score computed from content would cluster differently for code vs text, and for simple vs complex content. A perfectly flat uniform distribution means this column was randomly assigned. It is noise and should be excluded from any analysis.

**Status: Confirmed**

---

## Insight 7: AI Does NOT Behave the Same Across Structured vs Unstructured Content
**What was found:**
- In **code (structured)**: AI outputs are measurably longer than human (word count +2.1, char count +15) — a detectable signal
- In **text (unstructured)**: AI outputs are virtually identical to human on word count, char count, complexity, and topic distribution — no detectable signal on these metrics

**Evidence basis:** Type-controlled comparison of all numeric metrics across 4 groups.

**Why it matters:**
There is no single "AI behavior." Structured AI output (code) has a measurable verbosity pattern vs human. Unstructured AI output (text) is indistinguishable on surface metrics. Detection strategies must differ by content type.

**Status: Confirmed**

---

## Insight 8: CRITICAL LEAKAGE — "AI-generated" String Embedded in 100% of AI Content
**What was found:**
Every single AI-labeled row contains the literal string `"AI-generated"` inside the `content` column:
- Text AI rows: end with `(AI-generated)` — 5,067 rows
- Code AI rows: end with `# AI-generated` comment — 4,937 rows
- Human rows: zero occurrences of any AI marker

A single `str.contains("AI-generated")` check achieves 100% label accuracy.

**Evidence basis:** String match across all 20,000 rows.

**Why it matters:**
This is the most severe form of data leakage possible. The label is not inferred — it is literally written into the content. Any analysis, model, or comparison using the `content` column is measuring this marker, not real AI vs human writing behavior.

**Status: Confirmed — dataset-breaking**

---

## Insight 9: CRITICAL LEAKAGE — ai_model Column Is 100% Predictive
**What was found:**
- All 9,996 human rows: `ai_model` is blank
- All 10,004 AI rows: `ai_model` is filled (Claude / GPT-4 / Gemini)

**Evidence basis:** Null check on `ai_model` per label across all rows.

**Why it matters:**
This is a second independent 100% leakage column. Any analysis including `ai_model` trivially identifies the label.

**Status: Confirmed — dataset-breaking**

---

## Insight 10: Leakage Summary — Three Columns Each Achieve 100% Label Prediction
**What was found:**
Three columns independently achieve 100% accuracy at predicting `label`:
1. `source` — `generated` = ai, everything else = human
2. `ai_model` — blank = human, filled = ai
3. `content` — contains `"AI-generated"` string = ai, never in human rows

Prompt phrasing (first verb) shows NO meaningful difference — same verbs used proportionally for both labels. This is one of the few clean columns.

**Evidence basis:** Exhaustive per-column leakage scan across all 20,000 rows.

**Why it matters:**
This dataset has no analytical integrity for AI detection. Every signal that "works" is a metadata shortcut, not intelligence. The content itself carries an explicit label. Any finding claiming high detection accuracy on this data is meaningless.

**Status: Confirmed — dataset-breaking**

---

## Insight 5: Dataset Is Artificially Balanced
**What was found:**
- Human rows: 9,996
- AI rows: 10,004
- Near-perfect 50/50 split

**Evidence basis:** Label count across all rows.

**Why it matters:**
Real-world AI detection datasets are typically imbalanced. This balance is engineered, meaning performance metrics on this data will not reflect real deployment conditions.

**Status: Confirmed**
