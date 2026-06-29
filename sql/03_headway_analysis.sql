-- 03_headway_analysis.sql
-- Purpose: Build scheduled headway analytics for MBTA Green Line branches.
-- Metric: Time gap between consecutive scheduled departures at the same stop,
-- route, direction, and service pattern.

DROP VIEW IF EXISTS v_green_line_departures;
DROP VIEW IF EXISTS v_green_line_headways;
DROP VIEW IF EXISTS v_green_line_headway_summary;


-- 1. Convert GTFS departure_time into seconds after midnight.
-- GTFS times can exceed 24:00:00, so we avoid SQLite's built-in time functions.
CREATE VIEW v_green_line_departures AS
SELECT
    route_id,
    route_short_name,
    route_long_name,
    service_id,
    trip_id,
    trip_headsign,
    direction_id,
    stop_id,
    stop_name,
    stop_sequence,
    departure_time,

    CAST(SUBSTR(departure_time, 1, 2) AS INTEGER) AS departure_hour,
    CAST(SUBSTR(departure_time, 4, 2) AS INTEGER) AS departure_minute,
    CAST(SUBSTR(departure_time, 7, 2) AS INTEGER) AS departure_second,

    (
        CAST(SUBSTR(departure_time, 1, 2) AS INTEGER) * 3600
        + CAST(SUBSTR(departure_time, 4, 2) AS INTEGER) * 60
        + CAST(SUBSTR(departure_time, 7, 2) AS INTEGER)
    ) AS departure_seconds,

    CASE
        WHEN CAST(SUBSTR(departure_time, 1, 2) AS INTEGER) BETWEEN 6 AND 8
            THEN 'AM Peak'
        WHEN CAST(SUBSTR(departure_time, 1, 2) AS INTEGER) BETWEEN 9 AND 15
            THEN 'Midday'
        WHEN CAST(SUBSTR(departure_time, 1, 2) AS INTEGER) BETWEEN 16 AND 18
            THEN 'PM Peak'
        WHEN CAST(SUBSTR(departure_time, 1, 2) AS INTEGER) BETWEEN 19 AND 23
            THEN 'Evening'
        ELSE 'Late Night'
    END AS time_period

FROM v_green_line_trip_stop_sequence
WHERE departure_time IS NOT NULL
  AND departure_time != '';


-- 2. Calculate scheduled headway in minutes.
-- Headway = current departure - previous departure.
CREATE VIEW v_green_line_headways AS
SELECT
    route_id,
    route_short_name,
    route_long_name,
    service_id,
    direction_id,
    stop_id,
    stop_name,
    time_period,
    trip_id,
    trip_headsign,
    stop_sequence,
    departure_time,
    departure_seconds,

    LAG(departure_seconds) OVER (
        PARTITION BY route_id, service_id, direction_id, stop_id
        ORDER BY departure_seconds
    ) AS previous_departure_seconds,

    ROUND(
        (
            departure_seconds
            - LAG(departure_seconds) OVER (
                PARTITION BY route_id, service_id, direction_id, stop_id
                ORDER BY departure_seconds
            )
        ) / 60.0,
        2
    ) AS scheduled_headway_minutes

FROM v_green_line_departures;


-- 3. Summary by route, direction, stop, and time period.
CREATE VIEW v_green_line_headway_summary AS
SELECT
    route_id,
    route_short_name,
    route_long_name,
    direction_id,
    stop_id,
    stop_name,
    time_period,

    COUNT(*) AS scheduled_departure_count,

    ROUND(AVG(scheduled_headway_minutes), 2) AS avg_headway_minutes,
    ROUND(MIN(scheduled_headway_minutes), 2) AS min_headway_minutes,
    ROUND(MAX(scheduled_headway_minutes), 2) AS max_headway_minutes,

    ROUND(
        AVG(scheduled_headway_minutes * scheduled_headway_minutes)
        - AVG(scheduled_headway_minutes) * AVG(scheduled_headway_minutes),
        2
    ) AS headway_variance,

    ROUND(
        SQRT(
            AVG(scheduled_headway_minutes * scheduled_headway_minutes)
            - AVG(scheduled_headway_minutes) * AVG(scheduled_headway_minutes)
        ),
        2
    ) AS headway_stddev_minutes

FROM v_green_line_headways
WHERE scheduled_headway_minutes IS NOT NULL
  AND scheduled_headway_minutes > 0
  AND scheduled_headway_minutes <= 120
GROUP BY
    route_id,
    route_short_name,
    route_long_name,
    direction_id,
    stop_id,
    stop_name,
    time_period;