-- 02_green_line_views.sql
-- Purpose: Create reusable Green Line analytical views.
-- Scope: Scheduled MBTA Green Line rail branches only.
-- Excludes: Greenbush commuter rail and temporary shuttle routes.

DROP VIEW IF EXISTS v_green_line_routes;
DROP VIEW IF EXISTS v_green_line_trips;
DROP VIEW IF EXISTS v_green_line_stop_times;
DROP VIEW IF EXISTS v_green_line_stops;
DROP VIEW IF EXISTS v_green_line_trip_stop_sequence;


-- 1. Green Line rail branches only
CREATE VIEW v_green_line_routes AS
SELECT
    route_id,
    agency_id,
    route_short_name,
    route_long_name,
    route_desc,
    route_type,
    route_url,
    route_color,
    route_text_color
FROM routes
WHERE route_id IN (
    'Green-B',
    'Green-C',
    'Green-D',
    'Green-E'
);


-- 2. Trips that belong to Green Line rail branches
CREATE VIEW v_green_line_trips AS
SELECT
    t.route_id,
    r.route_short_name,
    r.route_long_name,
    t.service_id,
    t.trip_id,
    t.trip_headsign,
    t.direction_id,
    t.block_id,
    t.shape_id
FROM trips AS t
INNER JOIN v_green_line_routes AS r
    ON t.route_id = r.route_id;


-- 3. Stop times for Green Line rail trips
CREATE VIEW v_green_line_stop_times AS
SELECT
    st.trip_id,
    gt.route_id,
    gt.route_short_name,
    gt.route_long_name,
    gt.service_id,
    gt.trip_headsign,
    gt.direction_id,
    st.arrival_time,
    st.departure_time,
    st.stop_id,
    st.stop_sequence,
    st.pickup_type,
    st.drop_off_type
FROM stop_times AS st
INNER JOIN v_green_line_trips AS gt
    ON st.trip_id = gt.trip_id;


-- 4. Stops used by Green Line rail trips
CREATE VIEW v_green_line_stops AS
SELECT DISTINCT
    s.stop_id,
    s.stop_code,
    s.stop_name,
    s.stop_desc,
    s.stop_lat,
    s.stop_lon,
    s.zone_id,
    s.stop_url,
    s.location_type,
    s.parent_station
FROM stops AS s
INNER JOIN v_green_line_stop_times AS gst
    ON s.stop_id = gst.stop_id;


-- 5. Full trip-stop sequence view for route, stop, direction, and timing analysis
CREATE VIEW v_green_line_trip_stop_sequence AS
SELECT
    gst.route_id,
    gst.route_short_name,
    gst.route_long_name,
    gst.service_id,
    gst.trip_id,
    gst.trip_headsign,
    gst.direction_id,
    gst.arrival_time,
    gst.departure_time,
    gst.stop_sequence,
    gst.stop_id,
    s.stop_name,
    s.stop_lat,
    s.stop_lon
FROM v_green_line_stop_times AS gst
LEFT JOIN stops AS s
    ON gst.stop_id = s.stop_id;