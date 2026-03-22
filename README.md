# Parking Location Quote Matching

A Python pipeline that aggregates airport parking data from multiple providers,
normalizes inconsistent schemas, matches equivalent facilities across providers,
and exports structured datasets.

This project demonstrates **entity resolution over messy third-party APIs** —
a core problem in real-world integrations.

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
├── run.py
├── app/
│ ├── db.py
│ ├── models.py
│ ├── providers/
│ ├── normalize/
│ ├── matching/
│ └── export/
└── tests/
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
- Stores raw payloads for traceability/debugging

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

### Why this approach?

- Simple and explainable
- Works well for structured data
- Avoids overengineering (no ML required)
- Easy to tune and debug

---

## ⚙️ Setup

```bash
pip install -r requirements.txt
```

## ▶️ Usage

Run the full pipeline:

```
python run.py pipeline \
  --airports ORD LAX \
  --start "2026-03-28T10:00:00" \
  --end "2026-03-30T18:00:00"
```

Run individual steps:

```
# Fetch + normalize + store
python run.py fetch --airports ORD LAX --start ... --end ...

# Run matching
python run.py match

# Export results
python run.py export
```

## 📦 Outputs

Generated under `data/output/:`

- `parking_lots.csv / .json`
- `parking_quotes.csv / .json`
- `matched_lots.csv / .json`

## 🧪 Testing

```
pytest
```

### ⚠️ Assumptions & Limitations

- Matching is heuristic, not guaranteed perfect
  - Some facilities may:
  - have missing addresses or coordinates
- represent multiple parking products (valet vs self-park)
- Matching prioritizes precision over recall
- Mock data is used instead of real APIs

### 🔮 Future Improvements

- Replace mocked providers with real API integrations
- Add geospatial indexing for faster matching
- Introduce clustering (multi-provider grouping)
- Add confidence calibration or ML-based matching
- Visualize matches on a map

### 🤖 AI Usage

AI tools (ChatGPT / Copilot) were used to:

- scaffold project structure
- suggest normalization and matching strategies
- review and refine code

All final implementation decisions, schema design, and matching logic were
validated and adjusted manually.

### 📌 Summary

This project demonstrates:

- API integration design
- data normalization
- entity matching across messy sources
- pragmatic engineering tradeoffs

The focus is on clarity, explainability, and real-world applicability rather than overengineering.
