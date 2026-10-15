"""Search terms and match rules. Edit here, not in the fetchers."""

SEARCH_TERMS = [
    "google ads",
    "ppc",
    "paid search",
    "performance marketing",
    "ga4",
    "paid media",
    "paid social",
]

# A role must mention at least one of these to be considered at all.
CORE_TERMS = [
    "google ads", "adwords", "ppc", "pay per click", "paid search", "sem",
    "ga4", "google analytics", "performance marketing", "paid media",
    "paid social", "meta ads", "facebook ads", "tracking", "measurement",
    "conversion tracking", "tag manager", "gtm", "bigquery", "looker studio",
    "value-based bidding", "value based bidding", "biddable",
]

# Central terms that push a role towards Strong.
CENTRAL_TERMS = [
    "google ads", "adwords", "ppc", "paid search", "ga4", "google analytics",
    "performance marketing", "value-based bidding", "value based bidding",
]

SENIOR_TERMS = ["senior", "lead", "head of", "principal", "interim", "consultant",
                "specialist", "manager", "director", "expert"]

JUNIOR_TERMS = ["junior", "graduate", "intern", "internship", "apprentice",
                "trainee", "entry level", "entry-level", "assistant"]

PERMANENT_TERMS = ["permanent", "perm role", "full-time permanent"]

CONTRACT_TERMS = ["contract", "freelance", "interim", "day rate", "per day",
                  "outside ir35", "inside ir35", "fixed term", "fixed-term",
                  "temporary", "short term", "short-term", "project"]

# Roles mainly about these are dropped unless a central term is in the title.
OFF_FOCUS_TERMS = ["seo", "content writer", "copywriter", "social media manager",
                   "social media content", "community manager", "influencer",
                   "tiktok creator", "ugc"]

REGULATED_TERMS = ["asa", "mhra", "gphc", "pharmacy", "pharma", "healthcare",
                   "medical", "clinic", "regulated", "financial services", "fca"]

# Never include. Checked against company and recruiter/contact fields as whole
# words. "Impression" is only checked there, because "impressions" is an
# everyday ad metric and would knock out good roles if checked in the text.
EXCLUDED_COMPANIES = [
    "chequp", "cheq up", "impression", "impression digital",
    "creation recruitment", "creation recruitment bucks", "jessie rushton",
]

# Distinctive enough to check in the title and description as well.
EXCLUDED_ANYWHERE = [
    "chequp", "cheq up", "impression digital", "impressiondigital",
    "creation recruitment", "creation.co", "jessie rushton",
]
