# Scan Report — netflix_titles.csv
Generated: 2026-03-20 22:18

## Dataset Overview
| Metric | Value |
|--------|-------|
| Rows | 8,807 |
| Columns | 12 |
| Memory | 7.8 MB |
| Duplicates Found | 0 |

## Column Inventory
| Column | Type | Non-Null | Null % | Unique | Sample Values |
|--------|------|----------|--------|--------|---------------|
| show_id | object | 8,807 | 0.0% | 8,807 | ['s1', 's2', 's3'] |
| type | object | 8,807 | 0.0% | 2 | ['Movie', 'TV Show', 'TV Show'] |
| title | object | 8,807 | 0.0% | 8,807 | ['Dick Johnson Is Dead', 'Blood & Water', 'Ganglan |
| director | object | 6,173 | 29.9% | 4,528 | ['Kirsten Johnson', 'Julien Leclercq', 'Mike Flana |
| cast | object | 7,982 | 9.4% | 7,692 | ['Ama Qamata, Khosi Ngema, Gail Mabalane, Thabang  |
| country | object | 7,976 | 9.4% | 748 | ['United States', 'South Africa', 'India'] |
| date_added | object | 8,797 | 0.1% | 1,767 | ['September 25, 2021', 'September 24, 2021', 'Sept |
| release_year | int64 | 8,807 | 0.0% | 74 | [2020, 2021, 2021] |
| rating | object | 8,803 | 0.0% | 17 | ['PG-13', 'TV-MA', 'TV-MA'] |
| duration | object | 8,804 | 0.0% | 220 | ['90 min', '2 Seasons', '1 Season'] |
| listed_in | object | 8,807 | 0.0% | 514 | ['Documentaries', 'International TV Shows, TV Dram |
| description | object | 8,807 | 0.0% | 8,775 | ['As her father nears the end of his life, filmmak |

## Cleaning Actions Taken
1. Stripped whitespace from 11 text columns
2. Parsed 'date_added' as datetime
3. Filled 2634 nulls in 'director' with 'Unknown'
4. Filled 825 nulls in 'cast' with 'Unknown'
5. Filled 831 nulls in 'country' with 'Unknown'
6. Filled 4 nulls in 'rating' with 'Unknown'
7. Filled 3 nulls in 'duration' with 'Unknown'

## Output Files
- Cleaned dataset: `netflix-data_cleaned.csv`
- This report: `scan_report.md`
