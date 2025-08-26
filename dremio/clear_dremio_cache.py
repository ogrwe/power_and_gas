#!/usr/bin/env python
"""
Utility script to clear the Dremio query cache.

Usage:
    python clear_dremio_cache.py [--older-than HOURS]
    
Options:
    --older-than HOURS    Only clear cache files older than HOURS (default: clear all)
    
Examples:
    # Clear all cache files
    python clear_dremio_cache.py
    
    # Clear only files older than 48 hours
    python clear_dremio_cache.py --older-than 48
"""

import argparse
import shutil
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to sys.path if needed when running as script
script_dir = Path(__file__).parent.absolute()
if script_dir not in sys.path:
    sys.path.append(str(script_dir))

# Now import from the local module
from .dremio_client import default_cache_manager

# ----------------------------------------------------------------------
# Helper to recursively clear all Dremio cache directories
# ----------------------------------------------------------------------

def clear_caches_recursively(
    base_dir: Path, cache_dir_name: str, older_than_hours: int | None = None
) -> dict[str, int]:
    """Recursively delete Dremio cache files/directories below ``base_dir``.

    Returns a mapping of *parent-folder-relative-path* → *number-of-removed-parquet-files*.
    This enables callers to print meaningful summaries after execution.
    """
    removal_map: dict[str, int] = {}
    # Find every directory named *cache_dir_name* (depth-first search)
    for cache_dir in base_dir.rglob(cache_dir_name):
        if not cache_dir.is_dir():
            continue

        for cache_file in cache_dir.glob("*.parquet"):
            # Age filter (if requested)
            if older_than_hours is not None:
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                max_age = timedelta(hours=older_than_hours)
                if datetime.now() - file_time < max_age:
                    continue
            try:
                cache_file.unlink()
                # key by parent dir relative to *base_dir*
                relative_parent = str(cache_dir.parent.relative_to(base_dir)) or "."
                removal_map[relative_parent] = removal_map.get(relative_parent, 0) + 1
            except Exception as exc:
                print(f"Error deleting cache file {cache_file}: {exc}")

        # If the directory is now empty, try removing it to keep things tidy
        try:
            next(cache_dir.iterdir())
        except StopIteration:
            # Directory is empty
            try:
                cache_dir.rmdir()
            except Exception:
                pass

    return removal_map

def main():
    parser = argparse.ArgumentParser(description="Clear Dremio query cache")
    parser.add_argument("--older-than", type=int, 
                      help="Only clear cache files older than specified hours")
    args = parser.parse_args()
    
    # Determine the directory name used for caches (typically "dremio_cache")
    cache_dir_name = default_cache_manager.cache_dir.name

    # Base directory to begin search – the directory the command is executed in
    base_dir = Path.cwd()

    if args.older_than is not None:
        print(
            f"Recursively clearing cache files older than {args.older_than} hours under {base_dir.resolve()} …"
        )
        removal_map = clear_caches_recursively(
            base_dir, cache_dir_name, older_than_hours=args.older_than
        )
        folder_list_str = ", ".join(removal_map.keys()) if removal_map else "(none)"
        print(f"Folders cleared: {folder_list_str}")
        for folder, count in removal_map.items():
            print(f"  - {folder}: {count} file(s) removed")
        print(f"Total files deleted: {sum(removal_map.values())}")
    else:
        confirmation = input(
            f"This will recursively delete ALL Dremio cache files under {base_dir.resolve()} (directory name \"{cache_dir_name}\"). Continue? (y/n): "
        )
        if confirmation.lower() in {"y", "yes"}:
            removal_map = clear_caches_recursively(base_dir, cache_dir_name)
            folder_list_str = ", ".join(removal_map.keys()) if removal_map else "(none)"
            print(f"Folders cleared: {folder_list_str}")
            for folder, count in removal_map.items():
                print(f"  - {folder}: {count} file(s) removed")
            print(f"Total files deleted: {sum(removal_map.values())}")
        else:
            print("Operation cancelled.")

if __name__ == "__main__":
    main()