# Muted hashes

`muted_hashes.tsv` lists INSDC updates that ingest should ignore. Ingest downloads it from
`https://pathoplexus.github.io/curation_data/muted_hashes/muted_hashes.tsv` on each run. If an incoming record's hash
matches an entry for that Loculus accession, ingest skips it as a no-op. The record is not revised, not blocked, and no
"has been curated before" Slack notification is sent.

This is mainly for curated sequences where an upstream INSDC change shouldn't overwrite the curation.

## Columns

| column        | description                                                                 |
| ------------- | --------------------------------------------------------------------------- |
| `accession`   | Loculus accession **without version**, e.g. `PP_000QFTH` (not the INSDC accession) |
| `hash_digest` | the **new** hash of the incoming INSDC record (not the old hash)            |
| `date`        | date the entry was added (`YYYY-MM-DD`)                                     |
| `comment`     | link to the relevant `curation_reports` issue                               |

## Muting a notification

Given a Slack message like:

```
Ingest: Sequence PP_000QFTH with INSDC accession KT384388 has been curated before - do not know how to proceed.
New hash: 20026e7718839e261c9101bd465734fc, old hash: cd617fe2e5e9f0a31460b8b4c0d61a0b. Metadata diff: {...}
```

add a tab-separated row with the Loculus accession and the **New hash**:

```
PP_000QFTH	20026e7718839e261c9101bd465734fc	2026-11-24	https://github.com/pathoplexus/curation_reports/issues/12
```

Then open a PR. The mute takes effect on the first ingest run after it is merged and published.

## Notes

- A mute matches one exact update. If INSDC changes the record again, it gets a new hash and you'll need to add another
  row. You can't mute a whole accession.
- One accession can have several rows (several muted hashes).
- Segmented organisms: muting works when the segment grouping is unchanged or new segments are added. If the grouping
  changes, the record is revoked and the mute is not checked.
