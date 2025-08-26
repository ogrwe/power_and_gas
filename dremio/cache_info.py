#!/usr/bin/env python
"""
Utility script to inspect Dremio query cache files in the current directory.

Usage:
    python -m dremio.cache_info [OPTIONS]
    
Options:
    --list               List all cache files (default mode)
    --inspect HASH       Inspect a specific cache file by its hash ID with full details
    --sample N           Show first N files when using --schema or --full (default: all files)
    --schema             Show column names and data types for each file
    --full               Show column names, data types, and basic stats (no sample data)
    
Examples:
    # List all cache files in the current directory
    python -m dremio.cache_info
    
    # Inspect a specific cache file with full details
    python -m dremio.cache_info --inspect 65d52f39dbee3f1b91786676445ff6d8
    
    # Show schema for all cache files
    python -m dremio.cache_info --schema
    
    # Show detailed information for first 5 files (no sample data)
    python -m dremio.cache_info --full --sample 5
"""

import os
import sys
import glob
import argparse
import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime

def list_cache_files(cache_dir="dremio_cache"):
    """List all cache files with their modification times and sizes"""
    cache_path = Path(cache_dir)
    
    if not cache_path.exists():
        print(f"Cache directory not found: {cache_dir}")
        return []
    
    files = glob.glob(os.path.join(cache_path, "*.parquet"))
    
    if not files:
        print(f"No parquet files found in {cache_path}")
        return []
    
    print(f"Found {len(files)} parquet files in {cache_path}:")
    
    file_info = []
    for file in files:
        basename = os.path.basename(file)
        hash_id = os.path.splitext(basename)[0]
        size_mb = os.path.getsize(file) / (1024*1024)
        mod_time = os.path.getmtime(file)
        file_info.append((hash_id, size_mb, mod_time, file))
    
    # Sort by modification time (newest first)
    file_info.sort(key=lambda x: x[2], reverse=True)
    
    print(f"{'Hash ID':<40} {'Size (MB)':<10} {'Last Modified':<20}")
    print("-" * 70)
    
    for hash_id, size_mb, mod_time, _ in file_info:
        mod_time_str = pd.to_datetime(mod_time, unit='s').strftime('%Y-%m-%d %H:%M:%S')
        print(f"{hash_id:<40} {size_mb:<10.2f} {mod_time_str:<20}")
    
    return file_info

def show_schema(df, name="DataFrame"):
    """Display only the schema information for a DataFrame"""
    print(f"\n{'='*40} {name} {'='*40}")
    print(f"Shape: {df.shape} (rows, columns)")
    
    # List of columns with data types
    print("\nColumns and Data Types:")
    for i, (col, dtype) in enumerate(df.dtypes.items(), 1):
        print(f"  {i}. {col}: {dtype}")
    
    print(f"{'='*90}\n")

def inspect_dataframe(df, name="DataFrame", max_rows=5, schema_only=False, full=False, show_samples=False):
    """Display information about a DataFrame"""
    if schema_only:
        show_schema(df, name)
        return
        
    print(f"\n{'='*40} {name} {'='*40}")
    print(f"Shape: {df.shape} (rows, columns)")
    
    # List of columns
    print("\nColumns:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    # Data types
    print("\nData Types:")
    for col, dtype in df.dtypes.items():
        print(f"  {col}: {dtype}")
    
    # Only show sample data when explicitly requested
    if show_samples:
        # Sample data
        print(f"\nSample Data (first {min(max_rows, len(df))} rows):")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(df.head(max_rows))
        
        # Value counts for categorical columns (limited)
        categorical_cols = [col for col in df.columns if df[col].nunique() < 10 and df[col].nunique() > 0]
        if categorical_cols:
            print("\nTop values for selected columns:")
            for col in categorical_cols[:3]:  # Limit to first 3 categorical columns
                print(f"\n{col}:")
                print(df[col].value_counts().head(3))
                if df[col].nunique() > 3:
                    print(f"  ... and {df[col].nunique() - 3} more values")
    
    print(f"{'='*90}\n")

def inspect_parquet_file(file_path, schema_only=False, full=False, show_samples=False):
    """Load and inspect a parquet file"""
    try:
        df = pd.read_parquet(file_path)
        name = os.path.basename(file_path)
        inspect_dataframe(df, name=f"Parquet: {name}", max_rows=5, 
                         schema_only=schema_only, full=full, show_samples=show_samples)
        return df
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Inspect Dremio query cache files")
    parser.add_argument("--list", action="store_true", help="List all cache files (default)")
    parser.add_argument("--inspect", type=str, help="Inspect a specific cache file by its hash ID with full details")
    parser.add_argument("--sample", type=int, default=0, 
                      help="Show first N files when using --schema or --full (default: all files)")
    parser.add_argument("--schema", action="store_true", help="Show column names and data types for each file")
    parser.add_argument("--full", action="store_true", 
                      help="Show column names, data types, and basic stats (no sample data)")
    args = parser.parse_args()
    
    cache_dir = "dremio_cache"
    
    # If no arguments provided, default to list
    if len(sys.argv) == 1:
        args.list = True
    
    if args.inspect:
        # Inspect a specific file with full details
        file_path = os.path.join(cache_dir, f"{args.inspect}.parquet")
        if os.path.exists(file_path):
            # Only show samples for inspect mode
            inspect_parquet_file(file_path, schema_only=args.schema, full=args.full, show_samples=True)
        else:
            print(f"Cache file not found: {args.inspect}")
    else:
        # Default to list mode
        file_info = list_cache_files(cache_dir)
        
        # If schema or full flag is set, inspect files
        if file_info and len(file_info) > 0:
            # Determine how many files to process
            if args.sample > 0:
                sample_count = min(args.sample, len(file_info))
                file_subset = file_info[:sample_count]
            else:
                # Process all files if no sample count specified
                file_subset = file_info
            
            if args.schema:
                print(f"\nShowing schema for {len(file_subset)} files:")
                for hash_id, _, _, file_path in file_subset:
                    inspect_parquet_file(file_path, schema_only=True, full=False)
            
            elif args.full:
                print(f"\nShowing detailed information for {len(file_subset)} files (no sample data):")
                for hash_id, _, _, file_path in file_subset:
                    inspect_parquet_file(file_path, schema_only=False, full=True, show_samples=False)

if __name__ == "__main__":
    main()
