"""Load API keys from the environment, or from ~/.jobhunt/secrets.env.

Never print values. The env file is KEY=VALUE per line, # for comments.
"""
import os

SECRETS_FILE = os.path.expanduser(os.environ.get("JOBHUNT_SECRETS", "~/.jobhunt/secrets.env"))


def load() -> None:
    if not os.path.exists(SECRETS_FILE):
        return
    with open(SECRETS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def get(name: str) -> str:
    return os.environ.get(name, "")
