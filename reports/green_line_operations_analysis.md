# MBTA Green Line Operations Intelligence Analysis

## Project Overview

The Green Line Operations Intelligence project is a transit analytics portfolio project built using MBTA static GTFS schedule data. The goal of the project is to transform raw public transit schedule files into a structured analytics workflow that supports operational insights, dashboard reporting, and portfolio-ready business intelligence outputs.

The project focuses on scheduled Green Line service for the following MBTA branches:

- Green Line B
- Green Line C
- Green Line D
- Green Line E

The analysis excludes temporary shuttle routes, Greenbush commuter rail service, and other non-Green-Line services that may contain the word “Green” in the GTFS route data.

---

## Data Source

The project uses the official MBTA static GTFS feed.

Core GTFS files used in the analysis include:

- `routes.txt`
- `trips.txt`
- `stops.txt`
- `stop_times.txt`
- `calendar.txt`
- `calendar_dates.txt`
- `agency.txt`

The raw GTFS files are downloaded programmatically, extracted into a timestamped folder, and loaded into a SQLite database for analysis.

---

## Methodology

The project follows a repeatable ETL and analytics workflow:

```text
MBTA GTFS ZIP
→ Extracted GTFS text files
→ SQLite database
→ SQL validation queries
→ Green Line analytical views
→ Scheduled headway calculations
→ Tableau-ready CSV exports
→ Tableau dashboard
```

### 1. Data Ingestion

A Python script downloads the MBTA GTFS ZIP file and extracts the raw GTFS text files into the `data/raw/` directory.

### 2. Database Loading

A second Python script loads the GTFS text files into a SQLite database stored locally under:

```text
data/processed/green_line_ops.db
```

### 3. Data Validation

SQL validation checks confirm that the expected GTFS tables loaded successfully and that key relational joins are valid.

Validation checks include:

- Table existence
- Row counts
- Duplicate route checks
- Trips without matching routes
- Stop times without matching trips
- Stop times without matching stops

### 4. Green Line Scope Filtering

Reusable SQL views isolate the Green Line rail branches:

- `Green-B`
- `Green-C`
- `Green-D`
- `Green-E`

This step is important because broader text matching originally captured non-target routes such as Greenbush commuter rail and temporary shuttle routes.

### 5. Headway Analysis

Scheduled headway is calculated as the time gap between consecutive scheduled departures at the same stop, route, direction, and service pattern.

GTFS departure times are converted into seconds after midnight to support accurate time calculations, including cases where GTFS times extend beyond 24:00:00.

### 6. Tableau Export

A Python export script writes clean CSV files for Tableau, including:

- Green Line routes
- Green Line stops
- Green Line trips
- Headway detail
- Headway summary
- Route time-period summary
- Worst scheduled gaps
- Station service frequency

---

## Dashboard Summary

The Tableau dashboard summarizes scheduled Green Line operations using executive KPIs, route-level comparisons, time-period analysis, worst service gaps, and a station service map.

### Dashboard KPIs

| KPI | Value |
|---|---:|
| Average Scheduled Headway | 10.1 min |
| Worst Scheduled Gap | 31.0 min |
| Scheduled Stop Departures | 116,131 |

---

## Key Findings

### 1. Overall Scheduled Frequency

The average scheduled Green Line headway is approximately **10.1 minutes**, indicating relatively frequent scheduled service across the analyzed Green Line branches.

### 2. Worst Scheduled Gap

The largest observed scheduled service gap is approximately **31.0 minutes**. These worst gaps are concentrated in late-night service periods, which is expected because service frequency typically decreases outside peak operating hours.

### 3. Branch-Level Headways

Branch-level average scheduled headways are broadly similar across the B, C, D, and E branches. This suggests that the Green Line branches maintain relatively comparable scheduled service frequency at an aggregate level.

### 4. Time-of-Day Patterns

The time-period matrix shows that:

- AM Peak and PM Peak periods generally have stronger scheduled frequency.
- Midday and evening service remain relatively consistent.
- Late-night service shows longer scheduled headways across branches.

This pattern aligns with typical transit scheduling behavior, where service frequency is higher during commute periods and lower late at night.

### 5. Station Service Frequency

The station map shows the geographic distribution of scheduled service across the Green Line system. The branch colors help distinguish the B, C, D, and E service patterns spatially.

The map also supports station-level review by showing how scheduled frequency and worst gaps vary across the network.

---

## Dashboard Components

The final Tableau dashboard includes:

1. **Executive KPI Cards**
   - Average Scheduled Headway
   - Worst Scheduled Gap
   - Scheduled Stop Departures

2. **Average Scheduled Headway by Branch**
   - Compares average headway across Green Line B, C, D, and E branches.

3. **Scheduled Headway by Branch and Time Period**
   - Shows how scheduled headway changes across AM Peak, Midday, PM Peak, Evening, and Late Night periods.

4. **Worst Scheduled Service Gaps**
   - Identifies stops, branches, and time periods with the largest scheduled gaps.

5. **Green Line Station Service Frequency Map**
   - Visualizes Green Line stops geographically and distinguishes branch-level service patterns.

---

## Technical Skills Demonstrated

This project demonstrates:

- Python ETL scripting
- Public transit GTFS data processing
- SQLite database creation
- SQL validation and analytical views
- SQL window functions for headway calculations
- Tableau-ready data modeling
- Dashboard design
- Transit operations analytics
- Git/GitHub project organization
- Portfolio documentation

---

## Limitations

This analysis uses **static scheduled GTFS data**, not real-time vehicle location or actual arrival/departure data.

Therefore, the dashboard measures scheduled service patterns, not actual operational performance.

The current dashboard does not measure:

- Actual delays
- Real-time reliability
- Canceled trips
- Vehicle bunching
- Passenger load
- On-time performance
- Service disruptions

Future improvements could incorporate MBTA real-time feeds to compare scheduled service against actual service delivery.

---

## Future Improvements

Recommended future enhancements include:

1. Add real-time MBTA data for actual performance analysis.
2. Calculate schedule adherence using actual vs scheduled arrivals.
3. Add reliability scoring by branch and station.
4. Add peak vs off-peak comparison KPIs.
5. Add service coverage metrics by station.
6. Build a published Tableau Public dashboard link.
7. Add dashboard screenshots to the GitHub README.
8. Expand the project to other MBTA rapid transit lines.

---

## Conclusion

The Green Line Operations Intelligence project successfully builds an end-to-end analytics workflow from raw GTFS schedule data to a Tableau operations dashboard.
