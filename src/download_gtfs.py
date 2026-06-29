"""
download_gtfs.py

Downloads the official MBTA static GTFS feed, saves the ZIP file,
and extracts the GTFS text files for downstream analytics.

Project: Green Line Operations Intelligence
"""

from pathlib import Path
from datetime import datetime
import zipfile
import requests


GTFS_URL = "https://cdn.mbta.com/MBTA_GTFS.zip"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def create_run_folder() -> Path:
    """
    Creates a timestamped folder for the GTFS download.
    Example: data/raw/mbta_gtfs_2026_06_29_023000
    """
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    run_folder = RAW_DATA_DIR / f"mbta_gtfs_{timestamp}"
    run_folder.mkdir(parents=True, exist_ok=True)
    return run_folder


def download_file(url: str, destination: Path) -> None:
    """
    Downloads a file from a URL and saves it locally.
    """
    print(f"Downloading GTFS feed from: {url}")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    destination.write_bytes(response.content)

    file_size_mb = destination.stat().st_size / (1024 * 1024)
    print(f"Saved ZIP file to: {destination}")
    print(f"File size: {file_size_mb:.2f} MB")


def extract_zip(zip_path: Path, extract_to: Path) -> None:
    """
    Extracts a GTFS ZIP file into a target folder.
    """
    print(f"Extracting ZIP file to: {extract_to}")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    print("Extraction complete.")


def list_extracted_files(folder: Path) -> None:
    """
    Prints extracted GTFS files.
    """
    print("\nExtracted GTFS files:")

    files = sorted(folder.glob("*.txt"))

    if not files:
        print("No .txt files found. Check whether the GTFS ZIP extracted correctly.")
        return

    for file in files:
        size_kb = file.stat().st_size / 1024
        print(f"- {file.name} ({size_kb:.1f} KB)")


def validate_required_files(folder: Path) -> None:
    """
    Checks that core GTFS files exist.
    """
    required_files = [
        "agency.txt",
        "routes.txt",
        "trips.txt",
        "stops.txt",
        "stop_times.txt",
        "calendar.txt",
        "calendar_dates.txt",
    ]

    print("\nValidating required GTFS files:")

    missing_files = []

    for filename in required_files:
        file_path = folder / filename

        if file_path.exists():
            print(f"✓ {filename}")
        else:
            print(f"✗ Missing: {filename}")
            missing_files.append(filename)

    if missing_files:
        raise FileNotFoundError(
            f"Missing required GTFS files: {', '.join(missing_files)}"
        )

    print("All required GTFS files are present.")


def main() -> None:
    """
    Main script runner.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    run_folder = create_run_folder()
    zip_path = run_folder / "MBTA_GTFS.zip"
    extract_folder = run_folder / "extracted"

    extract_folder.mkdir(parents=True, exist_ok=True)

    download_file(GTFS_URL, zip_path)
    extract_zip(zip_path, extract_folder)
    list_extracted_files(extract_folder)
    validate_required_files(extract_folder)

    print("\nGTFS download pipeline finished successfully.")
    print(f"Raw GTFS folder: {extract_folder}")


if __name__ == "__main__":
    main()