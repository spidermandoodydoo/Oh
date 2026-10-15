"""Adzuna jobs API, UK. Docs: https://developer.adzuna.com/docs/search
Terms: personal research use permitted; credit Adzuna as the source.
Default limits 25/min, 250/day, so keep calls low (one per term).
"""
from .. import config, secrets
from ..model import Role
from .http import get_json

BASE = "https://api.adzuna.com/v1/api/jobs/gb/search/1"


def fetch():
    app_id, app_key = secrets.get("ADZUNA_APP_ID"), secrets.get("ADZUNA_APP_KEY")
    if not (app_id and app_key):
        raise RuntimeError("ADZUNA_APP_ID / ADZUNA_APP_KEY not set")
    seen, out = set(), []
    for term in config.SEARCH_TERMS:
        data = get_json(BASE, {"app_id": app_id, "app_key": app_key, "what": term,
                               "contract_type": "contract", "results_per_page": 50,
                               "max_days_old": 7, "sort_by": "date"})
        for j in data.get("results", []):
            jid = str(j["id"])
            if jid in seen:
                continue
            seen.add(jid)
            lo, hi = j.get("salary_min"), j.get("salary_max")
            predicted = str(j.get("salary_is_predicted", "0")) == "1"
            rate = "" if predicted or not (lo or hi) else (
                f"£{int(lo):,}-£{int(hi):,}" if lo and hi and lo != hi else f"£{int(lo or hi):,}")
            loc = (j.get("location") or {}).get("display_name", "")
            desc = j.get("description", "")
            out.append(Role(
                source="adzuna", source_id=jid, title=j.get("title", ""),
                url=j.get("redirect_url", ""),
                company=(j.get("company") or {}).get("display_name", ""),
                location=loc, remote="remote" in f"{loc} {desc}".lower(),
                rate=rate, rate_shown=bool(rate),
                contract_type=j.get("contract_type") or "unknown",
                description=desc, posted=j.get("created", ""),
                extra={"recruiter": (j.get("company") or {}).get("display_name", "")}))
    return out
