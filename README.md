# Parking Location Quote Matching

A Python pipeline that aggregates airport parking data from multiple providers,
normalizes inconsistent schemas, matches equivalent facilities across providers,
and exports structured datasets.

This project demonstrates **entity resolution over messy third-party APIs** —
a core problem in real-world integrations.

---

## Table of Contents

- [Overview](#-overview)
- [Architecture](#%EF%B8%8F-architecture)
- [Matching Approach](#-matching-approach)
- [Setup](#%EF%B8%8F-setup)
- [Usage](#%EF%B8%8F-usage)
- [Outputs](#-outputs)
- [Testing](#-testing)
- [Assumptions & Limitations](#%EF%B8%8F-assumptions--limitations)
- [API Discovery Notes](#-api-discovery-notes)
- [Provider Schema Notes](#-provider-schema-notes)
- [Performance, Scalability & Deployment](#-performance-scalability--deployment-strategy)

---

## 🚀 Overview

Parking providers expose inconsistent APIs with:

- different field names and formats
- no shared facility identifiers
- varying address and naming conventions

This pipeline:

1. Fetches parking data from multiple providers
2. Normalizes provider-specific payloads into a shared schema
3. Stores normalized data in SQLite
4. Matches facilities across providers using heuristic scoring
5. Exports results to CSV and JSON

---

## 🏗️ Architecture

```
parking_matching/
├── run.py                  # CLI entry point and pipeline orchestration
├── requirements.txt
├── .env.example
├── app/
│   ├── config.py           # Environment-driven settings
│   ├── db.py               # SQLite storage layer
│   ├── models.py           # ParkingLot, ParkingQuote, MatchedLot dataclasses
│   ├── providers/          # Provider fetch implementations
│   │   ├── base.py         # Abstract base provider interface
│   │   ├── parkwhiz.py     # ParkWhiz (real API + mock fallback)
│   │   ├── spothero.py     # SpotHero (mock)
│   │   └── cheap_airport_parking.py  # CheapAirportParking (mock)
│   ├── normalize/          # Schema normalization
│   │   ├── text.py         # Text cleaning, abbreviation expansion
│   │   ├── facility.py     # Raw record → ParkingLot
│   │   └── quote.py        # Raw record → ParkingQuote
│   ├── matching/
│   │   └── matcher.py      # Pairwise scoring and classification
│   └── export/
│       └── exporter.py     # CSV + JSON export
├── data/
│   ├── raw/                # Raw provider responses (timestamped)
│   └── output/             # Exported CSV and JSON files
└── tests/
    ├── test_matching.py
    └── test_text_normalization.py
```

### Key components

#### Providers (`app/providers/`)

- Each provider implements a common interface
- Currently uses **mocked data** simulating real API responses
- Designed to be easily replaced with real API integrations

#### Normalization (`app/normalize/`)

- Converts provider-specific fields into a unified schema
- Cleans text (addresses, names, abbreviations)
- Ensures consistent comparison across providers

#### Storage (`app/db.py`)

- SQLite database for:
  - normalized parking lots
  - quotes
  - match results
- Stores raw payloads for **traceability/debugging**
- Raw provider responses are also persisted under `data/raw/` for reproducibility, debugging, and inspection of provider-specific payloads.

#### Matching (`app/matching/`)

- Performs **pairwise facility matching**
- Uses a weighted heuristic over:
  - name similarity
  - address similarity
  - geographic distance
  - city/state/postal matches
- Produces:
  - `match`
  - `possible_match`
  - `no_match`

#### Export (`app/export/`)

- Outputs structured datasets to:
  - CSV
  - JSON

#### Models (`app/models.py`)

- Data models
  - ParkingLot
  - ParkingQuote
  - MatchedLot

---

## 🧠 Matching Approach

This project treats the problem as **entity resolution across heterogeneous datasets**.

### Step 1: Candidate filtering

Only compare:

- facilities from the same airport
- facilities from different providers

### Step 2: Scoring

Each pair is scored using:

| Signal                    | Weight |
| ------------------------- | ------ |
| Name similarity           | 0.40   |
| Address similarity        | 0.30   |
| Geo distance              | 0.20   |
| Locality (city/state/zip) | 0.10   |

### Step 3: Classification

| Score       | Result         |
| ----------- | -------------- |
| ≥ 0.85      | match          |
| 0.65 – 0.85 | possible_match |
| < 0.65      | no_match       |

---

### Example Match Output

Example of matched facilities across providers:

| Provider A          | Provider B                      | Score | Decision       | Reason                                                             |
| ------------------- | ------------------------------- | ----- | -------------- | ------------------------------------------------------------------ |
| ParkWhiz (pw_ord_1) | SpotHero (sh_ord_1)             | 0.92  | match          | high name similarity; same postal code; near-identical geolocation |
| ParkWhiz (pw_ord_2) | CheapAirportParking (cap_ord_2) | 0.78  | possible_match | moderate name similarity; nearby geolocation                       |
| ParkWhiz (pw_ord_3) | SpotHero (sh_ord_3)             | 0.42  | no_match       | weak overall similarity                                            |

The `reason` field helps explain why two facilities were or were not matched.

---

## ⚙️ Setup

**Prerequisites:**

- `Python` 3.11+
- `pip` (or any virtual-environment tool)

**Install:**

```bash
git clone https://github.com/payamdowlatyari/parking_matching.git
cd parking_matching
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Configure credentials:**

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

> **Note:** The pipeline works out of the box without any API keys.
> All providers fall back to realistic mock data when credentials are missing.
> Set `*_USE_MOCK_FALLBACK=true` in `.env` to explicitly use mock data for a provider.

## ▶️ Usage

**Run the full pipeline** (fetch → match → export):

```bash
python run.py pipeline \
  --airports ORD LAX \
  --start "2026-03-28T10:00:00" \
  --end "2026-03-30T18:00:00"
```

**Run individual steps:**

```bash
# Fetch from providers, normalize, and store in SQLite
python run.py fetch --airports ORD LAX \
  --start "2026-03-28T10:00:00" --end "2026-03-30T18:00:00"

# Run pairwise matching on stored lots
python run.py match

# Export lots, quotes, and matches to CSV + JSON
python run.py export
```

All commands accept `--db-path` to specify a custom database file (default: `parking_matching.db`).

## 📦 Outputs

**Results:**

- `data/output/`: Lots, quotes, and matched parkings
- `data/raw/`: Raw fetch artifacts

**Console Output:**

```
Fetched 3 records from parkwhiz for ORD -> raw saved to data/raw/parkwhiz_ORD_20260324T001526Z.json
Fetched 3 records from spothero for ORD -> raw saved to data/raw/spothero_ORD_20260324T001526Z.json
Fetched 3 records from cheap_airport_parking for ORD -> raw saved to data/raw/cheap_airport_parking_ORD_20260324T001526Z.json
[parkwhiz] Real API attempt failed for LAX: PARKWHIZ_API_TOKEN is not set
[parkwhiz] Using mock fallback for LAX
Fetched 3 records from parkwhiz for LAX -> raw saved to data/raw/parkwhiz_LAX_20260324T001526Z.json
Fetched 3 records from spothero for LAX -> raw saved to data/raw/spothero_LAX_20260324T001526Z.json
Fetched 3 records from cheap_airport_parking for LAX -> raw saved to data/raw/cheap_airport_parking_LAX_20260324T001526Z.json
Stored 54 match results
Exported parking lots to:
  - data/output/parking_lots.json
  - data/output/parking_lots.csv
Exported parking quotes to:
  - data/output/parking_quotes.json
  - data/output/parking_quotes.csv
Exported matched lots to:
  - data/output/matched_lots.json
  - data/output/matched_lots.csv
```

**Example Matched Results:**

```
[
  {
    "airport_code": "ORD",
    "left_provider": "parkwhiz",
    "left_lot_id": "pw_ord_3",
    "right_provider": "cheap_airport_parking",
    "right_lot_id": "cap_ord_2",
    "score": 0.3891,
    "decision": "no_match",
    "reason": "same city; same state; same postal code"
  },
  {
    "airport_code": "ORD",
    "left_provider": "parkwhiz",
    "left_lot_id": "pw_ord_3",
    "right_provider": "cheap_airport_parking",
    "right_lot_id": "cap_ord_3",
    "score": 0.8467,
    "decision": "possible_match",
    "reason": "high address similarity; near-identical geolocation; same city; same state"
  },
  {
    "airport_code": "ORD",
    "left_provider": "spothero",
    "left_lot_id": "sh_ord_1",
    "right_provider": "cheap_airport_parking",
    "right_lot_id": "cap_ord_1",
    "score": 0.9556,
    "decision": "match",
    "reason": "moderate name similarity; high address similarity; near-identical geolocation; same city; same state; same postal code"
  },
  ...
]
```

## 🧪 Testing

Run the full test suite:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

### What's tested

| Area               | Tests   | Description                                                                                                                  |
| ------------------ | ------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Text normalization | 7 tests | Punctuation removal, whitespace collapsing, abbreviation expansion, weak token removal, postal code cleanup, `None` handling |
| Matching scoring   | 4 tests | Similar lots → `match`, different lots → `no_match`, missing geo data handling, same-provider pair skipping                  |

---

## ⚠️ Assumptions & Limitations

- Matching is heuristic-based, not guaranteed perfect
- Some facilities may have missing addresses or coordinates
- Some facilities may represent multiple parking products (valet vs self-park) under one location
- Matching is tuned to prioritize **precision over recall** — high-confidence matches are reliable while ambiguous cases are surfaced as `possible_match`
- Mock data is used instead of real APIs (except ParkWhiz, which attempts real API calls before falling back to mocks)

---

## 🔍 API Discovery Notes

To simulate real-world provider integrations, I explored how each recommended provider exposes search/quote data. The goal was to understand how their APIs differ and design a system that can handle those inconsistencies.

### ParkWhiz

- Discovery method: Official documentation and public developer resources
- Observations:
  - Structured API with clear concepts like listings and quotes
  - Consistent use of IDs for facilities and rates
  - Includes geolocation and pricing in a predictable format
- Takeaway:
  - Easiest provider to integrate due to relatively clean schema

---

### SpotHero

- Discovery method: Public developer platform and browser network inspection
- Observations:
  - Uses “facility” and “rate” concepts similar to ParkWhiz but with different field names
  - Address and location fields differ slightly (e.g., municipality vs city)
  - Some fields (e.g., postal code) may be missing or null
- Takeaway:
  - Structurally similar to ParkWhiz but requires field mapping and null handling

---

### Cheap Airport Parking

- Discovery method: Browser network panel (XHR requests from search flow)
- Observations:
  - Less formalized API surface compared to other providers
  - Nested structures (e.g., geo and pricing objects)
  - Inconsistent naming conventions (e.g., `title`, `address_1`, `city_name`)
  - Some fields may be optional or missing
- Takeaway:
  - Represents a more “messy” real-world integration where normalization is critical

---

## 📓 Provider Schema Notes

Although all providers are normalized into a shared internal schema, each one exposes different provider-specific fields. The normalization layer extracts the stable fields needed for matching and storage, while preserving the full source payload in `raw_payload`.

### ParkWhiz

Modeled to reflect a documented quote/location-style API.

Typical fields include:

- facility/location identifiers
- quote identifiers
- address and geolocation
- total price and currency
- bookability
- site URL
- phone
- capacity
- hours / operating hours
- non-bookable rates

Example provider-specific fields preserved in `raw_payload`:

- `is_bookable`
- `site_url`
- `phone`
- `capacity`
- `hours`
- `operating_hours`
- `non_bookable_rates`

### SpotHero

Modeled to reflect a partner-style marketplace search result.

Typical fields include:

- facility and rate identifiers
- formatted pricing
- amenities
- refundability
- inventory status
- review metadata
- shuttle cadence
- distance to airport

Example provider-specific fields preserved in `raw_payload`:

- `display_price`
- `amenities`
- `review_score`
- `review_count`
- `shuttle_frequency_minutes`
- `distance_to_airport_miles`
- `is_refundable`
- `inventory_status`

### Cheap Airport Parking

Modeled to reflect a website-driven airport parking comparison result.

Typical fields include:

- lot identifiers
- nested pricing data
- parking type
- shuttle details
- reviews
- cancellation policy

Example provider-specific fields preserved in `raw_payload`:

- `pricing.display_total`
- `pricing.daily_from`
- `lot_type`
- `parking_type`
- `airport_shuttle`
- `reviews`
- `free_cancellation`

### Why preserve provider-specific fields?

Keeping the full raw provider payload makes the system easier to:

- **Debug** when upstream schemas change
- **Inspect** mapping assumptions during development
- **Enrich** the normalized model later without re-fetching data
- **Explain** matching decisions using source-specific context

---

### Key Challenges Identified

Across providers, several inconsistencies required normalization:

- **No shared facility identifiers**
  → Required heuristic matching instead of direct joins

- **Different field names**
  → e.g., `location_name` vs `facility_name` vs `title`

- **Address formatting differences**
  → `St` vs `Street`, punctuation, casing

- **Geolocation variance**
  → Slight differences in lat/lng precision across providers

- **Missing or partial data**
  → Some providers omit postal codes or coordinates

---

### Design Implications

These observations directly informed the system design:

- Introduced a **provider abstraction layer**
- Built a **normalization step** before any matching
- Used **weighted heuristic scoring** instead of relying on IDs
- Preserved **raw payloads** for traceability and debugging

---

### Note on Implementation

For this take-home, I implemented **mocked provider responses** that reflect real-world inconsistencies observed during API discovery.

The architecture is designed so that:

- mocked providers can be easily replaced with real HTTP integrations
- normalization and matching logic remain unchanged

---

### Real ParkWhiz integration

The ParkWhiz provider is structured to attempt a real API call first using the documented v4 `GET /quotes` endpoint, then fall back to mocked data if credentials are unavailable or the request fails. This keeps the demo runnable while preserving a clean migration path to real provider integrations.

---

## ⚡ Performance, Scalability & Deployment Strategy

The parking matching pipeline is designed as a modular, event-driven data workflow that separates ingestion, normalization, matching, and export into independent stages. This architecture ensures the system is reliable, scalable, and easy to extend as new providers are added.

Rather than running as a single monolithic script, the pipeline can be deployed as a series of orchestrated steps using cloud-native services.

---

### Performance & Scalability

The current implementation performs pairwise comparisons `(O(n²))` within each airport.

For larger datasets, this can be optimized by:

- **Blocking / candidate filtering**
  - Only compare facilities within a geographic radius or same postal code
- **Geospatial indexing**
  - Use PostGIS or Elasticsearch for efficient spatial queries
- **Parallel processing**
  - Run matching jobs per airport or batch in parallel

The architecture isolates matching logic, making these optimizations easy to introduce without changing ingestion or normalization layers.

---

### Proposed Cloud Architecture (AWS)

#### Core components:

- **Amazon S3** — stores raw, normalized, and final datasets
- **AWS Lambda** — executes lightweight processing steps (provider ingestion, normalization)
- **AWS Step Functions** — orchestrates the pipeline workflow
- **Amazon SQS** — buffers tasks and enables retries between stages
- **Database (PostgreSQL / DynamoDB)** — stores matched parking lots and pipeline metadata
- **CloudWatch** — logging, monitoring, and alerting

#### Pipeline flow:

1. **Trigger**
   - Scheduled via EventBridge (cron) or manual trigger
2. **Ingestion**
   - Fetch data from providers (SpotHero, ParkWhiz, etc.)
   - Store raw responses in S3
3. **Normalization**
   - Convert provider-specific formats into a unified schema
   - Output normalized data to S3
4. **Matching / Deduplication**
   - Identify duplicate parking lots across providers
   - Apply matching logic (e.g., location proximity, name similarity)
5. **Export**
   - Write results to CSV/JSON or persist in a database

#### Pipeline Diagram:

```
Trigger (EventBridge / Manual)
            │
            ▼
   Step Functions Orchestrator
            │
    ┌───────┼────────┐
    ▼       ▼        ▼
Provider  Provider  Provider
  A         B         C
    \       |        /
     ▼      ▼       ▼
        Raw Data (S3)
              │
              ▼
     Normalization Step
              │
              ▼
      Normalized Data (S3)
              │
              ▼
     Matching / Deduplication
              │
              ▼
        Final Results
        /           \
   CSV/JSON        Database
```

---

### Reliability Considerations

The system is designed to handle failures gracefully and ensure data integrity:

- **Idempotent processing:**
  Re-running any stage does not create duplicate records
- **Retry mechanisms:**
  Transient API failures are retried with exponential backoff
- **Fault isolation:**
  Each provider ingestion runs independently (one failure doesn’t break the pipeline)
- **Checkpointing:**
  Intermediate outputs are stored in S3, allowing partial restarts
- **Dead-letter queues (DLQ):**
  Failed messages are captured for later inspection
- **Run metadata tracking:**
  Each pipeline execution includes run IDs, timestamps, and status logs

---

### Scalability Strategy

The architecture is designed to scale with increasing data volume and provider count:

- **Parallel ingestion:**
  Each provider is processed independently and concurrently
- **Distributed normalization:**
  Data transformations scale horizontally via Lambda or batch jobs
- **Partitioned matching:**
  Matching can be segmented by geography (e.g., airport/city) or dataset size
- **Stateless compute:**
  Lambda-based processing enables automatic scaling without infrastructure management
- **Storage-first design:**
  Intermediate data persisted in S3 avoids memory bottlenecks

---

### Extensibility

The pipeline is built to easily support additional providers and features:

- **Provider adapter pattern:**
  Each provider implements a standard interface (fetch → normalize)
- **Config-driven providers:**
  Providers can be enabled/disabled without code changes
- **Versioned matching logic:**
  Matching algorithms can evolve while maintaining reproducibility
- **Schema standardization:**
  Ensures consistent downstream processing

---

### Local vs Production Setup

- **Local development**
  - Run pipeline as a CLI script
  - Use SQLite or local files for storage
- **Production**
  - Deploy using **AWS services (Step Functions + Lambda)**
  - Use **S3** for storage and **Postgres/DynamoDB** for persistence

---

### Design Philosophy

This system prioritizes:

- Separation of concerns (clear pipeline stages)
- Observability (logs, metrics, traceable runs)
- Resilience (retries, fault isolation)
- Scalability (parallel and distributed processing)

---

### Future Improvements

- Replace mocked providers with real API integrations
- Add geospatial indexing for faster matching
- Introduce clustering (multi-provider grouping)
- Add confidence calibration or ML-based matching
- Visualize matches on a map

---

### AI Usage

- **ChatGPT / GitHub Copilot**
  - Assisted with high-level architecture exploration and iterative development
  - Helped refine data modeling, pipeline structure, and documentation clarity
  - Accelerated implementation of well-understood patterns without replacing core reasoning
- **Claude**
  - Used primarily as a code reviewer and design sounding board
  - Identified potential edge cases, failure scenarios, and areas for improvement
  - Provided alternative implementations and highlighted trade-offs between approaches
  - Helped validate that the solution aligns with production-oriented best practices

AI tools were used as engineering assistants, not as sources of truth. All key decisions, system design, and implementation details were critically evaluated and finalized independently to ensure correctness, reliability, and clarity.

---

### Summary

This project demonstrates:

- API integration across heterogeneous providers
- schema normalization and data modeling
- entity resolution using explainable heuristics
- pragmatic tradeoffs between accuracy, complexity, and scalability

The system is designed to be extensible, debuggable, and production-ready with minimal changes.
