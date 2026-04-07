# 10x-Analyst Plugin — Agentic Analysis Swarm

This is a Claude Code plugin by **10x.in** — a multi-agent swarm for end-to-end data analysis automation.

## Plugin Commands

- `/10x-analyst:analyze` — Full agentic pipeline (ingest → clean → analyze → visualize → report → dashboard)
- `/10x-analyst:profile` — Data profiling and quality assessment only
- `/10x-analyst:clean` — Data cleaning and transformation only
- `/10x-analyst:query` — Ask natural language questions about your data
- `/10x-analyst:visualize` — Generate charts and visualizations from data
- `/10x-analyst:report` — Generate a comprehensive Markdown analysis report
- `/10x-analyst:dashboard` — Build a standalone interactive HTML dashboard

## Agent Swarm Architecture

The plugin coordinates 5 specialist agents in a pipeline:

```
User Request
     │
     ▼
┌─────────────────┐
│  ORCHESTRATOR    │  ← CLAUDE.md (this file) routes to agents
│  (Command Router)│
└────────┬────────┘
         │
    ┌────┼────┬──────────┬────────────┐
    ▼    ▼    ▼          ▼            ▼
┌──────┐┌──────┐┌──────────┐┌────────┐┌──────────┐
│ Data ││Stats ││Visualizer││Reporter││Strategist│
│Engine││ician ││          ││        ││          │
└──┬───┘└──┬───┘└────┬─────┘└───┬────┘└────┬─────┘
   │       │         │          │           │
   ▼       ▼         ▼          ▼           ▼
 Clean   EDA &    Charts &   Markdown    Business
 Data    Stats    Dashboard   Report     Actions
```

### Agent Responsibilities

| Agent | File | Role | Delegates To |
|-------|------|------|-------------|
| **Data Engineer** | `agents/data-engineer.md` | Ingest, profile, clean, transform data files | Scripts: `profiler.py`, `data_cleaner.py` |
| **Statistician** | `agents/statistician.md` | EDA, correlations, distributions, statistical tests, RFM | — |
| **Visualizer** | `agents/visualizer.md` | Matplotlib/seaborn charts, Chart.js HTML dashboards | Scripts: `chart_generator.py`, `dashboard_template.py` |
| **Reporter** | `agents/reporter.md` | Assemble findings into structured Markdown report | References: `analysis-patterns.md` |
| **Strategist** | `agents/strategist.md` | Interpret findings, generate business recommendations & action items | — |

### Pipeline Flow by Command

| Command | Agents Used (in order) |
|---------|----------------------|
| `:analyze` | Data Engineer → Statistician → Visualizer → Reporter → Strategist |
| `:profile` | Data Engineer only |
| `:clean` | Data Engineer only |
| `:query` | Data Engineer → Statistician → Strategist |
| `:visualize` | Data Engineer → Visualizer |
| `:report` | Data Engineer → Statistician → Reporter → Strategist |
| `:dashboard` | Data Engineer → Statistician → Visualizer |

### Path Resolution

Every command takes a **dataset name** as argument (e.g., `shopify-data`). The orchestrator resolves paths:
- **Input:** `input/<dataset-name>/` — where data files are read from
- **Output:** `output/<dataset-name>/` — where all artifacts are written

All paths are relative to the `10x-analyst/` plugin root. Never read or write outside the plugin directory.

## Supported Data Sources

- **CSV** (`.csv`) — pandas `read_csv`
- **Excel** (`.xlsx`, `.xls`) — pandas `read_excel` via openpyxl/xlrd
- **JSON** (`.json`) — pandas `read_json` / `json_normalize`

## Input / Output Directories

All data to analyze must be placed inside `input/` (in a subfolder per dataset).
All artifacts are written to `output/` (auto-creates a subfolder per analysis run).

```
10x-analyst/
├── input/                         # PUT YOUR DATA HERE
│   └── shopify-data/              # Example dataset (included)
│       ├── customers.csv
│       ├── orders.csv
│       ├── order_items.csv
│       ├── products.csv
│       └── price_changes.csv
│
└── output/                        # ALL RESULTS GO HERE
    └── shopify-data/              # Auto-created per dataset
        ├── report.md
        ├── dashboard.html
        ├── data-profile.md
        ├── cleaning-log.md
        ├── insights.json
        ├── cleaned-data/
        └── charts/
```

## Key Directories

- `agents/` — Specialist subagent definitions (5 agents)
- `skills/` — Plugin slash commands (7 commands)
- `references/` — Analysis patterns, chart styles, data quality standards
- `scripts/` — Reusable Python utilities for profiling, cleaning, charting, dashboards

## Model Strategy

- **Opus**: `:analyze` full pipeline, `:query` complex questions (maximum reasoning)
- **Sonnet**: `:report`, `:dashboard` generation (balanced quality/speed)
- **Haiku**: `:profile`, `:clean`, `:visualize` (token-efficient mechanical tasks)

## Demo Dataset

A Shopify e-commerce dataset is included at `input/shopify-data/`:
- `customers.csv` — Customer profiles
- `orders.csv` — Order transactions
- `order_items.csv` — Line items per order
- `products.csv` — Product catalog
- `price_changes.csv` — Historical price changes

Quick start: `/10x-analyst:analyze shopify-data`

This reads from `input/shopify-data/` and writes all results to `output/shopify-data/`.
