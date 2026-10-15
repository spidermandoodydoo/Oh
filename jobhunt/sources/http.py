import base64
import json
import urllib.parse
import urllib.request

UA = "jobhunt-autopilot/1.0 (personal job search)"


def get_json(url: str, params=None, basic_user: str = "", headers=None, timeout: int = 30):
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json",
                                               **(headers or {})})
    if basic_user:
        token = base64.b64encode(f"{basic_user}:".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)
