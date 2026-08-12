# HRH deficit queries

BigQuery (standard SQL) queries that produce the health-workforce population
estimates behind the AAAQ HRH deficit analysis. They read the NSS microdata
tables under `asar-287123.nss.*` and were moved here from the `asar-data`
repo (`misc/`), which was the common repo before this one.

## Per-round queries

Each file estimates, for one NSS round, the weighted population of health
workers by state and occupation, split into total and formally qualified.

| File | NSS round | Source tables | Occupation coding |
| --- | --- | --- | --- |
| `38.sql` | 38 | `nss_38_block_6`, `nss_38_block_41` | NCO-1968 |
| `50.sql` | 50 | `nss_50_block_4` | NCO-1968 |
| `55.sql` | 55 | `nss_55_block_512/521/522/41` | NCO-1968 |
| `68.sql` | 68 | `nss_68_block_51/52/4` | NCO-2004 + NIC |

Rounds 38–55 share the same shape: temp functions map NCO codes to cadres
(round 50 needs no join — occupation and education both live in block 4)
(Doctor, Dentist, AYUSH, Nurse, ANM, Pharmacist) and education codes to
attainment levels, then `is_qualified()` decides whether a worker holds the
credential their cadre requires. Three CTEs follow — worker rows, household
rollup (weights applied once per household), and the weighted state ×
occupation estimate.

Round 68 differs because the coding scheme changed: `occupation_code()` takes
both the NCO-2004 occupation and the NIC industry code, since the occupation
code alone no longer separates cadres. There is no general educational
attainment mapping for this round; `is_qualified()` uses technical education
only.

## Superseded files

Kept for provenance; not part of the current pipeline.

- `06_FEB_2022_AAAQ_HRH_Deficit.sql` — earlier query covering rounds 38, 50 and
  55 in one file. Note its final `SELECT` reads `estimates_38`, so the round-50
  and round-55 CTEs it defines are never returned; it also predates the
  qualified/unqualified split and reports total population only.
- `hrh-query.sql` — the original prototype that `38.sql` grew out of. Identical
  apart from carrying no `state_` column, so it yields national totals per
  occupation rather than a state breakdown.
