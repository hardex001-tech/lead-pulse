"""Configuration settings for LeadPulse."""

import os
from typing import List

USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

DEFAULT_TIMEOUT: int = 10
MAX_CONCURRENT_REQUESTS: int = 5

# Common disposable or generic emails to filter out or flag
GENERIC_PREFIXES = {
    "noreply", "no-reply", "mailer-daemon", "abuse", "privacy", "postmaster",
    "webmaster", "security", "donotreply", "auto-reply", "terms"
}

# File extensions that look like emails or image assets (e.g. logo@2x.png)
IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js", ".woff", ".ttf", ".mp4"
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
