"""LeadPulse main orchestration pipeline."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os
from typing import List, Dict, Callable, Optional

from lead_pulse.crawler import SiteCrawler
from lead_pulse.validator import EmailValidator
from lead_pulse.exporter import LeadExporter
from lead_pulse.config import OUTPUT_DIR, MAX_CONCURRENT_REQUESTS


class LeadPipeline:
    """End-to-end pipeline to crawl, extract, verify, and export B2B leads."""

    def __init__(self, max_workers: int = MAX_CONCURRENT_REQUESTS):
        self.max_workers = max_workers

    def process_single_target(self, target_url: str) -> Dict[str, any]:
        """Crawl a single target, extract contacts, and verify deliverability."""
        crawler = SiteCrawler(target_url)
        lead = crawler.crawl_target()

        # Run verification on the primary email if found
        if lead["emails"]:
            primary_email = lead["emails"][0]
            verification = EmailValidator.verify(primary_email)
            lead["verification"] = verification
        else:
            lead["verification"] = {
                "email": "",
                "status": "NO_EMAIL",
                "deliverable": False,
                "reason": "No email identified on scanned pages",
                "mx_server": None,
                "is_generic": False
            }

        return lead

    def run(
        self,
        targets: List[str],
        output_prefix: str = "leads",
        on_progress: Optional[Callable[[Dict[str, any]], None]] = None
    ) -> Dict[str, any]:
        """Process multiple targets concurrently with progress callbacks."""
        results: List[Dict[str, any]] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.process_single_target, url): url for url in targets
            }

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    lead_data = future.result()
                    results.append(lead_data)
                    if on_progress:
                        on_progress(lead_data)
                except Exception as e:
                    failed_record = {
                        "domain": url,
                        "url": url,
                        "company_name": url,
                        "description": f"Failed: {str(e)}",
                        "emails": [],
                        "phones": [],
                        "socials": {},
                        "verification": {"status": "ERROR", "deliverable": False}
                    }
                    results.append(failed_record)

        # Export outputs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = os.path.join(OUTPUT_DIR, f"{output_prefix}_{timestamp}.csv")
        json_file = os.path.join(OUTPUT_DIR, f"{output_prefix}_{timestamp}.json")

        LeadExporter.export_csv(results, csv_file)
        LeadExporter.export_json(results, json_file)

        # Compute summary metrics
        total = len(results)
        with_emails = sum(1 for r in results if r.get("emails"))
        deliverable = sum(1 for r in results if r.get("verification", {}).get("deliverable"))

        return {
            "total_processed": total,
            "leads_with_email": with_emails,
            "deliverable_emails": deliverable,
            "csv_path": csv_file,
            "json_path": json_file,
            "records": results
        }
