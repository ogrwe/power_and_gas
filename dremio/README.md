# Dremio Client for Python

A simple Python toolkit for working with Dremio data sources, SPECIFIC to RWE. This library handles connections to Dremio, caching query results, and managing metadata.

## Features

- 🔌 **Easy connection** to Dremio data sources
- 📊 **Fast queries** with results returned as pandas DataFrames
- 💾 **Automatic caching** to reduce load on Dremio and speed up repeated queries
- 🔄 **Environment detection** to work seamlessly in both local and Databricks environments

## How to Use

This repository is designed to be used as a "drag and drop" module in your projects. Simply copy the `dremio` folder into your project directory.

### Environment Variables

To run the Dremio client locally, you must create a `.env` file in your project's root directory with the following content:

```
DREMIO_USER=your_username
DREMIO_TOKEN=your_token
```

These environment variables are **not** required when running in a Databricks environment, as the client will automatically use the appropriate Databricks authentication methods.

### Running Queries

The `query_dremio` function is the recommended way to query Dremio. It automatically handles caching and environment detection.

```python
from dremio.dremio_client import query_dremio

df = query_dremio("SELECT * FROM Core.MyTable LIMIT 100")
```

## Caching

This library provides a caching mechanism to speed up repeated queries and reduce the load on Dremio, especially in a local development environment.

### Fine-tuning the Cache (Local Environment)

When running locally, `query_dremio` uses the cache automatically. For more granular control over caching behavior, you can use the `default_cache_manager`:

```python
from dremio.dremio_client import default_cache_manager

# Use cached results if they are less than 24 hours old
df = default_cache_manager.get_data(
    "SELECT * FROM Core.MyTable LIMIT 100",
    max_age_hours=24
)

# Force a refresh to ignore the cache and get fresh data
df = default_cache_manager.get_data(
    "SELECT * FROM my_table",
    force_refresh=True
)
```

### Managing the Cache via Command Line

You can manage the cache directly from your command line using the provided utilities.

#### Inspecting the Cache

To inspect the contents of the cache, use the `cache_info` utility:

```bash
# List all cache files in the current directory
python -m dremio.cache_info --list

# Show schema (columns and data types) for all cache files
python -m dremio.cache_info --schema

# Inspect a specific cache file by its hash ID
python -m dremio.cache_info --inspect 65d52f39dbee3f1b91786676445ff6d8
```

#### Clearing the Cache

To clear the cache, use the `clear_dremio_cache` utility:

```bash
# Clear only files older than 48 hours
python -m dremio.clear_dremio_cache --older-than 48

# Clear all cache files (will ask for confirmation)
python -m dremio.clear_dremio_cache
```

You can also clear the cache from within a Python script:
```python
from dremio.dremio_client import default_cache_manager

# Clear all cache files
default_cache_manager.clear_cache()

# Clear only files older than 3 days
default_cache_manager.clear_cache(older_than_hours=72)
```

## Troubleshooting

### Connection Issues

- Verify your Dremio credentials in the `.env` file (for local execution).
- Ensure your network can reach the Dremio server.
- Check if your Dremio token is still valid.
- If running in Databricks, ensure the `lidservices` package is available.
