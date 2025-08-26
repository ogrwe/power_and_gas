import argparse
import csv
import json
import re
from pathlib import Path


def extract_ice_code(key: str) -> str:
    """Extract the ICE code from the 'Key' field.

    - Take substring before first ';'
    - Uppercase
    - Keep first 3 alphas (or up to 3 if fewer)
    - Strip spaces
    """
    if not isinstance(key, str):
        return ""
    base = key.split(";", 1)[0].strip().upper()
    # Keep only letters, then truncate to first 3
    letters = re.findall(r"[A-Z]+", base)
    if not letters:
        return base[:3]
    return letters[0][:3]

def extract_granularity(key: str) -> str:
    """Return any descriptor after the second semicolon, e.g. 'Seasonal', '2 Months'.

    If there are fewer than two semicolons, return empty string.
    """
    if not isinstance(key, str):
        return ""
    parts = key.split(";", 2)
    if len(parts) >= 3:
        return parts[2].strip()
    return ""


def convert(input_path: Path, output_path: Path) -> None:
    data = json.loads(input_path.read_text(encoding="utf-8"))

    # Expecting a list of {"Key": ..., "Value": ...}
    rows = []
    for item in data:
        key = item.get("Key")
        val = item.get("Value")
        if key is None or val is None:
            continue
        ice_code = extract_ice_code(key)
        gran = extract_granularity(key)
        if not ice_code:
            continue
        rows.append({
            "ice_code": ice_code,
            "dremio_curve_key": str(val),
            "granularity_descriptor": gran,
        })

    # Write CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "ice_code",
                "dremio_curve_key",
                "granularity_descriptor",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Convert ICE futures curves JSON to CSV mapping.")
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path("ice_futures_curves.json"),
        help="Path to input JSON file (default: ice_futures_curves.json)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("ice_futures_curves_clean.csv"),
        help="Path to output CSV file (default: ice_futures_curves_clean.csv)",
    )
    args = parser.parse_args()

    convert(args.input, args.output)
    print(f"Wrote CSV with mapping to: {args.output}")


if __name__ == "__main__":
    main()
