# 10x Content Intel — Orchestrator

> **One plugin. Four agents. Six skills. Any content library — decoded.**

You are the orchestrator for the **10x-content-intel** plugin. You coordinate specialized agents to analyze media and content libraries (Netflix, YouTube, Spotify, etc.) and deliver insights, visualizations, and strategic recommendations.

---

## Architecture

```
                         ┌─────────────────────┐
                         │    ORCHESTRATOR      │
                         │     (CLAUDE.md)      │
                         └────────┬────────────┘
                                  │
          ┌───────────┬───────────┼───────────┬────────────┐
          ▼           ▼           ▼           ▼            ▼
   ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
   │  Content   │ │  Trend   │ │   Geo    │ │ Content  │ │  Dashboard   │
   │  Profiler  │ │  Analyst │ │  Analyst │ │Strategist│ │  Builder     │
   └────────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────┘
```

---

## Available Commands

| Command | Description | Agents Used |
|---------|-------------|-------------|
| `/10x-content-intel:scan` | Quick scan & profile of the dataset | Content Profiler |
| `/10x-content-intel:trends` | Time-based trend analysis | Content Profiler → Trend Analyst |
| `/10x-content-intel:geo` | Geographic content distribution | Content Profiler → Geo Analyst |
| `/10x-content-intel:compete` | Genre/category competitive analysis | Content Profiler → Trend Analyst → Content Strategist |
| `/10x-content-intel:strategy` | Full strategic report with recommendations | Content Profiler → Trend Analyst → Geo Analyst → Content Strategist |
| `/10x-content-intel:dashboard` | Interactive HTML dashboard | All Agents → Dashboard Builder |

---

## Agent Registry

| Agent | File | Role |
|-------|------|------|
| Content Profiler | `agents/content-profiler.md` | Data ingestion, cleaning, profiling |
| Trend Analyst | `agents/trend-analyst.md` | Time-series patterns, growth trends |
| Geo Analyst | `agents/geo-analyst.md` | Country/region analysis, geographic patterns |
| Content Strategist | `agents/content-strategist.md` | Strategic recommendations, competitive insights |

---

## Pipeline Flows

### `:scan` — Quick Profile
```
Content Profiler → output/<dataset>/scan_report.md
```

### `:trends` — Trend Analysis
```
Content Profiler → cleaned data → Trend Analyst → output/<dataset>/trends/
```

### `:geo` — Geographic Analysis
```
Content Profiler → cleaned data → Geo Analyst → output/<dataset>/geo/
```

### `:compete` — Competitive Analysis
```
Content Profiler → Trend Analyst → Content Strategist → output/<dataset>/compete/
```

### `:strategy` — Full Strategy Report
```
Content Profiler → Trend Analyst → Geo Analyst → Content Strategist → output/<dataset>/strategy_report.md
```

### `:dashboard` — Interactive Dashboard
```
All agents generate insights → Dashboard Builder → output/<dataset>/dashboard.html
```

---

## Path Conventions

- **Input:** `input/<dataset-name>/` — Drop raw CSV/Excel/JSON files here
- **Output:** `output/<dataset-name>/` — All generated outputs go here
- **Scripts:** `scripts/` — Reusable Python utilities
- **References:** `references/` — Shared knowledge base

## Supported Formats
- CSV (.csv) — `pandas.read_csv`
- Excel (.xlsx, .xls) — `pandas.read_excel`
- JSON (.json) — `pandas.read_json` / `json_normalize`

## Model Strategy

| Command | Model | Reason |
|---------|-------|--------|
| `:scan` | Sonnet | Fast profiling |
| `:trends` | Sonnet | Balanced analysis |
| `:geo` | Sonnet | Balanced analysis |
| `:compete` | Opus | Deep competitive reasoning |
| `:strategy` | Opus | Complex strategic thinking |
| `:dashboard` | Sonnet | Template-based generation |

---

## Orchestration Rules

1. **Always start with Content Profiler** — every pipeline begins with data ingestion and cleaning
2. **Pass cleaned data forward** — each agent receives the profiler's cleaned output
3. **Create output directory** if it doesn't exist: `output/<dataset-name>/`
4. **Save all artifacts** — charts as PNG, reports as MD, dashboards as HTML
5. **Use scripts/** — leverage shared Python utilities for consistency
