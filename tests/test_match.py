import os
import tempfile
import unittest

from jobhunt import match, seen
from jobhunt.model import Role


def role(**kw):
    base = dict(source="reed", source_id="1", title="Senior PPC Manager",
                url="https://www.reed.co.uk/jobs/1", contract_type="contract",
                rate="£450", rate_shown=True, description="Google Ads and GA4 contract")
    base.update(kw)
    return match.classify(Role(**base))


class Classify(unittest.TestCase):
    def test_strong(self):
        self.assertEqual(role().verdict, "strong")

    def test_no_rate_is_maybe(self):
        r = role(rate="", rate_shown=False)
        self.assertEqual(r.verdict, "maybe")
        self.assertIn("no rate", r.reason)

    def test_permanent_dropped(self):
        self.assertEqual(role(contract_type="permanent").verdict, "drop")

    def test_junior_dropped(self):
        self.assertEqual(role(title="Junior PPC Executive").verdict, "drop")

    def test_seo_dropped(self):
        self.assertEqual(role(title="SEO Specialist", description="SEO, some ppc").verdict, "drop")

    def test_excluded_companies(self):
        for c in ["CheqUp", "Impression", "Creation Recruitment"]:
            self.assertEqual(role(company=c).verdict, "drop", c)
        r = role(description="Contact Jessie Rushton about this Google Ads contract")
        self.assertEqual(r.verdict, "drop")

    def test_impressions_metric_not_excluded(self):
        r = role(description="Grow impressions and conversions in Google Ads, contract")
        self.assertEqual(r.verdict, "strong")

    def test_low_budget_dropped(self):
        self.assertEqual(role(extra={"low_budget": True}).verdict, "drop")

    def test_unknown_type_needs_contract_wording(self):
        self.assertEqual(role(contract_type="unknown", description="Google Ads role").verdict, "drop")
        self.assertNotEqual(role(contract_type="unknown",
                                 description="Google Ads freelance role").verdict, "drop")


class Seen(unittest.TestCase):
    def test_roundtrip_and_url_match(self):
        path = os.path.join(tempfile.mkdtemp(), "seen.json")
        d = seen.load(path)
        seen.mark(d, "reed:1", "https://www.reed.co.uk/jobs/1?src=x", "t")
        seen.save(d, path)
        d2 = seen.load(path)
        self.assertTrue(seen.is_seen(d2, "reed:1", ""))
        self.assertTrue(seen.is_seen(d2, "other:9", "https://www.reed.co.uk/jobs/1"))
        self.assertFalse(seen.is_seen(d2, "reed:2", "https://www.reed.co.uk/jobs/2"))


if __name__ == "__main__":
    unittest.main()
