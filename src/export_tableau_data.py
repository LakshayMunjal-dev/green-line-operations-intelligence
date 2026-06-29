"""
export_tableau_data.py

Exports clean analytical tables from SQLite into CSV files for Tableau.

Project: Green Line Operations Intelligence
"""

from pathlib import Path
import sqlite3
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "green_line_ops.db"
EXPORT_DIR = PROJECT_ROOT / "data" / "processed" / "tableau_exports"


EXPORT_QUERIES = {
    "green_line_routes.csv": """
        SELECT
            route_id,
            route_short_name,
            route_long_name,
            route_type,
            route_color,
            route_text_color
        FROM v_green_line_routes
        ORDER BY route_id;
    """,

    "green_line_stops.csv": """
        SELECT
            stop_id,
            stop_code,
            stop_name,
            stop_lat,
            stop_lon,
            location_type,
            parent_station
        FROM v_green_line_stops
        ORDER BY stop_name;
    """,

    "green_line_trips.csv": """
        SELECT
            route_id,
            route_short_name,
            route_long_name,
            service_id,
            trip_id,
            trip_headsign,
            direction_id,
            block_id,
            shape_id
        FROM v_green_line_trips
        ORDER BY route_short_name, direction_id, trip_id;
    """,

    "headway_detail.csv": """
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
            previous_departure_seconds,
            scheduled_headway_minutes
        FROM v_green_line_headways
        WHERE scheduled_headway_minutes IS NOT NULL
          AND scheduled_headway_minutes > 0
          AND scheduled_headway_minutes <= 120
        ORDER BY route_short_name, direction_id, stop_id, departure_seconds;
    """,

    "headway_summary.csv": """
        SELECT
            route_id,
            route_short_name,
            route_long_name,
            direction_id,
            stop_id,
            stop_name,
            time_period,
            scheduled_departure_count,
            avg_headway_minutes,
            min_headway_minutes,
            max_headway_minutes,
            headway_variance,
            headway_stddev_minutes
        FROM v_green_line_headway_summary
        ORDER BY route_short_name, direction_id, stop_name, time_period;
    """,

    "route_time_period_summary.csv": """
        SELECT
            route_short_name,
            route_long_name,
            direction_id,
            time_period,
            COUNT(DISTINCT stop_id) AS stops_analyzed,
            SUM(scheduled_departure_count) AS scheduled_departures,
            ROUND(AVG(avg_headway_minutes), 2) AS avg_headway_minutes,
            ROUND(AVG(min_headway_minutes), 2) AS avg_min_headway_minutes,
            ROUND(AVG(max_headway_minutes), 2) AS avg_max_headway_minutes,
            ROUND(AVG(headway_stddev_minutes), 2) AS avg_headway_stddev_minutes
        FROM v_green_line_headway_summary
        GROUP BY
            route_short_name,
            route_long_name,
            direction_id,
            time_period
        ORDER BY route_short_name, direction_id, time_period;
    """,

    "worst_scheduled_gaps.csv": """
        SELECT
            route_short_name,
            route_long_name,
            direction_id,
            stop_id,
            stop_name,
            time_period,
            avg_headway_minutes,
            max_headway_minutes,
            headway_stddev_minutes,
            scheduled_departure_count
        FROM v_green_line_headway_summary
        WHERE scheduled_departure_count >= 5
        ORDER BY max_headway_minutes DESC
        LIMIT 100;
    """,

    "station_service_frequency.csv": """
        SELECT
            h.stop_id,
            h.stop_name,
            s.stop_lat,
            s.stop_lon,
            h.route_short_name,
            h.direction_id,
            h.time_period,
            SUM(h.scheduled_departure_count) AS scheduled_departures,
            ROUND(AVG(h.avg_headway_minutes), 2) AS avg_headway_minutes,
            ROUND(MAX(h.max_headway_minutes), 2) AS worst_gap_minutes
        FROM v_green_line_headway_summary AS h
        LEFT JOIN v_green_line_stops AS s
            ON h.stop_id = s.stop_id
        GROUP BY
            h.stop_id,
            h.stop_name,
            s.stop_lat,
            s.stop_lon,
            h.route_short_name,
            h.direction_id,
            h.time_period
        ORDER BY h.stop_name, h.route_short_name, h.direction_id, h.time_period;
    """
}


def validate_database_exists() -> None:
    """
    Confirms that the SQLite database exists before exporting.
    """
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DATABASE_PATH}. "
            "Run src/load_gtfs_to_sqlite.py first, then apply the SQL view files."
        )


def export_query_to_csv(
    connection: sqlite3.Connection,
    output_filename: str,
    query: str,
) -> None:
    """
    Runs a SQL query and exports the result to a CSV file.
    """
    output_path = EXPORT_DIR / output_filename

    print(f"Exporting {output_filename}...")

    df = pd.read_sql_query(query, connection)
    df.to_csv(output_path, index=False)

    print(f"✓ {output_filename}: {len(df):,} rows")


def main() -> None:
    """
    Main script runner.
    """
    validate_database_exists()
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Using database: {DATABASE_PATH}")
    print(f"Export folder: {EXPORT_DIR}\n")

    with sqlite3.connect(DATABASE_PATH) as connection:
        for output_filename, query in EXPORT_QUERIES.items():
            export_query_to_csv(connection, output_filename, query)

    print("\nTableau export completed successfully.")
    print("CSV files are ready in:")
    print(EXPORT_DIR)


if __name__ == "__main__":
    main()