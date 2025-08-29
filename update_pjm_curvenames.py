import argparse
from pathlib import Path
from typing import List, Tuple
import re

from dremio.dremio_client import query_dremio

PJM_HEADER = "## PJM"
ERCOT_HEADER = "## ERCOT"
TABLE_HEADER = "| Product Code | CurveKey | CurveName"
SECTION_HEADER_PATTERN = re.compile(r"^## ")


def find_section(lines: List[str], header: str) -> Tuple[int, int]:
    """Return the [start, end) line indices of a section by its H2 header text."""
    start = -1
    for i, line in enumerate(lines):
        if line.strip() == header:
            start = i
            break
    if start == -1:
        raise ValueError(f"Could not find '{header}' section header")

    end = len(lines)
    for j in range(start + 1, len(lines)):
        if SECTION_HEADER_PATTERN.match(lines[j]) and lines[j].strip() != header:
            end = j
            break
    return start, end


def extract_curvekeys_from_section(lines: List[str], start: int, end: int) -> List[str]:
    """Extract CurveKeys from a section table. Does not modify the file."""
    # Find table header inside section
    header = -1
    for i in range(start, end):
        if lines[i].strip().startswith(TABLE_HEADER):
            header = i
            break
    if header == -1:
        return []

    # Alignment row is next; data rows follow until a non-table line
    keys: List[str] = []
    for j in range(header + 2, end):
        line = lines[j].strip()
        if not line.startswith("|"):
            break
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            break
        curvekey = parts[2].strip()
        if curvekey:
            keys.append(curvekey)
    return keys


def fetch_curvenames(curvekeys: List[str]) -> List[Tuple[str, str]]:
    """Return list of (CurveKey, CurveName) using Dremio, without changing files.

    Uses DISTINCT to avoid pulling many duplicate rows.
    """
    if not curvekeys:
        return []
    in_list = ",".join([f"'{ck}'" for ck in sorted(set(curvekeys))])
    sql = f"""
    SELECT DISTINCT CurveKey, CurveName
    FROM Core.Preparation.MIX.RAW.ICEIPE."ICE_FUTURES_SPECIAL"
    WHERE CurveKey IN ({in_list})
    """
    df = query_dremio(sql)
    if df is None or df.empty:
        return []
    # Deduplicate by keeping first non-empty CurveName per CurveKey
    out: dict[str, str] = {}
    for _, row in df.iterrows():
        ck = str(row.get("CurveKey", "")).strip()
        cn = str(row.get("CurveName", "")).strip()
        if ck and cn and ck not in out:
            out[ck] = cn
    # Preserve original key order
    return [(ck, out.get(ck, "")) for ck in curvekeys]


def main():
    parser = argparse.ArgumentParser(description="Get CurveName for PJM and ERCOT CurveKeys (no file edits)")
    parser.add_argument(
        "--path",
        default=str(Path("prompting") / "data_sources.md"),
        help="Path to prompting/data_sources.md",
    )
    args = parser.parse_args()

    md_path = Path(args.path)
    if not md_path.exists():
        raise SystemExit(f"File not found: {md_path}")

    lines = md_path.read_text(encoding="utf-8").splitlines()
    # PJM
    pjm_start, pjm_end = find_section(lines, PJM_HEADER)
    pjm_keys = extract_curvekeys_from_section(lines, pjm_start, pjm_end)
    pjm_pairs = fetch_curvenames(pjm_keys)

    # ERCOT
    ercot_start, ercot_end = find_section(lines, ERCOT_HEADER)
    ercot_keys = extract_curvekeys_from_section(lines, ercot_start, ercot_end)
    ercot_pairs = fetch_curvenames(ercot_keys)

    if not pjm_pairs and not ercot_pairs:
        print("No CurveName values retrieved. Check Dremio credentials or CurveKeys.")
        return

    # Print mappings separately for manual replacement
    if pjm_pairs:
        print("PJM CurveKey -> CurveName")
        for ck, cn in pjm_pairs:
            print(f"{ck}: {cn}")
        print("")

    if ercot_pairs:
        print("ERCOT CurveKey -> CurveName")
        for ck, cn in ercot_pairs:
            print(f"{ck}: {cn}")


if __name__ == "__main__":
    main()
