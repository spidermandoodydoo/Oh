# Daily run: job hunt autopilot

This is the instruction the 07:00 scheduled task follows. It runs in a fresh
cloud session with this repo checked out and the Gmail, Upwork and ZipRecruiter
connectors attached.

**Hard rules, every run**
- Drafts only. Never send a reply, submit a proposal, bid, apply or message anyone.
  The only email sent is the shortlist to Dan, from his own address to his own address.
- Never include CheqUp, Impression, or Creation Recruitment (Bucks, Jessie Rushton).
- Anything not checked against its source is marked **unverified**. Never state an
  inference as fact.
- One email per approach. If a fact or the vacancy can't be verified, don't draft.
  A wrong first email can't be corrected with a second one.
- Never print, log or commit API keys.

## 0. Preflight

1. If today is before Mon 19 Oct 2026 (UK time), stop. Do nothing.
2. Check which mailbox the Gmail connector is signed in to: run
   `search_threads` with `in:sent` and `pageSize: 1`, then read the sender.
   If the sender is not `dan@danwhitehouse.com` (or whatever address is set in
   `SHORTLIST_TO`), **stop**. Don't read, draft or send anything. The run ends here.
3. `scripts/state.sh pull` loads the seen list.

## 1. API sources

```
python3 -m jobhunt run
```
This fetches Reed (contract only), Adzuna (UK, contract) and Freelancer.com,
classifies the roles and writes `out/shortlist.json`. A source that fails is
recorded in `status` and the run carries on. Note any failures for the email footer.

## 2. Connector sources

Collect roles into JSON lists of objects with the `Role` fields from
`jobhunt/model.py`: `source, source_id, title, url, company, location, remote,
rate, rate_shown, contract_type, description, posted, extra`.

**Upwork** → `out/upwork.json` (freelancer org_uid from `list_accounts`, role TALENT)
- `find_jobs` `smart_search`, `mode: most_recent`, `days_posted: 1`
- `find_jobs` `search` with `title` set to each of `Google Ads`, `PPC`, `GA4`,
  `paid media`, `performance marketing`, and `experience_level: expert`
- Skip any job with `applied: true`. Set `contract_type: "freelance"`, `remote: true`,
  `source_id` to the job id, `url` to the job's `url`, and `rate` from its budget or
  hourly range. Put `client_country` and `proposals_tier` in `extra`.
- `save_job` is allowed for Strong roles, since it is not a bid. Nothing else
  that writes to Upwork.

**ZipRecruiter** → `out/ziprecruiter.json`
- `search_jobs` with `job_role` set to each of `google ads`, `ppc`, `performance marketing`,
  plus `employment_types: [CONTRACT]`, `location_types: [REMOTE]` and
  `max_posted_minutes_ago: 2880`.
- ZipRecruiter only lists US and Canada jobs. Keep a role only if it's remote and
  open to UK-based contractors. Otherwise leave it out.

**Gmail alert emails** → `out/email.json`
- `search_threads`:
  `from:(peopleperhour.com OR reed.co.uk OR totaljobs.com OR cv-library.co.uk OR indeed.com OR indeed.co.uk) newer_than:2d`
- Open each thread with `get_thread` and extract every listed job. Set `source` to
  `email:<site>`, `source_id` to the site's job id from the URL (or the URL itself),
  and `url` to one clean job URL with tracking parameters stripped where the
  link still works. Store the Gmail thread id in `extra.thread_id`.
- Alerts are set up as contract only, but still set `contract_type` from the text
  (`contract`, `freelance`, `permanent` or `unknown`).

Then re-run the pipeline with everything merged:
```
python3 -m jobhunt run --extra out/upwork.json --extra out/ziprecruiter.json --extra out/email.json
```

## 3. Sense check (required)

For every Strong and Maybe role in `out/shortlist.json`:
1. **Already approached?** Search Gmail `in:sent` for the company name, the job
   title keywords and the job URL. On Upwork, check `applied` and
   `list_freelancer_proposals`. If Dan has already applied or replied, remove the
   role from the shortlist, set `"seen_status": "applied"` on it, and include it in
   the mark-seen file.
2. **Still open?** Open the URL (WebFetch, or Upwork `find_jobs get`). If it's
   closed, filled or expired, drop it. If the page can't be read, keep the role
   and label it **unverified**.
3. **Facts.** Rate, location and contract type must come from the listing. Any field
   that was inferred is shown in the email with "(unverified)".
4. **Exclusions.** Check the recruiter or contact on the live page against the
   never-include list again.

Write the final list back to `out/shortlist.json`.

## 4. Drafts (top roles only)

- At most 3 drafts, and only for Strong roles that passed every check in step 3.
- **Voice:** before drafting, read 5 to 10 of Dan's recent sent emails from this
  mailbox and match how he writes: short, plain, first person, no headings, no
  bullet lists, no sign-off flourishes. Don't announce that the message is brief.
- Describe him as a senior performance marketing contractor. Only bring in the
  specifics that fit the role: Google Ads, GA4, Value-Based Bidding, BigQuery,
  Looker Studio, account turnaround, regulated sector work (ASA, MHRA, GPhC).
  Never invent results, figures or client names.
- If the role asks for a job title, don't pick one. Write `[TITLE: Dan to confirm]`
  and say so in the shortlist.
- **Email replies** (a recruiter or client email thread exists): `create_draft`
  threaded on that thread (set the thread id and reply subject), addressed to the
  real contact. Alert emails come from no-reply addresses, so no draft there. Put
  the text in the shortlist instead.
- **Upwork and PeoplePerHour proposals:** plain text in the shortlist email, ready to paste.

## 5. Shortlist email

`send_message` to `dan@danwhitehouse.com` (from the same mailbox), with the subject
`Job shortlist <Ddd D Mmm>`. Plain text:

```
<one line verdict, e.g. "2 strong, 3 maybe. Apply to the first two today.">

STRONG
1. <title> | <source> | <rate or "no rate shown"> | <location or remote>
   <one URL>
   <one clause on why it fits>
   [Draft in Gmail drafts]  or  [Proposal text below]

MAYBE
...

PROPOSALS TO PASTE
<role 1 title>
<text>

Notes: <failed sources, unverified items, title questions>
Adzuna listings: jobs data from Adzuna.
```
One URL per role, and no anchor links. If nothing is new, send one line saying so,
plus any source failures.

## 6. Save state

```
python3 -m jobhunt mark-seen out/shortlist.json
scripts/state.sh push
```
Mark only what was shown (plus anything found already applied). Dropped roles are
not marked, so a corrected listing can still come through later.
