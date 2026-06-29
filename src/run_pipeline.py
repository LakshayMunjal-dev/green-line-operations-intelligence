"""
run_pipeline.py

Runs the full Green Line Operations Intelligence backend pipeline.

Pipeline:
1. Download MBTA GTFS feed
2. Load GTFS files into SQLite
3. Apply Green Line SQL views
4. Apply headway analysis SQL
5. Export Tableau-ready CSV files

Project: Green Line Operations Intelligence
"""

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "green_line_ops.db"

SQL_FILES = [
    PROJECT_ROOT / "sql" / "02_green_line_views.sql",
    PROJECT_ROOT / "sql" / "03_headway_analysis.sql",
]


def run_python_script(script_path: Path) -> None:
    """
    Runs a Python script using the current Python interpreter.
    """
    print(f"\nRunning Python script: {script_path.name}")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Script failed: {script_path}")

    print(f"Finished: {script_path.name}")


def run_sql_file(sql_file_path: Path) -> None:
    """
    Applies a SQL file to the SQLite database.
    """
    print(f"\nApplying SQL file: {sql_file_path.name}")

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DATABASE_PATH}. "
            "Run the GTFS loader before applying SQL files."
        )

    with open(sql_file_path, "r", encoding="utf-8") as sql_file:
        result = subprocess.run(
            ["sqlite3", str(DATABASE_PATH)],
            stdin=sql_file,
            cwd=PROJECT_ROOT,
            check=False,
        )

    if result.returncode != 0:
        raise RuntimeError(f"SQL file failed: {sql_file_path}")

    print(f"Finished: {sql_file_path.name}")


def main() -> None:
    """
    Runs the complete backend pipeline.
    """
    print("=" * 70)
    print("GREEN LINE OPERATIONS INTELLIGENCE PIPELINE")
    print("=" * 70)

    run_python_script(PROJECT_ROOT / "src" / "download_gtfs.py")
    run_python_script(PROJECT_ROOT / "src" / "load_gtfs_to_sqlite.py")

    for sql_file in SQL_FILES:
        run_sql_file(sql_file)

    run_python_script(PROJECT_ROOT / "src" / "export_tableau_data.py")

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"SQLite database: {DATABASE_PATH}")
    print(
        "Tableau exports: "
        f"{PROJECT_ROOT / 'data' / 'processed' / 'tableau_exports'}"
    )


if __name__ == "__main__":
    main()