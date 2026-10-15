"""The seen list: one JSON file of role keys and URLs already shown to Dan."""
import json
import os
from datetime import date

DEFAULT_PATH = os.environ.get(
    "JOBHUNT_SEEN", os.path.join(os.path.dirname(__file__), "..", "state", "seen.json"))


def load(path: str = DEFAULT_PATH) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"roles": {}}


def save(data: dict, path: str = DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def _norm_url(url: str) -> str:
    return url.split("?")[0].split("#")[0].rstrip("/").lower()


def is_seen(data: dict, key: str, url: str) -> bool:
    if key in data["roles"]:
        return True
    u = _norm_url(url)
    return bool(u) and any(_norm_url(v.get("url", "")) == u for v in data["roles"].values())


def mark(data: dict, key: str, url: str, title: str, status: str = "shown") -> None:
    data["roles"][key] = {"url": url, "title": title,
                          "status": status, "date": date.today().isoformat()}
