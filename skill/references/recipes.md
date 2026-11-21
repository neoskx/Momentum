# Python stdlib: fetch, pin, route

Use Python 3; no third-party dependency is needed for JSON or JSONL.

```python
import json
from urllib.parse import urljoin
from urllib.request import urlopen

BASE = "https://neoskx.github.io/Momentum/"
def fetch(url):
    with urlopen(url, timeout=90) as response:
        return response.read().decode("utf-8")
def read(url):
    return json.loads(fetch(url))

router = fetch(urljoin(BASE, "index.md"))  # L0
cat = read(urljoin(BASE, "api/v2/catalog.json"))
sid, date = cat["snapshot_id"], cat["date"]
SNAP = urljoin(BASE, f"api/v2/snapshots/{sid}/")
def directory(url):
    doc = read(url)
    assert (doc["snapshot_id"], doc["date"]) == (sid, date)
    entries = dict(doc["entries"])
    for shard in doc.get("shards", []):
        entries.update(directory(urljoin(SNAP, shard["path"]))["entries"])
    return {**doc, "entries": entries}

topic_dir = directory(cat["agent_index"]["topics_url"])  # L1
topics = topic_dir["entries"]
if "sandbox" in topics:
    page = read(urljoin(topic_dir["base_url"], topics["sandbox"]["path"]))  # L2
    assert (page["snapshot_id"], page["date"]) == (sid, date)
    rows = page["rows"]
    print("total stars", date, sid, "matched", page["matched_count"])
    for index in page["top_by_stars"][:3]:
        print(rows[index]["full_name"], rows[index]["stars"])
```

For language paths use the language directory; for a lexical keyword open its
bucket from `keywords_url` and expand any shards. For browse-only agents, open
`html_path` against directory `base_url`. L2 has no Markdown. If an identity
assertion fails, restart from the catalog; a publication may have replaced a
stable slice. For weekly/monthly rankings use `top_by_gain_7d` or
`top_by_gain_30d`, also zero-based indices (top 25 each).

# Daily L3: metadata join, full filter, ranking, CSV

Continue with the pinned catalog above. Download once and reuse. For very large
cohorts, stream response lines rather than collecting decoded text first.

```python
import csv

def jsonl(url):
    with urlopen(url, timeout=90) as response:
        for line in response:
            if line.strip():
                yield json.loads(line)

meta = {r["node_id"]: r for r in jsonl(cat["metadata"]["metadata_jsonl_url"])}
members = read(cat["metadata"]["topic_members_url"])
assert (members["snapshot_id"], members["date"]) == (sid, date)
assert members["index_base"] == 0 and members["jsonl_url"] == cat["jsonl_url"]
positions = set(members["topics"].get("sandbox", []))  # full membership, not top 25
matched = []
for position, record in enumerate(jsonl(cat["jsonl_url"])):
    info = meta.get(record["node_id"], {})
    # Exact topic positions are meaningful only in this daily file order.
    if position in positions:
        matched.append({**record, "description": info.get("description"),
                        "topics": info.get("topics")})
known = [r for r in matched if r["gains"].get("30d") is not None]
known.sort(key=lambda r: (-r["gains"]["30d"], -r["stars"],
                          r["full_name"].casefold(), r["full_name"]))
print("30-day star gain", "matched", len(matched), "unknown", len(matched)-len(known), sid, date)
for r in known[:3]:
    print(r["full_name"], r["gains"]["30d"])
with open("sandbox.csv", "w", newline="") as output:
    writer = csv.writer(output)
    writer.writerow(["full_name", "stars", "gain_30d", "created_at", "pushed_at"])
    for r in matched:  # every match, including unknown gains
        values = [r["full_name"], r["stars"], r["gains"].get("30d"), r["created_at"], r["pushed_at"]]
        # Empty CSV cells mean unknown; guard untrusted spreadsheet text.
        writer.writerow(["'"+v if isinstance(v, str) and v.startswith(("=", "+", "-", "@")) else v for v in values])
```

Never filter a top-100 or L2 selection for a complete filtered answer.
For keyword unions, compute lexical membership on all metadata/name tokens,
deduplicate by node_id, then filter and rank. Use the token/phrase and stopword
rules in routing.md; no stemming. Use full bulk descriptions, not L2 excerpts.
State the exact interpretation. The removed snapshot topics/<topic>.json files
must not be used; even singleton topics are in the shared membership map.

# Optional weekly Parquet with DuckDB or PyArrow

Parquet is optional. Check `parquet_url` and `parquet` for null first. Its own
`date` and `snapshot_id` may differ from the daily catalog. Download to a local
file using the URL, verify byte length and SHA-256 from `cat["parquet"]`, and
cite those weekly identifiers for weekly results. Do not silently join weekly
stars to daily metadata and label them as a single daily snapshot.

```python
import hashlib
from pathlib import Path
if cat.get("parquet_url"):
    with urlopen(cat["parquet_url"], timeout=90) as response:
        blob = response.read()
    provenance = cat["parquet"]
    assert len(blob) == provenance["bytes"]
    assert hashlib.sha256(blob).hexdigest() == provenance["sha256"]
    Path("all.parquet").write_bytes(blob)
    print(provenance["snapshot_id"], provenance["date"])
```

Optional install: `python3 -m pip install duckdb` or `python3 -m pip install pyarrow`.

```python
import duckdb
print(duckdb.sql("""
    SELECT full_name, stars, gains."7d" AS gain_7d
    FROM read_parquet('all.parquet')
    WHERE gains."7d" IS NOT NULL
    ORDER BY gain_7d DESC, stars DESC, lower(full_name), full_name LIMIT 3
""").fetchall())
```

```python
import pyarrow.parquet as pq
rows = pq.read_table("all.parquet").to_pylist()  # nullable fields remain None
```
