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
│ ├── config.py
│ ├── providers/
│ ├── normalize/
│ ├── matching/
│ └── export/
├── data/
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

---

### 📄 Example Normalized Record

Below is an example of how different provider payloads are converted into a unified schema:

```json
{
  "provider": "parkwhiz",
  "provider_lot_id": "pw_ord_1",
  "airport_code": "ORD",
  "name": "Joe's Airport Parking",
  "address1": "9420 River St",
  "city": "Schiller Park",
  "state": "IL",
  "postal_code": "60176",
  "latitude": 41.9739,
  "longitude": -87.8694
}
```

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

### 🔗 Example Match Output

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

**Configure credentials**

```
cp .env.example .env
# Edit .env and fill in your API keys
```

## ▶️ Usage

**Run the full pipeline:**

```
python run.py pipeline \
  --airports ORD LAX \
  --start "2026-03-28T10:00:00" \
  --end "2026-03-30T18:00:00"
```

**Run individual steps:**

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

- `parking_lots.csv`/`.json`
- `parking_quotes.csv`/`.json`
- `matched_lots.csv`/`.json`

Raw fetch artifacts under `data/raw/`

## 🧪 Testing

```
pytest
```

### ⚠️ Assumptions & Limitations

- Matching is heuristic, not guaranteed perfect
  - Some facilities may:
  - have missing addresses or coordinates
- represent multiple parking products (valet vs self-park)
- Matching is tuned to prioritize **precision over recall**, ensuring high-confidence matches are reliable while ambiguous cases are surfaced as `possible_match`.
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

- debug when upstream schemas change
- inspect mapping assumptions
- enrich the normalized model later without re-fetching data
- explain matching decisions using source-specific context

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

## ⚡ Performance & Scalability Considerations

The current implementation performs pairwise comparisons (O(n²)) within each airport.

For larger datasets, this can be optimized by:

- **Blocking / candidate filtering**
  - Only compare facilities within a geographic radius or same postal code
- **Geospatial indexing**
  - Use PostGIS or Elasticsearch for efficient spatial queries
- **Parallel processing**
  - Run matching jobs per airport or batch in parallel

The architecture isolates matching logic, making these optimizations easy to introduce without changing ingestion or normalization layers.

---

### Future Improvements

- Replace mocked providers with real API integrations
- Add geospatial indexing for faster matching
- Introduce clustering (multi-provider grouping)
- Add confidence calibration or ML-based matching
- Visualize matches on a map

---

### AI Usage

AI tools (ChatGPT / Copilot) were used to:

- scaffold project structure
- suggest normalization and matching strategies
- review and refine code

All final implementation decisions, schema design, and matching logic were
validated and adjusted manually.

---

### Summary

This project demonstrates:

- API integration across heterogeneous providers
- schema normalization and data modeling
- entity resolution using explainable heuristics
- pragmatic tradeoffs between accuracy, complexity, and scalability

The system is designed to be extensible, debuggable, and production-ready with minimal changes.
