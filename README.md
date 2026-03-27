# 🚗 Parking Location Quote Matching

A data pipeline that aggregates parking availability from multiple providers, normalizes inconsistent schemas, and matches facilities across providers into canonical parking locations.

---

## Table of Contents

- [Overview](#-overview)
- [Architecture](#%EF%B8%8F-architecture)
- [Matching Approach](#-matching-approach)
- [Setup, Usage & Outputs](#setup)
- [Testing](#-testing)
- [Assumptions & Limitations](#%EF%B8%8F-assumptions--limitations)
- [API Discovery & Provider Schemas](#-api-discovery--provider-schemas)
- [Performance, Scalability & Deployment](#-performance-scalability--deployment-strategy)
- [AI Usage](#-ai-usage)
- [Summary](#-summary)

---

## 🚀 Overview

Parking providers expose inconsistent APIs with no shared identifiers. This pipeline:

1. **Fetches** parking data from multiple providers (ParkWhiz, SpotHero, CheapAirportParking)
2. **Normalizes** provider-specific payloads into a unified schema
3. **Stores** normalized data in SQLite
4. **Matches** equivalent facilities across providers using heuristic scoring
5. **Exports** deduplicated results to CSV and JSON

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
│   │   ├── parkwhiz.py     # ParkWhiz (live API)
│   │   ├── spothero.py     # SpotHero (restricted API)
│   │   └── cheap_airport_parking.py  # CheapAirportParking (HTML scrapping)
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
- Use live API where available (ParkWhiz)
- Handle restricted APIs (SpotHero) via scraping fallback
- Adapt to fully unstructured sources (CheapAirportParking)

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
  - **ParkingLot**
  - **ParkingQuote**
  - **MatchedLot**

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

### Example Match Output

Example of matched facilities across providers:

| Provider A          | Provider B                      | Score | Decision       | Reason                                                             |
| ------------------- | ------------------------------- | ----- | -------------- | ------------------------------------------------------------------ |
| ParkWhiz (pw_ord_1) | SpotHero (sh_ord_1)             | 0.92  | match          | high name similarity; same postal code; near-identical geolocation |
| ParkWhiz (pw_ord_2) | CheapAirportParking (cap_ord_2) | 0.78  | possible_match | moderate name similarity; nearby geolocation                       |
| ParkWhiz (pw_ord_3) | SpotHero (sh_ord_3)             | 0.42  | no_match       | weak overall similarity                                            |

The `reason` field helps explain why two facilities were or were not matched.

---

## ⚙️ Setup, Usage & Outputs

### Setup

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

### Usage

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

### Outputs

**Results:**

- `data/output/`: Lots, quotes, and matched parkings
- `data/raw/`: Raw fetch artifacts

**Console Output:**

```
Fetched 3 records from parkwhiz for ORD -> raw saved to data/raw/parkwhiz_ORD_...json
Fetched 3 records from spothero for ORD -> ...
Fetched 3 records from cheap_airport_parking for ORD -> ...
...
Stored 54 match results
Exported parking lots to:
  - data/output/parking_lots.json
  - data/output/parking_lots.csv
Exported matched lots to:
  - data/output/matched_lots.json
  - data/output/matched_lots.csv
```

**Example Match Result:**

```json
{
  "airport_code": "ORD",
  "left_provider": "spothero",
  "left_lot_id": "sh_ord_1",
  "right_provider": "cheap_airport_parking",
  "right_lot_id": "cap_ord_1",
  "score": 0.9556,
  "decision": "match",
  "reason": "moderate name similarity; high address similarity; near-identical geolocation; same city; same state; same postal code"
}
```

---

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
| Text normalization | 6 tests | Punctuation removal, whitespace collapsing, abbreviation expansion, weak token removal, postal code cleanup, `None` handling |
| Matching scoring   | 4 tests | Similar lots → `match`, different lots → `no_match`, missing geo data handling, same-provider pair skipping                  |

---

## ⚠️ Assumptions & Limitations

- Matching is heuristic-based, not guaranteed perfect
- Some facilities may have missing addresses or coordinates
- Some facilities may represent multiple parking products (valet vs self-park) under one location
- Matching is tuned to prioritize **precision over recall** — high-confidence matches are reliable while ambiguous cases are surfaced as `possible_match`

---

## 🔍 API Discovery & Provider Schemas

Parking providers do not consistently expose public or well-documented APIs.

To integrate multiple providers, this project uses a combination of:

- Official documentation (when available)
- Browser network inspection (Chrome DevTools)
- Reverse-engineered API requests
- HTML scraping as a fallback

### ParkWhiz

- **Discovery:** Official docs + network inspection of ParkWhiz search flows
- **Endpoint:**:
  - `GET https://api.parkwhiz.com/v4/quotes/`
- **Schema:** Well-structured JSON with consistent fields:
  - `location.name`
  - `price`
  - `distance`
- **Integration:**
  - Real API calls implemented and working
  - No API key required for basic queries
- **Notes:** Most reliable and complete data source in the pipeline

### SpotHero

- **Discovery:**
  - SpotHero developer portal requires partner access
  - Used DevTools to inspect XHR requests from the search page
- **Observed Behavior:**
  - Internal API endpoints exist but require:
  - Session cookies
  - Specific headers
  - Direct requests return empty results
- **Fallback Approach:**
  - Scraped results from:
    - `https://spothero.com/search?kind=airport&id=SFO&airport=true`
- **Schema:**
  - Nested structure requiring flattening
  - Inconsistent fields:
    - `municipality` vs `city`
    - nullable postal codes
- **Integration:**
  - HTML scraping used as a fallback
  - Parsed fields:
    - `name`
    - `price`
    - `rating` (if available)
- **Limitations:**
  - Fragile to frontend changes
  - Less structured than API-based providers

### Cheap Airport Parking

- **Discovery:**
  - No public API or XHR endpoints found for CheapAirportParking
  - Data appears server-rendered
- **Approach:**
  - HTML scraping with text parsing
- **Schema:**
  - Inferred from UI content
  - Highly inconsistent fields:
    - `title`
    - `address_1`
    - `city_name`
- **Integration:**
  - Flexible adapter designed to handle unstructured input
  - Currently returns limited results depending on page structure
- **Challenges:**
  - Data embedded in raw text blocks
  - Difficult to reliably extract structured listings

### Key Challenges

| Challenge                      | Example                                         | Solution                                         |
| ------------------------------ | ----------------------------------------------- | ------------------------------------------------ |
| No shared facility identifiers | Each provider uses its own ID scheme            | Heuristic matching instead of direct joins       |
| Different field names          | `location.name` vs `municipality` vs `title`    | Provider-specific normalization layer            |
| Address formatting differences | `St` vs `Street`, punctuation, casing           | Text normalization with abbreviation expansion   |
| Geolocation variance           | Slight lat/lng precision differences            | Haversine distance with tolerance bands          |
| Missing or partial data        | Some providers omit postal codes or coordinates | Graceful fallback (score 0.0 for missing fields) |
| Anti-scraping / blocked APIs   | SpotHero requires session headers               | Scraping fallback + resilient parsing            |

---

## ⚡ Performance, Scalability & Deployment Strategy

The parking matching pipeline is designed as a modular, event-driven data workflow that separates ingestion, normalization, matching, and export into independent stages. This architecture ensures the system is reliable, scalable, and easy to extend as new providers are added.

Rather than running as a single monolithic script, the pipeline can be deployed as a series of orchestrated steps using cloud-native services.

### Performance & Scalability

The current implementation performs pairwise comparisons `O(n²)` within each airport.

For larger datasets, this can be optimized by:

- **Blocking / candidate filtering**
  - Only compare facilities within a geographic radius or same postal code
- **Geospatial indexing**
  - Use PostGIS or Elasticsearch for efficient spatial queries
- **Parallel processing**
  - Run matching jobs per airport or batch in parallel

The architecture isolates matching logic, making these optimizations easy to introduce without changing ingestion or normalization layers.

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

### Local vs Production Setup

- **Local development**
  - Run pipeline as a CLI script
  - Use SQLite or local files for storage
- **Production**
  - Deploy using **AWS services (Step Functions + Lambda)**
  - Use **S3** for storage and **Postgres/DynamoDB** for persistence

### Design Philosophy

This system prioritizes:

- Separation of concerns (clear pipeline stages)
- Observability (logs, metrics, traceable runs)
- Resilience (retries, fault isolation)
- Scalability (parallel and distributed processing)

### Future Improvements

- Implement hybrid matching using LLM
- Add geospatial indexing for faster matching
- Introduce clustering (multi-provider grouping)
- Visualize matches on a map

### LLM-Assisted Matching

The current matching system relies on deterministic rules and weighted scoring (name, address, geographic proximity), which provides strong reliability and explainability. However, this approach can struggle with highly inconsistent or ambiguous provider data.

A natural evolution is to introduce a hybrid matching architecture that incorporates embeddings and LLMs to improve accuracy for edge cases.

### Hybrid Matching Architecture

The proposed approach extends the existing pipeline rather than replacing it:

1. **Deterministic Candidate Generation**
   - Filter records by geography and metadata
   - Limit comparisons to likely matches for efficiency
2. **Rule-Based Scoring**
   - Compute similarity using name, address, geographic distance
   - Automatically accept or reject high-confidence cases
3. **LLM / Embedding Layer (Selective)**
   - Applied only to borderline matches
   - Uses semantic similarity to evaluate ambiguous records
4. **Final Decision Layer**
   - Enforces hard constraints (e.g., geo distance thresholds)
   - Ensures consistency and prevents incorrect matches

### Enhancements Enabled by LLMs

**Semantic Similarity (Embeddings)**

- Captures meaning beyond exact string matching
- Handles variations like: “SFO Garage Parking” vs “San Francisco Airport Garage”

**Pairwise Evaluation (LLM)**

- Evaluates whether two records refer to the same real-world entity
- Provides structured outputs (match, confidence, reasoning)

**Data Normalization**

- Standardizes messy provider inputs
- Extracts structured fields (e.g., airport codes, address formats)

---

## 🔦 AI Usage

AI tools were used selectively to support development of the parking matching pipeline, with a focus on improving code quality, validating matching logic, and refining system design.

- **ChatGPT / GitHub Copilot**
  - Assisted with designing the overall pipeline architecture (ingestion → normalization → matching → export)
  - Helped refine the data model, including separation between provider records and canonical parking lots
  - Accelerated implementation of common patterns such as data transformation, scoring logic, and modular structure
  - Improved documentation clarity and organization of the `README`
- **Claude**
  - Used primarily as a code reviewer and design sounding board
  - Reviewed the matching strategy, including scoring signals (name, address, geo) and threshold decisions
  - Identified edge cases such as inconsistent provider data, missing fields, and false-positive matches
  - Suggested alternative approaches for entity resolution and pipeline structuring
  - Helped validate that the solution is robust, extensible, and aligned with production-oriented data pipelines

AI tools were used as engineering assistants, not as sources of truth. All matching logic, system design decisions, and final implementations were critically evaluated and validated independently to ensure correctness, reliability, and clarity.

---

## ✅ Summary

This project is a data pipeline that aggregates parking listings from multiple providers, normalizes inconsistent schemas, and matches duplicate facilities across sources.

The system integrates data from ParkWhiz, SpotHero, and CheapAirportParking using a mix of real API calls, reverse-engineered endpoints, and HTML scraping. Because providers expose data differently (or not at all), the pipeline is designed to be resilient to incomplete, inconsistent, and unstructured inputs.

Core capabilities include:

- **Multi-source ingestion:** Fetches parking data from heterogeneous providers
- **Schema normalization:** Standardizes fields like name, price, and location
- **Deduplication & matching:** Uses heuristics (name similarity + geolocation) to identify the same facility across providers
- **Extensible architecture:** Easily add new providers via a common interface
- **Export support:** Outputs matched results to CSV or JSON

This project demonstrates real-world challenges in third-party data integration, including API discovery, unreliable data sources, and entity resolution at scale.
