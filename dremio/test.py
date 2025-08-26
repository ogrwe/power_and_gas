import pandas as pd
from dremio_client import default_cache_manager, query_dremio

test_query = """
    SELECT *
    FROM "Core"."Preparation"."S3"."Team_CAO_US"."LT"."Environmental_Products"."processed_environmental_products"
    LIMIT 15
    """

print("--- Testing query_dremio() ---")
try:
    # Note: query_dremio() has environment detection.
    # This will test the local execution path.
    df_query = query_dremio(test_query)
    if isinstance(df_query, pd.DataFrame) and not df_query.empty:
        print("Successfully retrieved data using query_dremio.")
        print("DataFrame head:")
        print(df_query.head())
    else:
        print("Failed to retrieve data or received an empty DataFrame using query_dremio.")
except Exception as e:
    print(f"An error occurred while testing query_dremio: {e}")
