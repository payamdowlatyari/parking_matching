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

### 🔮 Future Improvements

- Replace mocked providers with real API integrations
- Add geospatial indexing for faster matching
- Introduce clustering (multi-provider grouping)
- Add confidence calibration or ML-based matching
- Visualize matches on a map

---

### 🤖 AI Usage

AI tools (ChatGPT / Copilot) were used to:

- scaffold project structure
- suggest normalization and matching strategies
- review and refine code

All final implementation decisions, schema design, and matching logic were
validated and adjusted manually.

---

### 📌 Summary

This project demonstrates:

- API integration design
- data normalization
- entity matching across messy sources
- pragmatic engineering tradeoffs

The focus is on clarity, explainability, and real-world applicability rather than overengineering.
