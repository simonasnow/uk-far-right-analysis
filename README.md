# Website Scraper for UK far-right content analysis

## Overview

This repository contains a configurable Python web-scraping pipeline used to collect publicly available content from the Patriotic Alternative website (<https://www.patrioticalternative.org.uk>). The scraper extracts article URLs, titles, publication dates, textual content, images, and videos and stores the results in a structured JSON file.

The scraper is designed to be reusable across different websites through a configuration file (`config.yml`) that specifies the target website and relevant content sections.

---

## Repository Structure

```text
.
├── scraper.py
├── config.yml
├── articles.json
├── requirements.txt
└── README.md
```
---
## Use

1. Clone the repository.

2. Install dependencies: pip install -r requirements.txt

3. Configure config.yml.

4. Run: python scraper.py.

5. Inspect the generated articles.json file.

**Use the scraper responsibly for research purposes.**

