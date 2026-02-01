import argparse
import sys
import time
from pathlib import Path
from extractor.scraper import Fetcher
from extractor.parser import extract_contacts
from extractor.normalizer import normalize_record
from extractor.utils import dedupe_records, setup_logger
from extractor.writer import write_excel

#!/usr/bin/env python3
"""
CLI entry point for contact scraper.
"""



def main():
    parser = argparse.ArgumentParser(
        description="Scrape contact information from URLs or local files."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Text file with one URL or local path per line"
    )
    parser.add_argument(
        "--out",
        default="output.xlsx",
        help="Output Excel file (default: output.xlsx)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between requests in seconds (default: 0.5)"
    )
    parser.add_argument(
        "--user-agent",
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        help="User agent string for requests"
    )
    parser.add_argument(
        "--no-robots",
        action="store_true",
        help="Ignore robots.txt rules"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger(debug=args.verbose)
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)
    
    # Read input URLs/paths
    logger.info(f"Reading input from {args.input}")
    with open(input_path, 'r', encoding='utf-8') as f:
        sources = [line.strip() for line in f if line.strip()]
    
    if not sources:
        logger.error("No URLs or paths found in input file")
        sys.exit(1)
    
    logger.info(f"Found {len(sources)} source(s) to process")
    
    # Initialize fetcher
    fetcher = Fetcher(
        user_agent=args.user_agent,
        respect_robots=not args.no_robots
    )
    
    # Collect all records
    all_records = []
    
    for idx, source in enumerate(sources, 1):
        logger.info(f"Processing [{idx}/{len(sources)}]: {source}")
        
        try:
            # Fetch content
            html_text, final_url = fetcher.get(source)

            if html_text:
                # Parse contacts
                contacts = extract_contacts(html_text, final_url)
                logger.info(f"  Found {len(contacts)} contact(s)")

                # Normalize each record
                for contact in contacts:
                    normalized = normalize_record(contact)
                    all_records.append(normalized)
                logger.debug("Sample records: %s", all_records[:3])
            else:
                logger.warning(f"  No content retrieved from {source}")
        except Exception as e:
            logger.error(f"  Error processing {source}: {e}")
        
        # Apply delay between requests (except for last item)
        if idx < len(sources) and args.delay > 0:
            time.sleep(args.delay)
    
    logger.info(f"Collected {len(all_records)} total record(s)")
    
    # Deduplicate records
    unique_records = dedupe_records(all_records)
    logger.info(f"After deduplication: {len(unique_records)} unique record(s)")
    
    # Write to Excel
    if unique_records:
        write_excel(unique_records, args.out)
        logger.info(f"Successfully wrote {len(unique_records)} unique records to {args.out}")
        print(f"\n✓ Wrote {len(unique_records)} unique contact records to {args.out}")
    else:
        logger.warning("No records to write")
        print("\n⚠ No contact records found")
        sys.exit(0)


if __name__ == "__main__":
    main()