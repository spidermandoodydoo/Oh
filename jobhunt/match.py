"""Decide Strong / Maybe / Drop for a role. Pure functions, no network."""
import re

from . import config
from .model import Role


def _has(text: str, terms) -> list:
    hits = []
    for t in terms:
        if re.search(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])", text):
            hits.append(t)
    return hits


def excluded(role: Role) -> str:
    """Return the matched excluded name, or '' if the role is allowed."""
    who = " ".join([role.company, str(role.extra.get("recruiter", "")),
                    str(role.extra.get("contact", "")),
                    str(role.extra.get("sender", ""))]).lower()
    hit = _has(who, config.EXCLUDED_COMPANIES)
    if hit:
        return hit[0]
    text = f"{role.title} {role.description} {role.url}".lower()
    hit = _has(text, config.EXCLUDED_ANYWHERE)
    return hit[0] if hit else ""


def classify(role: Role) -> Role:
    title = role.title.lower()
    text = f"{title} {role.description.lower()}"
    ctype = (role.contract_type or "").lower()

    ex = excluded(role)
    if ex:
        return _set(role, "drop", f"excluded name: {ex}")

    if not _has(text, config.CORE_TERMS):
        return _set(role, "drop", "no performance marketing terms")

    if _has(title, config.JUNIOR_TERMS):
        return _set(role, "drop", "junior")

    is_contract = ctype in ("contract", "freelance", "temporary", "interim") \
        or bool(_has(title, config.CONTRACT_TERMS))
    is_perm = ctype == "permanent" or (
        not is_contract and bool(_has(title, config.PERMANENT_TERMS)))
    if is_perm:
        return _set(role, "drop", "permanent")
    if not is_contract and ctype not in ("unknown", ""):
        return _set(role, "drop", f"type {ctype}")
    if not is_contract:
        # unknown type: allow only if the text itself says contract/freelance
        is_contract = bool(_has(text, config.CONTRACT_TERMS))
        if not is_contract:
            return _set(role, "drop", "not shown as contract or freelance")

    central_title = _has(title, config.CENTRAL_TERMS)
    if _has(title, config.OFF_FOCUS_TERMS) and not central_title:
        return _set(role, "drop", "mainly SEO or social content")

    lang = role.extra.get("language")
    if lang and lang != "en":
        return _set(role, "drop", f"not in English ({lang})")
    if role.extra.get("low_budget"):
        return _set(role, "drop", "budget too low for senior work")

    central = central_title or _has(text, config.CENTRAL_TERMS)
    if not central and not _has(title, config.CORE_TERMS):
        return _set(role, "drop", "performance marketing not central")

    # Seniority is judged on the title, or an explicit "senior" in the text.
    senior = _has(title, config.SENIOR_TERMS) or _has(text, ["senior", "interim"])
    regulated = _has(text, config.REGULATED_TERMS)

    why = []
    if central:
        why.append(", ".join(sorted(set(central))[:3]))
    if regulated:
        why.append("regulated sector")
    if senior:
        why.append("senior level")
    reason = "; ".join(why) or "partly relevant"

    if central and role.rate_shown and senior:
        return _set(role, "strong", reason)
    if not role.rate_shown:
        reason += "; no rate shown"
    elif not senior:
        reason += "; seniority unclear"
    return _set(role, "maybe", reason)


def _set(role: Role, verdict: str, reason: str) -> Role:
    role.verdict = verdict
    role.reason = reason
    return role


def rank(roles):
    order = {"strong": 0, "maybe": 1, "drop": 2}
    return sorted(roles, key=lambda r: (order.get(r.verdict, 3), not r.rate_shown, r.title))
