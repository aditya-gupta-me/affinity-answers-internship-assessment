# Technical Documentation

## Quick Overview

This scraper automates OLX search result extraction using Selenium + BeautifulSoup, with intelligent filtering to return only relevant car cover products.

**Stack**: Python 3.7+ | Selenium WebDriver | Firefox | BeautifulSoup4 | Tabulate

**Execution Time**: ~15-20 seconds per run

---

## Architecture

The code follows a modular functional design with four layers:

1. **Scraping** (`scrape_olx_with_selenium`) - Browser automation & data extraction
2. **Filtering** (`is_relevant_car_cover`) - Relevance detection logic
3. **Display** (`display_results`, `show_filtered_items`) - Terminal output formatting
4. **Persistence** (`save_to_csv`) - CSV export

---

## Core Functions

### `scrape_olx_with_selenium(url)`

Automated browser scraping with headless Firefox:

- **Headless mode** - Runs in background
- **Custom user agent** - Mimics regular browser
- **Progressive scrolling** - Loads lazy content (3 scrolls × 2 sec)
- **Fallback selectors** - Multiple strategies for data extraction

**Timing**: 8 sec initial load + 6 sec scrolling + 1-2 sec parsing

**Returns**: `(listings, filtered_out)` - Two lists with relevant and excluded items

### `is_relevant_car_cover(title, price)`

Three-layer filtering:

1. **Keyword Exclusion** - Removes real estate (bhk, flat, sqft) and electronics (phone, laptop, tv)
2. **Price Validation** - Filters items >₹50,000 (car covers typically ₹200-10,000)
3. **Relevance Check** - Must contain both car terms AND cover terms

**Returns**: `True` if relevant, `False` otherwise

### Data Extraction Strategy

| Field       | Primary Selector                | Fallback                     |
| ----------- | ------------------------------- | ---------------------------- |
| Title       | `data-aut-id="itemTitle"`       | First `<a>` or `<span>`      |
| Price       | `data-aut-id="itemPrice"`       | Text with `₹` symbol         |
| Description | `data-aut-id="itemDescription"` | Class matching `description` |
| Location    | `data-aut-id="item-location"`   | "N/A"                        |
| Date        | `data-aut-id="item-date"`       | "N/A"                        |

---

## Configuration

Adjustable parameters in code:

```python
time.sleep(8)           # Initial page load wait
for i in range(3):      # Number of scrolls
if price_num > 50000:   # Max price threshold
```

---

## Error Handling

- **Browser init**: Falls back to system geckodriver if webdriver-manager fails
- **Data extraction**: Try-except per listing - skips failed items without stopping
- **Price parsing**: Continues with text filtering if numeric parsing fails

---

## Output

**Terminal**: Formatted table with truncated text (Title: 50 chars, Description: 40 chars)

**CSV**: `Output/olx_car_covers.csv` with UTF-8 encoding

```csv
Title,Price,Description,Location,Date
```

---

## Common Issues & Fixes

**Geckodriver not found**  
→ Script auto-downloads via webdriver-manager (needs internet)

**No listings found**  
→ Check internet connection or OLX may have changed HTML structure (update selectors)

**Too many filtered out**  
→ Adjust `exclude_keywords`, price threshold, or relevance terms in `is_relevant_car_cover()`

**Slow execution**  
→ Reduce wait times or scroll iterations (may miss some content)

---

## Updating Selectors

If OLX changes their HTML:

1. Open URL in browser and inspect a listing element
2. Find new `data-aut-id` attributes or class names
3. Update selectors in `scrape_olx_with_selenium()`

---

## Limitations

- Single page only (no pagination)
- English-optimized filtering
- No rate limiting (risk of IP blocking)
- Requires Firefox installed

---

## Future Enhancements

- Multi-page scraping with pagination
- Database storage (SQLite/PostgreSQL)
- Configuration file for parameters
- Logging instead of print statements
- Unit tests for filtering logic

---

**Version**: 1.0
