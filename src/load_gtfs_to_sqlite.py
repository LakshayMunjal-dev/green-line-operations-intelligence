"""
load_gtfs_to_sqlite.py

Loads the latest extracted MBTA GTFS text files into a SQLite database.

"""

from pathlib import Path
import sqlite3
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_PATH = PROCESSED_DATA_DIR / "green_line_ops.db"


def find_latest_extracted_gtfs_folder() -> Path:
    """
    Finds the latest extracted GTFS folder created by download_gtfs.py.
    Expected folder pattern:
    data/raw/mbta_gtfs_YYYY_MM_DD_HHMMSS/extracted
    """
    gtfs_folders = sorted(
        RAW_DATA_DIR.glob("mbta_gtfs_*/extracted"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not gtfs_folders:
        raise FileNotFoundError(
            "No extracted GTFS folder found. Run src/download_gtfs.py first."
        )

    latest_folder = gtfs_folders[0]
    print(f"Using latest GTFS folder: {latest_folder}")

    return latest_folder


def load_txt_file_to_sqlite(file_path: Path, connection: sqlite3.Connection) -> None:
    """
    Loads a single GTFS .txt file into SQLite.
    Table name is based on file name.
    Example:
    routes.txt -> routes
    stop_times.txt -> stop_times
    """
    table_name = file_path.stem

    print(f"Loading {file_path.name} into table: {table_name}")

    df = pd.read_csv(file_path, low_memory=False)

    df.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False,
    )

    print(f"Loaded {len(df):,} rows into {table_name}")


def create_indexes(connection: sqlite3.Connection) -> None:
    """
    Creates helpful indexes for common GTFS analytical joins.
    """
    print("\nCreating indexes...")

    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_routes_route_id ON routes(route_id);",
        "CREATE INDEX IF NOT EXISTS idx_trips_trip_id ON trips(trip_id);",
        "CREATE INDEX IF NOT EXISTS idx_trips_route_id ON trips(route_id);",
        "CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id ON stop_times(trip_id);",
        "CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON stop_times(stop_id);",
        "CREATE INDEX IF NOT EXISTS idx_stops_stop_id ON stops(stop_id);",
        "CREATE INDEX IF NOT EXISTS idx_calendar_service_id ON calendar(service_id);",
        "CREATE INDEX IF NOT EXISTS idx_calendar_dates_service_id ON calendar_dates(service_id);",
    ]

    cursor = connection.cursor()

    for statement in index_statements:
        try:
            cursor.execute(statement)
            print(f"✓ {statement}")
        except sqlite3.OperationalError as error:
            print(f"Skipped index due to missing table/column: {error}")

    connection.commit()
    print("Indexes created.")


def show_database_summary(connection: sqlite3.Connection) -> None:
    """
    Prints table names and row counts.
    """
    print("\nDatabase summary:")

    tables_query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
    """

    tables = pd.read_sql_query(tables_query, connection)

    for table_name in tables["name"]:
        count_query = f"SELECT COUNT(*) AS row_count FROM {table_name};"
        row_count = pd.read_sql_query(count_query, connection)["row_count"].iloc[0]
        print(f"- {table_name}: {row_count:,} rows")


def main() -> None:
    """
    Main script runner.
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    gtfs_folder = find_latest_extracted_gtfs_folder()

    gtfs_files = sorted(gtfs_folder.glob("*.txt"))

    if not gtfs_files:
        raise FileNotFoundError(f"No GTFS .txt files found in {gtfs_folder}")

    print(f"Creating SQLite database at: {DATABASE_PATH}")

    with sqlite3.connect(DATABASE_PATH) as connection:
        for file_path in gtfs_files:
            load_txt_file_to_sqlite(file_path, connection)

        create_indexes(connection)
        show_database_summary(connection)

    print("\nGTFS SQLite loading pipeline finished successfully.")
    print(f"Database created at: {DATABASE_PATH}")


if __name__ == "__main__":
    main()