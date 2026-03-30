---
name: strategy
description: "Full strategic analysis — combines profiling, trends, geography, and competition into actionable business recommendations"
argument-hint: "<dataset-folder-name>"
risk: "safe"
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
model: claude-sonnet-4-6
context: fork
agent: general-purpose
---

# Strategy — Full Content Strategy Report

You are executing the `:strategy` skill for the **10x-content-intel** plugin.

## What This Skill Does

Runs the **full pipeline** — Profile → Trends → Geo → Compete → Strategy — and generates a comprehensive strategic report with actionable recommendations.

## Instructions

### Step 1: Run All Upstream Analyses
Execute each phase sequentially, following the respective agent instructions:

1. **Content Profiler** (`agents/content-profiler.md`): Clean and profile the data
2. **Trend Analyst** (`agents/trend-analyst.md`): Analyze temporal patterns
3. **Geo Analyst** (`agents/geo-analyst.md`): Analyze geographic distribution
4. **Content Strategist** (`agents/content-strategist.md`): Synthesize all findings

### Step 2: Load All Results
After running all analyses, gather findings from:
- `output/{argument}/scan_report.md`
- `output/{argument}/trends/trend_analysis.md`
- `output/{argument}/geo/geo_analysis.md`
- `output/{argument}/compete/competitive_analysis.md`

If any of these don't exist yet, run the respective analysis first.

### Step 3: Generate Strategy Report
Create `output/{argument}/strategy_report.md` with this structure:

```markdown
# Content Strategy Report — {Dataset Name}
Generated on: {date}

## Executive Summary
- 5 bullet points summarizing the most critical findings
- One-paragraph strategic direction

## Content Library Overview
- Total content count, type split, date range
- Data quality summary

## Key Trends
- Content growth trajectory
- Genre evolution
- Format/duration shifts
- Seasonality patterns

## Geographic Landscape
- Top producing countries
- Regional concentration
- Co-production patterns
- Underrepresented regions

## Competitive Analysis
- Oversaturated genres
- Opportunity gaps
- Rising categories

## Strategic Recommendations
1. [Recommendation with rationale]
2. [Recommendation with rationale]
3. [Recommendation with rationale]
4. [Recommendation with rationale]
5. [Recommendation with rationale]
6. [Recommendation with rationale]
7. [Recommendation with rationale]

## Risk Factors & Considerations
- Data limitations
- Market assumptions
- External factors
```

## Output
- `output/{argument}/strategy_report.md`
- All intermediate outputs from upstream agents
