import html
import json
import re

from django.test import TestCase


class DutchHomepageTests(TestCase):
    def test_homepages_have_reciprocal_hreflang_and_self_canonicals(self):
        expected_hreflang = [
            ("en", "https://www.difusionseo.com/"),
            ("nl-NL", "https://www.difusionseo.com/nl/"),
        ]

        for path, canonical in [
            ("/", "https://www.difusionseo.com/"),
            ("/nl/", "https://www.difusionseo.com/nl/"),
        ]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            page = response.content.decode()
            alternates = re.findall(
                r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"',
                page,
            )
            self.assertEqual(alternates, expected_hreflang)
            self.assertEqual(
                re.findall(r'<link rel="canonical" href="([^"]+)"', page),
                [canonical],
            )

        english_page = self.client.get("/").content.decode()
        english_graph = json.loads(
            re.search(
                r'<script type="application/ld\+json">(.*?)</script>',
                english_page,
                re.S,
            ).group(1)
        )["@graph"]
        organization = next(
            item for item in english_graph if item["@type"] == "Organization"
        )
        self.assertEqual(organization["contactPoint"]["email"], "info@difusionseo.com")
        self.assertEqual(organization["contactPoint"]["telephone"], "+31 6 38879199")

        unrelated_page = self.client.get("/contact/").content.decode()
        self.assertNotIn('rel="alternate" hreflang=', unrelated_page)

    def test_dutch_homepage_faq_schema_matches_visible_answers(self):
        response = self.client.get("/nl/")
        self.assertEqual(response.status_code, 200)
        page = response.content.decode()
        self.assertIn('<html class="dark" lang="nl-NL">', page)

        schema_match = re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            page,
            re.S,
        )
        self.assertIsNotNone(schema_match)
        graph = json.loads(schema_match.group(1))["@graph"]
        faq_schema = next(item for item in graph if item["@type"] == "FAQPage")

        faq_section = page.split('id="nl-faq"', 1)[1].split("</section>", 1)[0]
        visible_faqs = [
            tuple(
                html.unescape(re.sub(r"<[^>]+>", "", value)).strip()
                for value in question_and_answer
            )
            for question_and_answer in re.findall(
                r"<summary[^>]*>(.*?)</summary>\s*<p[^>]*>(.*?)</p>",
                faq_section,
                re.S,
            )
        ]
        structured_faqs = [
            (item["name"], item["acceptedAnswer"]["text"])
            for item in faq_schema["mainEntity"]
        ]

        self.assertEqual(len(visible_faqs), 7)
        self.assertEqual(visible_faqs, structured_faqs)
        self.assertEqual(
            len(re.findall(r'<a[^>]*>Meer over .*? \(Engels\)</a>', page)),
            6,
        )
        self.assertIn('href="mailto:info@difusionseo.com"', page)
        self.assertIn('href="tel:+31638879199"', page)
        self.assertIn('href="https://wa.me/31638879199"', page)
        self.assertNotIn("Bellen / WhatsApp:", page)

    def test_dutch_homepage_is_in_sitemap(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<loc>https://www.difusionseo.com/nl/</loc>")
