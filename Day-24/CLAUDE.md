# CLAUDE.md

## Objective

Analyze `dataset.csv` using a memory-driven agentic workflow.

The analysis must:

* inspect and understand the dataset
* identify meaningful patterns
* store validated findings in persistent memory
* reuse previous findings in later steps
* prepare clean structured outputs for dashboard creation

This workflow is analysis-first.
Do not train predictive models unless explicitly requested.

---

## Working Context

Expected project structure:

project/
├── CLAUDE.md
├── dataset.csv
└── analysis_outputs/
├── insights_registry.md
├── dashboard_data.json
└── prompt_log.md

---

## Core Principle

Do not treat each prompt as isolated.

Operate with memory.

That means:

1. analyze the current request
2. check previously stored findings
3. update memory with validated results
4. refine later analysis using stored context

---

## Memory Files

### 1. `analysis_outputs/insights_registry.md`

Purpose:

* store validated findings
* store important patterns
* store contradictions, caveats, and confirmed observations

Rules:

* only add findings that are supported by data
* write each insight clearly and concisely
* avoid duplicate or weak insights
* if a previous insight is contradicted by new evidence, update it

Suggested entry structure:

* Insight Title
* What was found
* Evidence basis
* Why it matters
* Status: confirmed / provisional

---

### 2. `analysis_outputs/dashboard_data.json`

Purpose:

* store structured, chart-ready data
* act as the source of truth for dashboard generation
* keep aggregated data clean and visualization-friendly

Rules:

* only store structured data
* do not store narrative paragraphs here
* use clear keys and labels
* update existing sections instead of creating messy duplicates
* keep data normalized and dashboard-ready

Typical contents may include:

* KPI summaries
* grouped comparisons
* counts by category
* averages and medians
* trend tables
* segment summaries

---

### 3. `analysis_outputs/prompt_log.md`

Purpose:

* store a running log of analysis steps
* track which prompt was executed
* record what was updated

For every meaningful prompt, append:

* timestamp or sequence number
* prompt summary
* action taken
* files updated
* short result summary

---

## File Handling Rules

* Use `dataset.csv` as the primary dataset unless specified otherwise.
* Use `analysis_outputs/` for all persistent memory.
* If `analysis_outputs/` does not exist, create it.
* If `insights_registry.md` does not exist, create it with a clean initial structure.
* If `dashboard_data.json` does not exist, create it with a clean initial JSON structure.
* If `prompt_log.md` does not exist, create it with a clean initial log header.
* If memory files already exist, read and reuse them before performing new analysis.
* Never overwrite useful information blindly; update or append intelligently.
* Never leave important findings only in chat output.
* Every meaningful analysis step must update at least one memory file.

---

## Initialization Rule

At the beginning of a session or first analysis step:

1. Check whether `analysis_outputs/` exists.
2. If not, create it.
3. Check whether the three memory files exist.
4. If not, create them.
5. Then read existing memory before starting new analysis.

---

## Step 1: Dataset Inspection

Before deep analysis, inspect:

* number of rows and columns
* column names
* data types
* missing values
* duplicate rows
* likely variable groups
* likely grain of the dataset

Return a concise summary of:

* dataset structure
* likely meaning of the columns
* what types of analysis are possible

If column meaning is unclear, infer cautiously and say so.

---

## Step 2: Read Existing Memory

Before starting a new analysis task:

* read `analysis_outputs/insights_registry.md` if it exists
* read `analysis_outputs/dashboard_data.json` if it exists
* read `analysis_outputs/prompt_log.md` if it exists

Use them to:

* avoid repeating the same work
* refine the current analysis
* build on earlier findings
* keep conclusions consistent

---

## Step 3: Run Analysis

Perform only analyses that are supported by the dataset.

Examples of valid analysis behaviors:

* compare segments
* analyze distributions
* detect anomalies
* identify misleading patterns
* test whether a previous finding still holds
* refine earlier conclusions

Keep results:

* evidence-based
* concise
* non-redundant
* relevant to the user’s question

---

## Step 4: Validate Before Storing

Before writing to memory, ask:

* Is this finding actually supported by the data?
* Is it strong enough to matter?
* Is it new?
* Does it refine or contradict an earlier insight?

If yes:

* store it

If weak or inconclusive:

* mention it in the response if useful
* do not store it as a confirmed insight

---

## Step 5: Update Memory

### Update `analysis_outputs/insights_registry.md` when:

* a meaningful pattern is discovered
* a previous belief is corrected
* a strong contrast or anomaly is found
* a conclusion becomes clear enough to reuse later

### Update `analysis_outputs/dashboard_data.json` when:

* a metric, summary, or grouped result can be visualized
* a chart-ready table is produced
* a KPI value is identified
* a category comparison is useful for dashboarding

### Update `analysis_outputs/prompt_log.md` after every meaningful step.

---

## Response Style

When replying:

* answer clearly
* summarize only the most relevant findings
* do not dump unnecessary numbers
* refer to stored memory when relevant
* maintain continuity across prompts

---

## Dashboard Preparation Rule

If the user later asks for a dashboard:

* use `analysis_outputs/dashboard_data.json` as the main source of truth
* use `analysis_outputs/insights_registry.md` for narrative insight sections
* do not rebuild everything from chat history if the structured files already exist

If dashboard data is incomplete:

* complete the missing structured sections first
* then generate the dashboard

---

## Dashboard Data Standard

When storing dashboard data, prefer sections like:

```json
{
  "kpis": {},
  "category_comparisons": {},
  "distribution_summaries": {},
  "segment_analysis": {},
  "outliers": {},
  "trends": {}
}
```

Only include sections supported by the dataset.

---

## Analysis Discipline

* Do not assume causation from correlation
* Do not overstate weak findings
* Do not store speculation as memory
* Do not rely only on averages when distributions matter
* Prefer fewer strong insights over many weak ones
* If earlier stored insights are wrong, correct them

---

## Behavior Under Uncertainty

If the dataset is incomplete or ambiguous:

* state the limitation
* continue with the strongest supported analysis
* store only what is defensible

---

## Final Standard

Follow this pattern:

data -> inspect -> analyze -> validate -> store -> reuse -> refine

Avoid:

data -> answer -> forget
x