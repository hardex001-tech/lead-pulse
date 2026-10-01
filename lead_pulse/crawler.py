"""Target website crawler with subpage discovery for deep contact extraction."""

import random
from typing import Dict, List, Set
from urllib.parse import urljoin, urlparse
import httpx

from lead_pulse.config import DEFAULT_TIMEOUT, USER_AGENTS
from lead_pulse.extractor import ContactExtractor

# Subpaths likely to contain direct founder/business contact details
CONTACT_SUBPATHS = [
    "/contact", "/contact-us", "/about", "/about-us", "/team",
    "/our-team", "/reach-us", "/support", "/imprint"
]


class SiteCrawler:
    """Visits a target domain and crawls relevant contact and about pages."""

    def __init__(self, base_url: str, timeout: int = DEFAULT_TIMEOUT):
        if not base_url.startswith(("http://", "https://")):
            self.base_url = f"https://{base_url}"
        else:
            self.base_url = base_url

        self.timeout = timeout
        parsed = urlparse(self.base_url)
        self.domain = parsed.netloc

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def fetch_page(self, client: httpx.Client, url: str) -> str:
        """Safely fetch HTML with error handling."""
        try:
            response = client.get(url, headers=self._get_headers(), timeout=self.timeout, follow_redirects=True)
            if response.status_code == 200:
                return response.text
        except Exception:
            pass
        return ""

    def crawl_target(self) -> Dict[str, any]:
        """Crawl homepage plus relevant subpages and extract consolidated lead data."""
        all_emails: Set[str] = set()
        all_phones: Set[str] = set()
        all_socials: Dict[str, str] = {}
        metadata: Dict[str, str] = {"title": "", "description": ""}

        visited_urls: Set[str] = set()

        with httpx.Client(verify=False) as client:
            # 1. Fetch Homepage
            home_html = self.fetch_page(client, self.base_url)
            visited_urls.add(self.base_url)

            if home_html:
                metadata = ContactExtractor.extract_metadata(home_html)
                for email in ContactExtractor.extract_emails(home_html):
                    all_emails.add(email)
                for phone in ContactExtractor.extract_phones(home_html):
                    all_phones.add(phone)
                all_socials.update(ContactExtractor.extract_socials(home_html))

            # 2. Probe high-intent contact subpages
            for path in CONTACT_SUBPATHS:
                target_subpage = urljoin(self.base_url, path)
                if target_subpage in visited_urls:
                    continue

                subpage_html = self.fetch_page(client, target_subpage)
                visited_urls.add(target_subpage)

                if subpage_html:
                    for email in ContactExtractor.extract_emails(subpage_html):
                        all_emails.add(email)
                    for phone in ContactExtractor.extract_phones(subpage_html):
                        all_phones.add(phone)
                    all_socials.update(ContactExtractor.extract_socials(subpage_html))

                # Stop early if we have found solid leads
                if len(all_emails) >= 3 and len(all_socials) >= 2:
                    break

        return {
            "domain": self.domain,
            "url": self.base_url,
            "company_name": metadata["title"].split("|")[0].split("-")[0].strip() or self.domain,
            "description": metadata["description"],
            "emails": sorted(list(all_emails)),
            "phones": sorted(list(all_phones)),
            "socials": all_socials,
            "pages_crawled": len(visited_urls)
        }
