# Job hunt autopilot

Once a day this finds contract and freelance performance marketing work, removes
anything already shown, ranks what's left, and sends Dan one shortlist email.
The top roles get draft replies. **Nothing is ever sent, bid or applied for
automatically.** Dan sends everything himself.

- `RUNBOOK.md`: the step-by-step instruction the daily scheduled task follows
- `jobhunt/`: fetchers for Reed, Adzuna and Freelancer.com, match rules, seen list
- `jobhunt/config.py`: search terms, match terms and the never-include list
- `state/seen.json`: the seen list. The live copy is on the `jobhunt-state` branch.
- `docs/fiverr-gig.md`: Fiverr gig copy (Part 2, nothing to build)

## Sources and how each is reached

| Source | Route | Terms checked |
|---|---|---|
| Upwork | Claude Upwork connector (find jobs, save job) | Official connector |
| ZipRecruiter | Claude ZipRecruiter connector | Official connector. **US and Canada jobs only**, so for Dan it only helps with remote roles open to UK contractors. Expect little from it. |
| Reed | Jobseeker API, `contract=true` | API key via basic auth. The docs page states no automation limits. |
| Adzuna | Jobs API, `gb`, `contract_type=contract` | Personal research use is allowed. Credit Adzuna as the data source. Limit is 250 calls a day; a run uses about 7. |
| Freelancer.com | Public projects API, filtered by skill (Google Ads, Analytics, PPC, BigQuery, Looker Studio) | Public search works without a token. |
| PeoplePerHour | Gmail alert emails | No official public API as of Oct 2026 (only third-party scrapers), so email only |
| Reed, Totaljobs, CV-Library, Indeed alerts | Gmail alert emails | Email route |

## Match rules

- **Strong:** contract or freelance, rate shown, Google Ads, GA4 or performance
  marketing central, senior level
- **Maybe:** relevant but no rate shown, or seniority unclear
- **Drop** (never shown): permanent, junior, mainly SEO or social content, not in
  English, budget too low for senior work (Freelancer under about $750 fixed or
  $35/hr), or the never-include list

## Secrets

Keys are never pasted into chat or committed (`*.env` is gitignored). They're
read from environment variables first, then from `~/.jobhunt/secrets.env`:

```
REED_API_KEY=...
ADZUNA_APP_ID=...
ADZUNA_APP_KEY=...
# optional
FREELANCER_TOKEN=...
```

For the cloud scheduled task, add the same variables in the environment's
settings (cloud environment menu, then Edit, then environment variables or
network secrets). For local runs, use the env file.

## Dan's setup steps (about 15 minutes)

1. **Connect the right Gmail.** The Gmail connector in Claude is currently signed in to
   `dan.whitehouse@chequp.com`. Reconnect it to `dan@danwhitehouse.com` in claude.ai
   connector settings. The daily run checks this and stops without touching email
   if it's still the wrong mailbox.
2. Create PeoplePerHour category alerts (Google Ads, PPC, GA4, paid media) delivered to that Gmail.
3. Create alerts on Reed, Totaljobs, CV-Library and Indeed: contract only, UK or remote.
4. Get API keys:
   - Reed: https://www.reed.co.uk/developers/jobseeker
   - Adzuna: https://developer.adzuna.com/signup
   - Freelancer.com: optional, search works without one
5. Save the keys as environment variables as described above.
6. Confirm the shortlist address (`dan@danwhitehouse.com`).

## Schedule

Daily at 07:00 UK time from Mon 19 Oct 2026, set up as a Claude scheduled task
that starts a fresh session each day using `RUNBOOK.md`, with the Gmail, Upwork
and ZipRecruiter connectors attached. The cron is
`CRON_TZ=Europe/London 50 6 * * *`, starting a few minutes early so the email is
in by 07:00. The runbook skips any day before 19 Oct.

**Stop and resume:** pause or resume the scheduled task in claude.ai. The seen list
lives on the `jobhunt-state` branch, so nothing is lost.

## Local use

```
python3 -m jobhunt run                 # fetch, classify, write out/shortlist.json
python3 -m jobhunt seen-check <url>
python3 -m jobhunt mark-seen out/shortlist.json
python3 -m unittest discover -s tests
```
Python 3.9+ with the standard library only. No packages to install.
