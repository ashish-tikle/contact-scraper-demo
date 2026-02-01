# Contact Scraper Demo

A Python-based web scraper that extracts contact information (names, emails, phone numbers) from websites and generates clean Excel reports.

## What It Does

- Scrapes websites or local HTML files for contact data
- Extracts and normalizes Name, Email, and Phone Number fields
- Exports deduplicated results to Excel with summary statistics

## Features

- ✅ **Robots.txt compliance** – Respects site crawling rules
- ✅ **Rate limiting** – Configurable delays between requests
- ✅ **Data normalization** – Cleans and standardizes contact info
- ✅ **Deduplication** – Removes duplicate entries automatically
- ✅ **Excel export** – Professional formatted output with summary sheet

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run against sample URLs
python scraper.py --input sample_urls.txt --output contacts.xlsx
```

## CLI Options

```
--input PATH          Input file containing URLs or HTML files (required)
--output PATH         Output Excel file path (default: contacts.xlsx)
--delay SECONDS       Delay between requests in seconds (default: 1)
--user-agent STRING   Custom User-Agent header
--no-robots           Ignore robots.txt restrictions
--verbose            Enable detailed logging
```

## Usage Examples

**Scrape local HTML files:**
```bash
python scraper.py --input local_files.txt --output local_contacts.xlsx --verbose
```

**Scrape real URLs with 2-second delay:**
```bash
python scraper.py --input urls.txt --output results.xlsx --delay 2
```

**Ignore robots.txt with custom user agent:**
```bash
python scraper.py --input urls.txt --output data.xlsx --no-robots --user-agent "MyBot/1.0"
```

## Project Structure

```
contact-scraper-demo/
├── scraper.py           # Main scraping logic
├── requirements.txt     # Python dependencies
├── sample_urls.txt      # Example input URLs
├── contacts.xlsx        # Output file (generated)
└── README.md
```

## Client Deliverables

**What to showcase:**

1. **Screenshot** of the Excel output showing clean, organized data
2. **Data quality** – Highlight normalization (formatted phones, validated emails)
3. **Summary sheet** – Total contacts found, duplicates removed, success rate
4. **Before/After** – Raw HTML vs. structured Excel comparison

## What I Would Extend for Your Site

- 🎯 **Site-specific parsers** – Custom extraction logic for LinkedIn, directory sites, or your target domains
- 🌐 **Selenium/Playwright** – Handle JavaScript-rendered content and dynamic pages
- 🔄 **Proxy rotation** – Rotate IPs to avoid blocking on large-scale scrapes
- 🔍 **Domain filtering** – Only scrape contacts from specific domains or email patterns
- 📊 **Google Sheets export** – Direct integration for real-time cloud-based reporting
- 🧹 **Advanced deduplication** – Fuzzy matching for similar names/companies

## Extensibility Ideas

- 🔧 **Async scraping** – Parallel requests for faster processing
- 🔧 **Database integration** – PostgreSQL/MySQL for large datasets
- 🔧 **Contact validation** – Real-time email/phone verification APIs
- 🔧 **Multiple formats** – Add CSV/JSON export options

---

**License:** MIT  
**Python Version:** 3.8+