"""Daily job hunt pipeline.

  python -m jobhunt run [--extra roles.json ...]   fetch APIs, merge extra roles,
                                                   classify, drop seen, write out/
  python -m jobhunt mark-seen out/shortlist.json   add shown roles to the seen list
  python -m jobhunt seen-check KEY_OR_URL          is this already in the seen list?

Extra roles files hold a JSON list of Role dicts collected by the agent from
the Upwork and ZipRecruiter connectors and from Gmail alert emails.
"""
import argparse
import json
import os
import sys
import traceback

from . import match, secrets, seen
from .model import Role
from .sources import adzuna, freelancer, reed

OUT = os.path.join(os.path.dirname(__file__), "..", "out")
API_SOURCES = {"reed": reed.fetch, "adzuna": adzuna.fetch, "freelancer": freelancer.fetch}


def cmd_run(args):
    secrets.load()
    roles, status = [], {}
    for name, fn in API_SOURCES.items():
        if name in args.skip:
            status[name] = "skipped"
            continue
        try:
            got = fn()
            roles += got
            status[name] = f"ok, {len(got)} fetched"
        except Exception as e:  # one source failing must not stop the run
            status[name] = f"failed: {type(e).__name__}: {e}"
            if args.verbose:
                traceback.print_exc()
    for path in args.extra:
        with open(path) as f:
            items = json.load(f)
        roles += [Role.from_dict(d) for d in items]
        status[f"extra:{os.path.basename(path)}"] = f"ok, {len(items)} loaded"

    data = seen.load()
    fresh, dupes, keys = [], 0, set()
    for r in roles:
        if r.key in keys or seen.is_seen(data, r.key, r.url):
            dupes += 1
            continue
        keys.add(r.key)
        fresh.append(match.classify(r))

    ranked = match.rank(fresh)
    shown = [r for r in ranked if r.verdict in ("strong", "maybe")]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "shortlist.json"), "w") as f:
        json.dump({"status": status, "already_seen": dupes,
                   "dropped": sum(r.verdict == "drop" for r in ranked),
                   "roles": [r.to_dict() for r in shown]}, f, indent=1)
    with open(os.path.join(OUT, "dropped.json"), "w") as f:
        json.dump([{"key": r.key, "title": r.title, "reason": r.reason}
                   for r in ranked if r.verdict == "drop"], f, indent=1)
    print(json.dumps({"status": status, "already_seen": dupes,
                      "strong": sum(r.verdict == "strong" for r in shown),
                      "maybe": sum(r.verdict == "maybe" for r in shown)}, indent=1))


def cmd_mark_seen(args):
    with open(args.file) as f:
        doc = json.load(f)
    items = doc["roles"] if isinstance(doc, dict) else doc
    data = seen.load()
    for d in items:
        r = Role.from_dict(d)
        seen.mark(data, r.key, r.url, r.title, d.get("seen_status", "shown"))
    seen.save(data)
    print(f"seen list now holds {len(data['roles'])} roles")


def cmd_seen_check(args):
    data = seen.load()
    hit = [k for k, v in data["roles"].items()
           if k == args.value or seen._norm_url(v.get("url", "")) == seen._norm_url(args.value)]
    print(json.dumps({k: data["roles"][k] for k in hit}, indent=1) if hit else "not seen")


def main(argv=None):
    p = argparse.ArgumentParser(prog="jobhunt")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--extra", action="append", default=[])
    r.add_argument("--skip", action="append", default=[], choices=list(API_SOURCES))
    r.add_argument("-v", "--verbose", action="store_true")
    r.set_defaults(fn=cmd_run)
    m = sub.add_parser("mark-seen")
    m.add_argument("file")
    m.set_defaults(fn=cmd_mark_seen)
    c = sub.add_parser("seen-check")
    c.add_argument("value")
    c.set_defaults(fn=cmd_seen_check)
    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
