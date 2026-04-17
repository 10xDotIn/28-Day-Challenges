# CLAUDE.md

## Objective

Perform structured, evidence-based analysis on the **Social Media Impact on Teen Mental Health** dataset to identify meaningful behavioral patterns, risk indicators, and decision-relevant insights.

Additionally:

* persist all important outputs to disk
* maintain structured data for dashboard creation
* ensure no critical result is lost in chat output

Default mode:
**analysis + persistence + dashboard preparation**

Do not train predictive models unless explicitly requested.

---

## Operating Principles

* Work strictly from observed data
* Avoid assumptions without evidence
* Prefer structured data over text explanations
* Keep outputs concise and decision-oriented
* Prioritize strong patterns over weak observations
* Always persist outputs to files
* Maintain clean, reusable data for dashboards

---

## Execution Flow

Follow this sequence:

1. Inspect dataset
2. Validate data quality
3. Group variables
4. Run analysis
5. Detect patterns
6. Generate insights
7. Persist outputs
8. Maintain dashboard-ready data

---

## Step 1: Dataset Inspection

* Identify schema, columns, data types
* Detect missing values and duplicates
* Infer dataset grain (likely one row per student)

Output:

* dataset summary
* schema explanation
* initial grouping

---

## Step 2: Data Validation

Check for:

* missing values
* inconsistent categories
* invalid numeric values
* extreme outliers

Output:

* data quality summary
* usable columns
* limitations

---

## Step 3: Variable Grouping

Group into:

* demographics
* social media usage
* sleep / lifestyle
* mental health indicators
* performance indicators

---

## Step 4: Analysis Execution

Run high-value analyses:

* usage vs stress/anxiety
* usage vs sleep
* high vs low usage comparison
* segment analysis
* distribution analysis
* outlier detection

For each:

* compute metrics
* compare groups
* identify patterns
* give short interpretation

---

## Step 5: Pattern Detection

Identify:

* high usage + poor well-being
* high usage + stable well-being
* low usage + poor outcomes
* sleep imbalance patterns
* subgroup differences
* outliers

---

## Step 6: Insight Generation

Each insight must include:

* what is happening
* who is affected
* why it matters

Keep:

* concise
* non-repetitive
* evidence-based

---

## Step 7: Persistence Rules (CRITICAL)

After EVERY meaningful analysis step, persist outputs to disk.

All files must be stored inside:

analysis_outputs/

---

### Maintain these files:

#### latest_summary.md

* current findings
* latest analysis updates

---

#### dashboard_data.json

* structured metrics
* aggregated results
* clean visualization-ready data

---

#### dashboard_tables.csv

* flat tabular summaries
* grouped data for charts

---

#### prompt_log.md

Append:

* prompt used
* timestamp
* action summary
* files updated

---

#### insights_registry.md

Append:

* validated insights only
* one insight per entry

---

### Persistence Rules

* Never leave important results only in chat
* Always update existing files
* Keep data clean and structured
* Ensure dashboard_data.json is always usable
* Every prompt must update at least one file

---

## Step 8: Dashboard Preparation

Before dashboard creation:

Ensure:

* dashboard_data.json is complete
* tables are consistent
* labels are clean

---

## Step 9: Dashboard Generation

When user requests dashboard:

Use:

* dashboard_data.json as source of truth

Generate:

* HTML
* CSS
* JavaScript (Chart.js)

Include:

Charts:

* usage vs stress
* usage vs sleep
* high vs low usage
* usage distribution

UI:

* clean layout
* responsive design
* clear sections

---

## Preferred Analysis Focus

### Usage Analysis

* screen time groups
* heavy vs light users

### Mental Health

* stress / anxiety comparison
* avg vs median

### Sleep

* sleep vs usage

### Performance

* academic or functional metrics

### Segments

* age / gender

### Outliers

* contradictions
* anomalies

---

## Decision Rules

* Do not assume causation
* Compare distributions, not just averages
* Always check subgroup variation
* Flag small samples
* Prefer fewer strong insights

---

## Behavior Under Uncertainty

* narrow scope if needed
* state limitations clearly
* proceed with strongest signals

---

## Output Format

Always return:

1. Dataset Summary
2. Data Quality
3. Variable Groups
4. Analysis
5. Patterns
6. Insights
7. Persisted Updates

---

## Final Standard

Follow:

data → structure → comparison → pattern → insight → persist → visualize

Avoid:

data → text → forget
