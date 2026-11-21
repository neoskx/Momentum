# HTML navigation for chat agents

Entry: https://neoskx.github.io/Momentum/index.html or
https://neoskx.github.io/Momentum/index.md. Its question table writes every next
URL in full: topic/keyword letter pages, languages, whole-cohort pages under
`/f/` (facts, top risers per window, new repos, breakouts, gems, milestones,
sums by language and topic) and the repo directory by name range. Any answer is
at most 4 clicks from index.html.
Each slice page lists the top 10 by stars (with created_at, pushed_at,
commits_30d), 7-day and 30-day gain, then complete facts for the whole slice:
filter rows with full counts and leaders, the other windows' leaders,
language and topic/word intersections, gain distribution (sum, median, p90),
owner/archive/fork/activity counts and created per year/month.
Slice rows link repo HTML with stars, gains 1/7/30/90/365, dates, activity, flags,
language, topics, rank in the most populous selected topic, rank_7d and rank_30d.
Every cohort repo has a page; `r/index.html` lists name ranges, each range page
lists its repos. Pages are under 100 KB; repo pages under 2 KB. Descriptions remain in bulk metadata to preserve the size budget. Follow provided paths: index-prefixed slice slugs are
reserved for directories and use deterministic hashed slice names.
Snapshot query keys avoid old caches, not select historical data. Compare the
full snapshot identity and date, and follow the router refresh link on mismatch.
If a snapshot URL fails or the date is older than today, re-read
https://neoskx.github.io/Momentum/index.html?refresh=<YYYY-MM-DD> (today's date).
The previous two publications keep their small snapshot files (no bulk), so a
cached router's links still resolve. Read with the web page reader, not curl or a
code sandbox: claude.ai's sandbox proxy blocks neoskx.github.io unless the user
adds it under Settings → Capabilities.

# Directory and row contracts

Start at https://neoskx.github.io/Momentum/index.md and the linked catalog.
The catalog's `agent_index` has `topics_url`, `languages_url`, `keywords_url`.
L1 files are snapshot-local: resolve `shards[].path` and keyword bucket paths
against `api/v2/snapshots/<snapshot_id>/`. Slice `path` and `html_path` instead
resolve against L1 `base_url`, the site root. Prefer entry paths to guessed slugs.

L1 documents carry `entries`, `entry_count`, `base_url`, `date`, `snapshot_id`.
Each is <180,000 bytes. Large roots have empty `entries` plus
`shards: [{path, entry_count}]`; expand every shard and combine entries.
Compare date and identity at every step. Slice entries carry `repo_count`,
`gain_7d_total`, `gain_30d_total` (whole-slice known sums, null if none known).

Selection, ordered by repo count descending then label ascending for caps:

- `topics-index.json`: exact topics with >=20 repos, max 4,000; entries have
  `path`, `html_path`, up to three `related_topics` (hints, never membership).
- `languages.json`: original language labels with >=5 repos. Slugs use lowercase,
  `#` -> `sharp`, `+` -> `p`, punctuation -> `-`; hashes handle Unicode/collisions.
- `keywords-index.json`: two-letter buckets with `path: keywords/<xx>.json`.
  Buckets may shard too. Include tokens with >=20 repos and <=2% of cohort,
  max 4,000, plus every present question keyword regardless of caps/thresholds:
  sandbox, vector-database, data-analysis, browser-automation, rag, mcp, ocr,
  tts, observability, orm, coding-agent.
- Tokens: lowercase ASCII alphanumeric, begin with a letter, 2–40 characters,
  from full names (including owner), descriptions and topics; common stopwords
  removed. Question phrases match adjacent words across punctuation/whitespace.
  No stemming or semantic matching. Each repo counts once per keyword.

Missing directory entries do not prove there are no bulk matches.

Canonical L2 exists at stable `t/<slug>.{json,html}`, `l/<slug>.{json,html}` and
`k/<slug>.{json,html}` under the site root. Compact topic aliases (tiny pages
linking the full slice) may be linked from repo pages; follow their supplied URLs. There is no L2
Markdown or snapshot-directory copy. JSON is <200,000 bytes; HTML <100,000. Stable files change on publication:
compare `date` AND `snapshot_id` with the pinned catalog/L1 and restart on mismatch.

Each JSON has `matched_count`, `unknown_gain_7d_count`, and `top_by_stars`,
`top_by_gain_7d`, `top_by_gain_30d`: three ordered arrays of zero-based indices
into a deduplicated `rows` union, at most 25 per list and 75 rows in total.
Never filter that union and claim a full-cohort answer. HTML shows the top 10
of each list plus complete whole-slice filter counts and intersections; follow
repo HTML for individual facts and JSON for full slice details.

Rows expose name, language, topics, stars,
gains (1/7/30/90/365d), created_at, pushed_at, commits_30d, archived, is_fork,
owner_type, history_pending, activity_checked, whole-slice `rank_in_slice_by_stars`,
and `breakout_ratio = gains.7d / (gains.90d / 13)` (null input/zero baseline ->
unknown; negative nonzero baseline keeps its mathematical ratio).

Rank by descending measure, descending stars, case-folded name, exact name.
Exclude null gains, retain zero and negative gains. Age/creation filters use UTC
dates and capture date. Catalog `top100.gain_<N>d` offers overall window JSON and
Markdown; these are the only ranked Markdown tables, alongside the L0 router.

# Schema 2.1 full membership and retention

Daily bulk has all seven gain windows; full descriptions/topics are in
`metadata.metadata_jsonl_url`, joined by `node_id` or `full_name`. `[]` means
known no topics; null means unknown. Unknown metadata does not contribute topics.

`metadata.topic_members_url` links `topic-members.json`: verify its `snapshot_id`,
`date`, `index_base: 0`, and `jsonl_url` before joining. `topics` maps every valid
observed topic (including singletons) to sorted unique zero-based row positions
in the same daily `all.jsonl`. These are file line numbers, never L2 row indices
or weekly Parquet positions. They give full membership independent of L1 caps.
`topics_full_url` counts every observed topic; `metadata.topics_index_url`
counts topics with >=3 repos and may be null when metadata is absent.

Schema 2.1 removed `metadata.topic_url_template` and snapshot `topics/<topic>.json`.
`metadata.topic_slice_url_template` is for ranked `/t/<slug>.json`; consult L1
selection before fetching. Full membership uses the shared map and daily rows.

The public report branch is replaced by a single orphan commit each publication.
Only the latest daily snapshot and latest weekly Parquet are served in full; the
previous two keep only their small files. Older daily URLs disappear; preserve needed rows locally, not only snapshot IDs.
Weekly Parquet has its own provenance; it cannot replace an arbitrary previous
snapshot. Unsupplied historical snapshots, weekly commit counts and user dependency
lists cannot be answered from this index alone; explain the specific missing input.

Full contract: https://neoskx.github.io/Momentum/docs/agent-feed.md

Long topic links may have abbreviated labels and compact snapshot-specific
URLs; follow them for the full topic label and rankings. A compact top-topic
rank names its one-based position in the page’s topic list.
