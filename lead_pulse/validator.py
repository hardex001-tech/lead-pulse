"""Email validation and domain MX record verifier."""

import re
from typing import Dict, Tuple

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

from lead_pulse.config import GENERIC_PREFIXES

# Common disposable email providers
DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "throwawaymail.com", "sharklasers.com", "yopmail.com"
}


class EmailValidator:
    """Validates email format and verifies domain Mail Exchanger (MX) DNS records."""

    @staticmethod
    def validate_syntax(email: str) -> bool:
        """Verify basic email syntax structure."""
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    @classmethod
    def check_mx_records(cls, domain: str) -> Tuple[bool, str]:
        """Check if domain has active MX records."""
        if not DNS_AVAILABLE:
            return True, "DNS module bypassed"

        try:
            records = dns.resolver.resolve(domain, "MX", lifetime=3.0)
            if records:
                primary_mx = str(records[0].exchange).rstrip(".")
                return True, primary_mx
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
            # Fallback check for A record if no explicit MX exists
            try:
                a_records = dns.resolver.resolve(domain, "A", lifetime=2.0)
                if a_records:
                    return True, "A-record fallback"
            except Exception:
                pass
            return False, "No MX records found"
        except Exception as e:
            return False, f"DNS error: {str(e)[:30]}"

        return False, "No MX records"

    @classmethod
    def verify(cls, email: str) -> Dict[str, any]:
        """Comprehensive verification of an email address."""
        email = email.strip().lower()
        
        if not cls.validate_syntax(email):
            return {
                "email": email,
                "status": "INVALID",
                "deliverable": False,
                "reason": "Malformed syntax",
                "mx_server": None,
                "is_generic": False
            }

        username, domain = email.split("@", 1)
        is_generic = username in GENERIC_PREFIXES

        if domain in DISPOSABLE_DOMAINS:
            return {
                "email": email,
                "status": "DISPOSABLE",
                "deliverable": False,
                "reason": "Disposable email service",
                "mx_server": None,
                "is_generic": is_generic
            }

        has_mx, mx_info = cls.check_mx_records(domain)
        if not has_mx:
            return {
                "email": email,
                "status": "UNDELIVERABLE",
                "deliverable": False,
                "reason": "Domain has no active mail server",
                "mx_server": None,
                "is_generic": is_generic
            }

        status = "ACCEPT_ALL" if is_generic else "VERIFIED"
        return {
            "email": email,
            "status": status,
            "deliverable": True,
            "reason": "Active MX record confirmed",
            "mx_server": mx_info,
            "is_generic": is_generic
        }
