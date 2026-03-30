# Hotel Review Sentiment Analyzer

> You are a business intelligence analyst specializing in customer feedback analysis.
> Analyze the hotel reviews in `data/hotel_reviews.csv` and turn raw customer voices into actionable business insights.

## Setup
- Reviews CSV is in `data/hotel_reviews.csv`
- ~35,000 hotel reviews
- Key columns: name (hotel name), reviews.rating, reviews.text, reviews.title, reviews.date, reviews.username, city, country, reviews.doRecommend
- Save all outputs in `output/` folder
- Install missing packages automatically: textblob pandas matplotlib numpy wordcloud pillow seaborn

## Important
- Some columns may have missing values — handle them gracefully
- reviews.text is the main review column
- reviews.rating is 1-5 stars
- name is the hotel name
- Do NOT sample or limit the data — use ALL reviews in the CSV, every single row

## What to Analyze

### Sentiment Scoring
- Score every review using TextBlob polarity (-1 to +1)
- Also extract subjectivity (0 to 1) — how opinion-based vs factual
- Positive: polarity > 0.1
- Negative: polarity < -0.1
- Neutral: between -0.1 and 0.1
- Calculate overall sentiment distribution

### Emotion Detection
Beyond just positive/negative, classify reviews into emotions:
- Joy: amazing, love, wonderful, fantastic, excellent, perfect, beautiful, delightful
- Anger: terrible, worst, awful, horrible, disgusting, unacceptable, furious, outrageous
- Disappointment: disappointed, expected, underwhelming, mediocre, letdown, overrated
- Trust: reliable, safe, consistent, dependable, professional, trustworthy
- Surprise: surprised, unexpected, shocked, wow, impressed, beyond
- Count each emotion across all reviews

### Rating vs Sentiment Mismatch
- Find reviews where rating is high (4-5) but sentiment is negative
- Find reviews where rating is low (1-2) but sentiment is positive
- List top 10 mismatches with actual review text

### Word Frequency Analysis
- Most common words from positive reviews (exclude stopwords)
- Most common words from negative reviews (exclude stopwords)
- Find words unique to negative reviews
- Find words unique to positive reviews
- Find bigrams (2-word phrases) in negative reviews — more insightful than single words

### Topic Detection
Group reviews by topic using keyword matching:
- Cleanliness: dirty, clean, stain, mold, smell, hygiene, filthy, dust, hair, stained, spotless
- Service: staff, rude, friendly, helpful, reception, manager, service, attitude, polite, courteous
- Room: bed, pillow, mattress, bathroom, shower, toilet, towel, small, spacious, comfortable, suite
- Location: location, walk, distance, far, near, central, transport, area, downtown, metro, beach
- Food: breakfast, food, restaurant, dinner, meal, coffee, buffet, eat, lunch, dining
- WiFi: wifi, internet, connection, slow, signal, network, wireless
- Price: price, expensive, cheap, value, money, worth, cost, overpriced, rate, afford, budget
- Noise: noise, noisy, loud, quiet, street, traffic, wall, hear, sound, silent, thin
Count for both complaints and praise. Rank by frequency.

### Hotel Comparison
- Top 10 most reviewed hotels
- Average sentiment + rating per hotel
- Best and worst hotels ranked

### Sentiment Over Time
- Group by year-month
- Track average sentiment trend
- Flag sudden drops or spikes

### Review Length Analysis
- Average word count of positive vs negative reviews
- Do angry guests write longer reviews?
- Scatter plot: review length vs sentiment

### City Analysis
- Average sentiment per city (top 10 cities with most reviews)
- Which city has happiest hotel guests?

## Output Files — Create ALL of These

### 1. `output/dashboard.html`
Self-contained interactive HTML dashboard with modern design:

**Design Requirements:**
- Dark theme (#0a0a0a background)
- Gradient header with title and key stats
- Stat cards at top: total reviews, % positive, % negative, % neutral, avg rating, total hotels
- Each stat card should have an icon or colored accent border
- Use CSS grid for layout — 2 or 3 columns where appropriate
- All charts embedded as base64 PNG images inside the HTML
- Smooth rounded corners (16px), subtle shadows, card-based layout
- Color scheme: green (#2ecc71) for positive, red (#e74c3c) for negative, yellow (#f1c40f) for neutral, purple (#6C63FF) for accents
- Section headers with subtle left border accent
- Responsive — looks good at different sizes
- Smooth hover effects on cards

**Dashboard Sections:**
1. Hero stats bar (total reviews, positive %, negative %, neutral %, avg rating)
2. Sentiment distribution — donut chart (not pie — donut looks better)
3. Emotion breakdown — horizontal bar chart showing joy, anger, disappointment, trust, surprise counts
4. Topic analysis — side by side bars (complaints red, praise green)
5. Hotel ranking — top 10 hotels with sentiment score bars
6. Word clouds — positive and negative side by side (embed the PNGs)
7. Sentiment over time — line chart
8. Review length analysis — do angry guests write more?
9. City comparison — top 10 cities by sentiment
10. Rating mismatch showcase — show 5 examples with actual review text in quote cards
11. Top 5 most positive quotes — actual review text in green cards
12. Top 5 most negative quotes — actual review text in red cards
13. Footer with generation info

All in ONE self-contained HTML file.

### 2. `output/word_cloud_positive.png`
Word cloud — green color scheme, white background, 1200x600px

### 3. `output/word_cloud_negative.png`
Word cloud — red color scheme, white background, 1200x600px

### 4. `output/topic_chart.png`
Horizontal bar chart: complaints (red) vs praise (green) side by side per topic.
Clean, professional, sorted by total mentions.

### 5. `output/sentiment_timeline.png`
Line chart with green fill above zero, red fill below zero.
Mark any significant drops with red dots. Clean axis labels.

### 6. `output/hotel_ranking.png`
Horizontal bar chart. Top 10 hotels by sentiment.
Color gradient green to red. Review count labels on each bar.

### 7. `output/emotion_chart.png`
Horizontal bar chart showing emotion distribution.
Each emotion gets its own color:
- Joy: green
- Anger: red
- Disappointment: orange
- Trust: blue
- Surprise: purple
Sorted by count.

### 8. `output/review_length_chart.png`
Two parts:
- Bar chart: average word count for positive vs negative vs neutral reviews
- Scatter plot: review length (x) vs polarity (y), colored by sentiment

### 9. `output/city_sentiment.png`
Bar chart of top 10 cities ranked by average guest sentiment.
Color gradient. City name + review count on each bar.

### 10. `output/bigram_chart.png`
Top 20 most common 2-word phrases from negative reviews.
Horizontal bar chart. Red bars.
Bigrams are more insightful than single words — "front desk", "air conditioning", "hot water" etc.

### 11. `output/insights_report.md`
Written business report:
- Executive summary (3 sentences)
- Sentiment breakdown with numbers
- Emotion analysis — what emotions dominate?
- Top 5 things guests love (with actual quote examples)
- Top 5 things guests hate (with actual quote examples)
- Hotel ranking with analysis
- City ranking
- Top 10 rating mismatches (show review text)
- Topic analysis — where should hotels invest?
- Review length insight — do angry guests write more?
- Bigram analysis — what 2-word phrases reveal about problems
- Sentiment trend
- 5 specific business recommendations
- Final verdict: #1 thing to fix right now

## Rules
1. Read this file first
2. Install packages silently
3. Write and run analyzer.py — fix errors yourself
4. Handle missing data gracefully
5. Create ALL 11 output files
6. End with: overall sentiment, biggest complaint, #1 recommendation

## IMPORTANT: Visual Output Rule
When I ask follow-up questions after the initial analysis:
- NEVER just print text answers in the terminal
- ALWAYS create a NEW visual output file for every question I ask
- Save every visual as a PNG image or HTML file in the output/ folder
- For comparisons → create a new chart PNG
- For review examples or quotes → create a styled HTML page
- For reports or memos → create a styled HTML page
- Every single answer I ask for must produce a FILE I can open and show on screen
- Use matplotlib/seaborn for charts, save as PNG
- Use dark themed HTML for any text-heavy outputs
- Name files clearly: output/prompt_02_dashboard.png, output/prompt_03_wordclouds.png, etc.
- Keep responses short in terminal — just say what file was created and where
