"""Contact and social link extraction engine using Regex and BeautifulSoup."""

import re
from typing import Dict, List, Set
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from lead_pulse.config import GENERIC_PREFIXES, IGNORED_EXTENSIONS

# Robust email pattern
EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    re.IGNORECASE
)

# International and domestic phone pattern (handles +1, (555) 000-0000, +44, etc.)
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
)

# Social network patterns
SOCIAL_PATTERNS = {
    "linkedin": re.compile(r"https?://(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9_-]+/?", re.I),
    "twitter": re.compile(r"https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9_]+/?", re.I),
    "instagram": re.compile(r"https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+/?", re.I),
    "facebook": re.compile(r"https?://(?:www\.)?facebook\.com/[a-zA-Z0-9_.]+/?", re.I),
    "github": re.compile(r"https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?", re.I),
}


class ContactExtractor:
    """Extracts, cleans, and deduplicates contact data from raw HTML or text."""

    @staticmethod
    def extract_emails(html_content: str) -> List[str]:
        """Extract clean, valid emails, filtering false positives and asset names."""
        soup = BeautifulSoup(html_content, "html.parser")
        candidates: Set[str] = set()

        # 1. Check mailto: links
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if href.lower().startswith("mailto:"):
                clean_email = href.split("mailto:")[1].split("?")[0].strip()
                if clean_email:
                    candidates.add(clean_email.lower())

        # 2. Check full text via Regex
        raw_matches = EMAIL_REGEX.findall(html_content)
        for email in raw_matches:
            email_lower = email.lower().strip(".,;:()")
            candidates.add(email_lower)

        # 3. Filter false positives
        valid_emails = []
        for email in candidates:
            # Check length and dots
            if len(email) < 6 or "@" not in email:
                continue
            
            # Avoid image assets like image@2x.png
            if any(email.endswith(ext) for ext in IGNORED_EXTENSIONS):
                continue

            username, domain = email.split("@", 1)
            if not username or not domain or "." not in domain:
                continue

            # Avoid placeholder domains
            if domain in {"example.com", "domain.com", "email.com", "yourdomain.com", "mysite.com"}:
                continue

            valid_emails.append(email)

        # Sort with non-generic emails prioritized first (e.g. founder@ over info@)
        valid_emails.sort(key=lambda x: (x.split("@")[0] in GENERIC_PREFIXES, x))
        return valid_emails

    @staticmethod
    def extract_phones(html_content: str) -> List[str]:
        """Extract clean phone numbers from tel: links and body text."""
        soup = BeautifulSoup(html_content, "html.parser")
        phones: Set[str] = set()

        # 1. Check tel: links
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if href.lower().startswith("tel:"):
                clean_tel = href.split("tel:")[1].strip()
                if len(re.sub(r"\D", "", clean_tel)) >= 7:
                    phones.add(clean_tel)

        # 2. Regex search in page text
        text = soup.get_text()
        matches = PHONE_REGEX.findall(text)
        for match in matches:
            cleaned = match.strip(".,;:()- ")
            digits = re.sub(r"\D", "", cleaned)
            # Accept if digits are between 7 and 15 (standard phone length)
            if 7 <= len(digits) <= 15:
                phones.add(cleaned)

        return sorted(list(phones))[:3]  # Return top 3 candidates

    @staticmethod
    def extract_socials(html_content: str) -> Dict[str, str]:
        """Extract social profile links from anchor tags."""
        soup = BeautifulSoup(html_content, "html.parser")
        found_socials: Dict[str, str] = {}

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            for platform, pattern in SOCIAL_PATTERNS.items():
                if platform not in found_socials and pattern.match(href):
                    found_socials[platform] = href

        return found_socials

    @staticmethod
    def extract_metadata(html_content: str) -> Dict[str, str]:
        """Extract company name, page title, and meta description."""
        soup = BeautifulSoup(html_content, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        
        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()

        return {
            "title": title,
            "description": meta_desc[:250] if meta_desc else ""
        }
