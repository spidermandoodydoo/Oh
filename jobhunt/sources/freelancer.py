"""Freelancer.com projects API. Docs: https://developers.freelancer.com
Active project search is public. A token (FREELANCER_TOKEN, sent as
freelancer-oauth-v1) is used if set, but is not required to search.
"""
from datetime import datetime, timezone

from .. import secrets
from ..model import Role
from .http import get_json

BASE = "https://www.freelancer.com/api/projects/0.1/projects/active/"

# Freelancer skill ids: 66 Google Adwords, 2356 Google Ads, 298 Google Analytics,
# 1026 PPC Marketing, 2285 BigQuery, 3285 Looker Studio, 74 Facebook Marketing,
# 2274 Bing Ads, 736 Conversion Rate Optimization
JOB_IDS = [66, 2356, 298, 1026, 2285, 3285, 2274]


def fetch():
    token = secrets.get("FREELANCER_TOKEN")
    headers = {"freelancer-oauth-v1": token} if token else {}
    data = get_json(BASE, {"jobs[]": JOB_IDS, "limit": 50, "full_description": "true",
                           "job_details": "true", "compact": "true",
                           "sort_field": "time_updated"}, headers=headers)
    out = []
    for p in data.get("result", {}).get("projects", []):
        cur = p.get("currency", {}).get("code", "")
        b = p.get("budget") or {}
        unit = "/hr" if p.get("type") == "hourly" else " fixed"
        lo, hi = b.get("minimum"), b.get("maximum")
        rate = f"{cur} {int(lo)}-{int(hi)}{unit}" if lo and hi else (
            f"{cur} {int(lo or hi)}{unit}" if (lo or hi) else "")
        fx = p.get("currency", {}).get("exchange_rate") or 1.0
        top_usd = (hi or lo or 0) * fx
        low = top_usd < (35 if p.get("type") == "hourly" else 750)
        posted = p.get("submitdate")
        out.append(Role(
            source="freelancer", source_id=str(p["id"]), title=p.get("title", ""),
            url=f"https://www.freelancer.com/projects/{p.get('seo_url', p['id'])}",
            location="remote", remote=True, rate=rate, rate_shown=bool(rate),
            contract_type="freelance",
            description=p.get("description") or p.get("preview_description", ""),
            posted=datetime.fromtimestamp(posted, timezone.utc).isoformat() if posted else "",
            extra={"skills": [j.get("name") for j in (p.get("jobs") or [])],
                   "language": p.get("language", ""),
                   "low_budget": low}))
    return out
