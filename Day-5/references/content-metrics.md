# Content Intelligence — Reference Metrics & Definitions

## Key Metrics

### Content Volume Metrics
- **Total Library Size**: Count of all unique titles
- **Content Type Split**: Percentage of Movies vs TV Shows
- **Addition Rate**: Average content added per month/year
- **Content Freshness**: % of content added in the last 2 years

### Geographic Metrics
- **Country Concentration Index**: % of total content from top 3 countries (higher = less diverse)
- **Co-production Rate**: % of content involving multiple countries
- **Regional Diversity Score**: Number of unique regions with >1% content share

### Genre Metrics
- **Genre Saturation**: Genres with >10% total share are "saturated"
- **Genre Growth Rate**: Year-over-year % change in content count per genre
- **Genre Diversity Index**: Number of unique genres / total content (higher = more diverse)

### Trend Metrics
- **Growth Trajectory**: Compound annual growth rate (CAGR) of content additions
- **Seasonality Index**: Standard deviation of monthly additions (higher = more seasonal)
- **Format Shift**: Year-over-year change in Movie:Show ratio

## Rating Categories (Netflix/US)
| Rating | Description | Audience |
|--------|-------------|----------|
| TV-MA | Mature audiences only | Adults 17+ |
| TV-14 | Parents strongly cautioned | Teens 14+ |
| TV-PG | Parental guidance suggested | General with guidance |
| TV-Y | All children | Kids |
| TV-Y7 | Directed to older children | Kids 7+ |
| TV-G | General audience | All ages |
| R | Restricted | Adults 17+ |
| PG-13 | Parents strongly cautioned | Teens 13+ |
| PG | Parental guidance | General with guidance |
| G | General audiences | All ages |
| NR/UR | Not rated / Unrated | Varies |

## Region Mapping Reference
| Region | Key Countries |
|--------|---------------|
| North America | United States, Canada |
| Europe | UK, France, Germany, Spain, Italy, Turkey |
| South Asia | India, Pakistan, Bangladesh |
| East Asia | Japan, South Korea, China, Taiwan, Hong Kong |
| Southeast Asia | Thailand, Philippines, Indonesia, Singapore |
| Latin America | Mexico, Brazil, Argentina, Colombia |
| Middle East | Egypt, UAE, Saudi Arabia, Israel |
| Africa | Nigeria, South Africa, Kenya, Ghana |
| Oceania | Australia, New Zealand |

## Chart Style Guide
- **Background**: White (`#ffffff`) for static charts, Dark (`#0f1117`) for dashboards
- **Primary Palette**: `sns.color_palette("muted")` for matplotlib
- **Dashboard Palette**: Teal `#00d4aa`, Purple `#7c5cfc`, Coral `#ff6b6b`, Gold `#ffd93d`
- **Font**: Segoe UI / system-ui
- **Grid**: Light gray `#eeeeee` for static, `#2a2e42` for dark dashboards
