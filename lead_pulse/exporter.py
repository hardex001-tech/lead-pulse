"""Export engine for CSV, JSON, and Excel formats with buyer-ready column formatting."""

import os
import json
from datetime import datetime
from typing import List, Dict
import pandas as pd


class LeadExporter:
    """Formats and exports enriched lead records to disk."""

    @staticmethod
    def flatten_records(records: List[Dict[str, any]]) -> List[Dict[str, str]]:
        """Flatten nested lead structures into clean tabular rows."""
        flat_rows = []

        for r in records:
            ver = r.get("verification", {})
            socials = r.get("socials", {})
            phones = r.get("phones", [])
            emails = r.get("emails", [])

            # Primary email is the first verified or candidate email
            primary_email = emails[0] if emails else ""
            primary_phone = phones[0] if phones else ""

            row = {
                "Company Name": r.get("company_name", ""),
                "Domain": r.get("domain", ""),
                "Website URL": r.get("url", ""),
                "Primary Email": primary_email,
                "Email Status": ver.get("status", "UNCHECKED"),
                "Deliverable": "YES" if ver.get("deliverable") else "NO",
                "Mail Server (MX)": ver.get("mx_server", "") or "",
                "Phone Number": primary_phone,
                "LinkedIn": socials.get("linkedin", ""),
                "Twitter / X": socials.get("twitter", ""),
                "Instagram": socials.get("instagram", ""),
                "Facebook": socials.get("facebook", ""),
                "Description": r.get("description", ""),
                "All Emails": ", ".join(emails),
                "All Phones": ", ".join(phones),
            }
            flat_rows.append(row)

        return flat_rows

    @classmethod
    def export_csv(cls, records: List[Dict[str, any]], filepath: str) -> str:
        """Export records to CSV."""
        flat = cls.flatten_records(records)
        df = pd.DataFrame(flat)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        df.to_csv(filepath, index=False, encoding="utf-8")
        return filepath

    @classmethod
    def export_json(cls, records: List[Dict[str, any]], filepath: str) -> str:
        """Export raw enriched records to JSON."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        return filepath
