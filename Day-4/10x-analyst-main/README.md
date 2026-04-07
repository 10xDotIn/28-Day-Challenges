<p align="center">
  <img src="https://10x.in/logo.png" alt="10x.in" width="120" />
</p>

<h1 align="center">10x-Analyst</h1>

<p align="center">
  <strong>Agentic Analysis Automation Swarm</strong><br/>
  A proprietary multi-agent Claude Code plugin for end-to-end data analysis automation
</p>

<p align="center">
  <a href="https://10x.in">Website</a> &middot;
  <a href="#quick-start">Quick Start</a> &middot;
  <a href="#commands">Commands</a> &middot;
  <a href="#architecture">Architecture</a>
</p>

---

> **Proprietary Software** — This plugin is the intellectual property of [10x.in](https://10x.in) and is developed, maintained, and owned by the **10x Team**. All rights reserved. Unauthorized reproduction, distribution, or commercial use without explicit written permission from 10x.in is strictly prohibited. See [LICENSE](#license) for details.

---

## What is 10x-Analyst?

**10x-Analyst** is a production-grade Claude Code plugin built by the 10x Team that transforms raw data into actionable insights, comprehensive reports, and interactive dashboards — fully automated through a coordinated swarm of five specialist AI agents.

Drop your data in, run one command, and get:
- Cleaned & profiled datasets
- Statistical analysis with EDA, correlations, and KPIs
- Publication-ready charts and visualizations
- Structured Markdown reports
- Interactive HTML dashboards
- Business recommendations and strategic action items

## Quick Start

```bash
# 1. Place your data files in the input directory
#    input/my-dataset/data.csv

# 2. Run the full analysis pipeline
/10x-analyst:analyze my-dataset

# 3. Find all results in output/my-dataset/
```

A **demo Shopify e-commerce dataset** is included out of the box:

```bash
/10x-analyst:analyze shopify-data
```

## Commands

| Command | Description |
|---------|-------------|
| `/10x-analyst:analyze` | Full agentic pipeline — ingest, clean, analyze, visualize, report, dashboard |
| `/10x-analyst:profile` | Data profiling and quality assessment |
| `/10x-analyst:clean` | Data cleaning and transformation |
| `/10x-analyst:query` | Ask natural language questions about your data |
| `/10x-analyst:visualize` | Generate charts and visualizations |
| `/10x-analyst:report` | Generate a comprehensive Markdown analysis report |
| `/10x-analyst:dashboard` | Build a standalone interactive HTML dashboard |

Every command takes a **dataset name** as argument and reads from `input/<dataset>/`, writing results to `output/<dataset>/`.

## Architecture

10x-Analyst coordinates **5 specialist agents** through an orchestrator pipeline:

```
                        User Request
                             │
                             ▼
                   ┌───────────────────┐
                   │   ORCHESTRATOR    │
                   │  (Command Router) │
                   └────────┬──────────┘
                            │
         ┌──────┬───────────┼───────────┬──────────┐
         ▼      ▼           ▼           ▼          ▼
    ┌─────────┐┌──────────┐┌──────────┐┌────────┐┌──────────┐
    │  Data   ││  Stats   ││Visualizer││Reporter││Strategist│
    │ Engineer││  ician   ││          ││        ││          │
    └────┬────┘└────┬─────┘└────┬─────┘└───┬────┘└────┬─────┘
         │          │           │           │          │
         ▼          ▼           ▼           ▼          ▼
      Clean &    EDA &      Charts &    Markdown   Business
      Profile    Stats      Dashboard    Report    Actions
```

### Agent Responsibilities

| Agent | Role |
|-------|------|
| **Data Engineer** | Ingest, profile, clean, and transform raw data files |
| **Statistician** | Exploratory data analysis, correlations, distributions, statistical tests, RFM segmentation |
| **Visualizer** | Matplotlib/Seaborn charts, Chart.js interactive HTML dashboards |
| **Reporter** | Assemble all findings into structured, publication-ready Markdown reports |
| **Strategist** | Interpret findings and generate business recommendations & prioritized action items |

### Pipeline Flow

| Command | Agent Pipeline |
|---------|---------------|
| `:analyze` | Data Engineer → Statistician → Visualizer → Reporter → Strategist |
| `:profile` | Data Engineer |
| `:clean` | Data Engineer |
| `:query` | Data Engineer → Statistician → Strategist |
| `:visualize` | Data Engineer → Visualizer |
| `:report` | Data Engineer → Statistician → Reporter → Strategist |
| `:dashboard` | Data Engineer → Statistician → Visualizer |

### Model Strategy

| Model | Best For | Why |
|-------|----------|-----|
| **Opus** | `:analyze`, complex `:query` | Maximum reasoning for deep analysis |
| **Sonnet** | `:report`, `:dashboard`, `:query` | Balanced quality and speed |
| **Haiku** | `:profile`, `:clean`, `:visualize` | Fast, token-efficient for scripted tasks |

## Supported Data Formats

| Format | Extensions | Engine |
|--------|-----------|--------|
| CSV | `.csv` | pandas `read_csv` |
| Excel | `.xlsx`, `.xls` | pandas `read_excel` (openpyxl / xlrd) |
| JSON | `.json` | pandas `read_json` / `json_normalize` |

## Project Structure

```
10x-analyst/
├── .claude-plugin/plugin.json     # Plugin metadata
├── CLAUDE.md                      # Orchestrator — routes commands to agents
├── README.md                      # This file
├── input/                         # Data input directory
│   └── shopify-data/              # Demo dataset (included)
│       ├── customers.csv
│       ├── orders.csv
│       ├── order_items.csv
│       ├── products.csv
│       └── price_changes.csv
├── output/                        # Analysis output directory (auto-created)
├── agents/                        # 5 specialist subagent definitions
│   ├── data-engineer.md
│   ├── statistician.md
│   ├── visualizer.md
│   ├── reporter.md
│   └── strategist.md
├── skills/                        # 7 slash commands
│   ├── analyze/SKILL.md
│   ├── profile/SKILL.md
│   ├── clean/SKILL.md
│   ├── query/SKILL.md
│   ├── visualize/SKILL.md
│   ├── report/SKILL.md
│   └── dashboard/SKILL.md
├── references/                    # Shared knowledge base
│   ├── analysis-patterns.md
│   ├── chart-styles.md
│   └── data-quality.md
└── scripts/                       # Reusable Python utilities
    ├── profiler.py
    ├── data_cleaner.py
    ├── chart_generator.py
    └── dashboard_template.py
```

## Requirements

- Python 3.8+
- pandas, matplotlib, seaborn (auto-installed if missing)
- openpyxl (for `.xlsx`), xlrd (for `.xls`)
- Chart.js CDN (for dashboard interactivity)

## License

**Proprietary Software** — Copyright (c) 2024-2026 [10x.in](https://10x.in). All rights reserved.

This software and its associated documentation are the exclusive property of 10x.in. No part of this software may be reproduced, distributed, modified, or transmitted in any form or by any means without the prior written permission of 10x.in.

For licensing inquiries, contact the 10x Team at [10x.in](https://10x.in).

---

<p align="center">
  <sub>Built with precision by the <strong>10x Team</strong> at <a href="https://10x.in">10x.in</a></sub><br/>
  <sub>10x-Analyst v1.0.0</sub>
</p>
