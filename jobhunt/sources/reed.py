"""Reed jobseeker API. Docs: https://www.reed.co.uk/developers/jobseeker
Auth: API key as the basic auth username, empty password. Contract filter: contract=true.
"""
from .. import config, secrets
from ..model import Role
from .http import get_json

BASE = "https://www.reed.co.uk/api/1.0/search"


def fetch():
    key = secrets.get("REED_API_KEY")
    if not key:
        raise RuntimeError("REED_API_KEY not set")
    seen, out = set(), []
    for term in config.SEARCH_TERMS:
        data = get_json(BASE, {"keywords": term, "contract": "true",
                               "resultsToTake": 100}, basic_user=key)
        for j in data.get("results", []):
            jid = str(j["jobId"])
            if jid in seen:
                continue
            seen.add(jid)
            lo, hi = j.get("minimumSalary"), j.get("maximumSalary")
            rate = _rate(lo, hi, j.get("currency") or "GBP")
            loc = j.get("locationName") or ""
            desc = j.get("jobDescription") or ""
            out.append(Role(
                source="reed", source_id=jid, title=j.get("jobTitle", ""),
                url=j.get("jobUrl") or f"https://www.reed.co.uk/jobs/{jid}",
                company=j.get("employerName", ""), location=loc,
                remote="remote" in f"{loc} {desc} {j.get('jobTitle','')}".lower(),
                rate=rate, rate_shown=bool(rate), contract_type="contract",
                description=desc, posted=j.get("date", ""),
                extra={"recruiter": j.get("employerName", "")}))
    return out


def _rate(lo, hi, cur):
    if not lo and not hi:
        return ""
    sym = "£" if cur == "GBP" else cur + " "
    fmt = lambda v: f"{sym}{int(v):,}"
    if lo and hi and lo != hi:
        return f"{fmt(lo)}-{fmt(hi)}"
    return fmt(lo or hi)
