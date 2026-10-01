"""Automated test suite for contact extraction and validation."""

import unittest
from lead_pulse.extractor import ContactExtractor
from lead_pulse.validator import EmailValidator


class TestExtractor(unittest.TestCase):
    def setUp(self):
        self.sample_html = """
        <html>
            <head><title>Acme Innovations | Modern Cloud Security</title></head>
            <body>
                <h1>Welcome to Acme</h1>
                <p>Contact founder directly at founder@acme-corp.io or sales@acme-corp.io</p>
                <a href="mailto:support@acme-corp.io">Email Us</a>
                <a href="tel:+15551234567">Call Us</a>
                <a href="https://linkedin.com/company/acme-innovations">LinkedIn Profile</a>
                <a href="https://x.com/acme_sec">Twitter</a>
                <img src="logo@2x.png" alt="Logo" />
            </body>
        </html>
        """

    def test_email_extraction(self):
        emails = ContactExtractor.extract_emails(self.sample_html)
        self.assertIn("founder@acme-corp.io", emails)
        self.assertIn("support@acme-corp.io", emails)
        self.assertNotIn("logo@2x.png", emails)

    def test_phone_extraction(self):
        phones = ContactExtractor.extract_phones(self.sample_html)
        self.assertTrue(len(phones) >= 1)
        self.assertTrue(any("5551234567" in p.replace("+", "").replace("-", "") for p in phones))

    def test_social_extraction(self):
        socials = ContactExtractor.extract_socials(self.sample_html)
        self.assertIn("linkedin", socials)
        self.assertEqual(socials["linkedin"], "https://linkedin.com/company/acme-innovations")
        self.assertIn("twitter", socials)

    def test_email_syntax_validation(self):
        self.assertTrue(EmailValidator.validate_syntax("valid.user@company.com"))
        self.assertFalse(EmailValidator.validate_syntax("invalid-email-address"))


if __name__ == "__main__":
    unittest.main()
