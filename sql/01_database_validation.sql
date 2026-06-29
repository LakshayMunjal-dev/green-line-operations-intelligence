-- 01_database_validation.sql
-- Purpose: Validate that GTFS tables loaded correctly into SQLite.

-- 1. List all tables
SELECT
    name AS table_name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;


-- 2. Core GTFS row counts
SELECT 'agency' AS table_name, COUNT(*) AS row_count FROM agency
UNION ALL
SELECT 'routes', COUNT(*) FROM routes
UNION ALL
SELECT 'trips', COUNT(*) FROM trips
UNION ALL
SELECT 'stops', COUNT(*) FROM stops
UNION ALL
SELECT 'stop_times', COUNT(*) FROM stop_times
UNION ALL
SELECT 'calendar', COUNT(*) FROM calendar
UNION ALL
SELECT 'calendar_dates', COUNT(*) FROM calendar_dates
ORDER BY table_name;


-- 3. Check for duplicate route IDs
SELECT
    route_id,
    COUNT(*) AS duplicate_count
FROM routes
GROUP BY route_id
HAVING COUNT(*) > 1;


-- 4. Check for trips without a matching route
SELECT
    COUNT(*) AS trips_without_matching_route
FROM trips AS t
LEFT JOIN routes AS r
    ON t.route_id = r.route_id
WHERE r.route_id IS NULL;


-- 5. Check for stop_times without matching trips
SELECT
    COUNT(*) AS stop_times_without_matching_trip
FROM stop_times AS st
LEFT JOIN trips AS t
    ON st.trip_id = t.trip_id
WHERE t.trip_id IS NULL;


-- 6. Check for stop_times without matching stops
SELECT
    COUNT(*) AS stop_times_without_matching_stop
FROM stop_times AS st
LEFT JOIN stops AS s
    ON st.stop_id = s.stop_id
WHERE s.stop_id IS NULL;


-- 7. Find Green Line routes
SELECT
    route_id,
    route_short_name,
    route_long_name,
    route_type
FROM routes
WHERE LOWER(COALESCE(route_id, '')) LIKE '%green%'
   OR LOWER(COALESCE(route_short_name, '')) LIKE '%green%'
   OR LOWER(COALESCE(route_long_name, '')) LIKE '%green%'
ORDER BY route_id;