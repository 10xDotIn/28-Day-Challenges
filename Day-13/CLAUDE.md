# Claude Code Analysis Guide

## Objective

Analyze the provided dataset as a **business decision problem**, not as a machine learning training task.

The purpose is to:
- understand the business problem clearly
- understand the dataset structure
- identify the main decision points
- perform focused exploratory analysis
- find waste, opportunity, and actionable insights
- produce outputs that are easy for students to understand

Do **not** train predictive models unless explicitly asked.

---

## General Working Style

While working on the dataset:

1. First understand the **business problem**
2. Then understand the **dataset columns**
3. Then identify the **core business questions**
4. Then perform **targeted analysis**
5. Then summarize findings in **plain business language**
6. Then suggest **possible decisions or actions**

Keep the output:
- practical
- structured
- readable
- insight-driven
- student-friendly

Avoid unnecessary technical complexity.

---

## Main Task

Given any dataset, do the following:

### Step 1: Understand the business context
Infer:
- what domain this dataset belongs to
- what the business is trying to achieve
- what the likely decision problem is

Output:
- a short section called **Business Problem**
- a short section called **What decision are we trying to improve?**

---

### Step 2: Understand the dataset
Read the dataset and explain:
- what each important column means
- which columns describe the entity/customer/product/user
- which columns describe actions/interventions/campaign behavior
- which columns describe outcomes/results

Output:
- a section called **Dataset Understanding**
- group columns into logical buckets
- explain them in simple language

---

### Step 3: Find the main analysis direction
Identify the 3 to 5 most useful analysis directions based on the dataset.

Examples:
- over-targeting
- segment performance
- price-demand relationships
- conversion funnel drop-offs
- campaign fatigue
- product underexposure
- past behavior effects

Output:
- a section called **What we should analyze today**
- keep only the highest-value analyses

---

### Step 4: Perform the analysis
For each selected analysis:
- define the business question
- identify the relevant columns
- calculate the necessary summaries
- describe the pattern
- explain the business meaning

For every analysis, provide:

#### Analysis Title
#### Business Question
#### Columns Used
#### What the pattern shows
#### Business Meaning
#### Recommended Action

Do not just report numbers.
Interpret them.

---

### Step 5: Add WOW findings
Find moments that are surprising, intuitive, or high-impact.

Examples:
- more effort leads to worse outcomes
- high clicks do not mean high purchases
- past campaign behavior matters more than demographics
- some customer groups are being over-targeted
- the company is ignoring high-opportunity segments

Output:
- a section called **WOW Findings**
- each finding should include:
  - the insight
  - why it is surprising
  - why it matters to the business

---

### Step 6: Add student-friendly questions
Create simple engagement questions based on the dataset.

Each question should include:
- the question
- expected answer
- explanation

Output:
- a section called **Class Engagement Questions**

Keep these practical and short.

---

### Step 7: Frame for agentic analysis
Explain how an AI agent like Claude Code can help with this dataset.

Output:
- a section called **Agentic Analysis View**
- explain:
  - what the agent can automate
  - what the human still needs to decide
  - what good prompts would look like

---

### Step 8: Final deliverable format
Your final output must contain these sections in this exact order:

1. Business Problem
2. What decision are we trying to improve?
3. Dataset Understanding
4. What we should analyze today
5. Core Analyses
6. WOW Findings
7. Class Engagement Questions
8. Agentic Analysis View
9. Final Business Recommendations

---

## Specific Instruction for This Dataset

For the current dataset, assume the goal is:

**to understand how a bank should improve its marketing targeting decisions**

Focus the analysis on:
- which customers respond better
- whether repeated contact is wasteful
- whether previous campaign outcomes matter
- which customer segments look promising
- where the campaign is wasting effort

If these columns exist, prioritize them:
- `age`
- `job`
- `marital`
- `education`
- `balance`
- `housing`
- `loan`
- `contact`
- `month`
- `campaign`
- `previous`
- `poutcome`
- `y`

Where:
- `campaign` = number of contacts in this campaign
- `previous` = number of prior contacts
- `poutcome` = result of previous campaign
- `y` = final response / subscription outcome

---

## Analysis Priorities for This Dataset

If the above bank marketing columns exist, analyze these first:

### 1. Campaign Fatigue / Over-Targeting
Check whether more contacts are improving response or reducing efficiency.

### 2. Customer Segment Response
Check which customer groups respond better than others.

### 3. Previous Campaign Signal
Check whether previous campaign outcome strongly influences current response.

### 4. Contact Method / Timing
If available, compare response by contact type or month.

---

## Rules for Interpretation

When analyzing:
- do not assume correlation means causation
- do not overclaim
- do not use jargon unless needed
- explain patterns in plain English
- prioritize business usefulness over technical detail

If the dataset is messy:
- say what is missing
- say what assumptions you are making
- continue with the best possible analysis

---

## Output Style

Write as if the result will be shown to students in class.

So:
- keep the language simple
- keep the structure clean
- keep the insights sharp
- avoid long technical paragraphs
- prefer insight + explanation + decision

---

## Example Prompt You Can Run

Analyze this dataset as a business decision problem, not a machine learning problem. First explain the business problem and dataset structure. Then identify the top 3 to 4 analyses that matter most. Perform those analyses, summarize the patterns, add WOW findings, create class engagement questions with expected answers, and finish with business recommendations and an agentic analysis view.

---

## Additional Prompt Examples

### Prompt 1
Analyze this bank marketing dataset and identify where the campaign is wasting effort.

### Prompt 2
Find which customer segments have the highest response rates and explain how the bank should change targeting.

### Prompt 3
Check whether repeated contacts improve results or create diminishing returns.

### Prompt 4
Analyze whether previous campaign outcomes are more useful than customer demographics for decision-making.


---

## Final Reminder

The goal is **not** to build a model.

The goal is to answer:

- What is the business problem?
- What does this dataset actually represent?
- What patterns matter?
- What decisions should change?
- How can AI help us analyze it faster?

Always optimize for:
**clarity, insight, and action**