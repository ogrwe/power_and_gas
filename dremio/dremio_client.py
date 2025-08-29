"""
Dremio Client - Core functionality for connecting to Dremio and managing query caching.

This module provides:
1. DremioConnector - Connect to Dremio and execute queries
2. DremioCacheManager - Cache query results to improve performance
3. Utility functions for working with Dremio data

Required Environment Variables:
    DREMIO_USER: Your Dremio username
    DREMIO_TOKEN: Your Dremio authentication token
"""

# Standard library imports
import ssl
import codecs
from http.cookies import SimpleCookie
import hashlib
from datetime import datetime, timedelta
import os
from pathlib import Path
import time
from typing import Dict, List, Any, Optional, Union
import sys

# Third-party imports
import pandas as pd
from pyarrow import flight
# Conditionally import dotenv: needed for local development (.env files),
# but often unavailable in Databricks. Provide a harmless fallback there.
try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    def load_dotenv(*args, **kwargs):  # type: ignore
        """Fallback no-op when python-dotenv is not installed (e.g., on Databricks)."""
        return None

#=====================================================================
# CONNECTION CLASSES AND UTILITIES
#=====================================================================

def get_rwe_certificate():
    """Get the RWE Server Auth certificate if available in the system store."""
    try:
        ssc = ssl.create_default_context()
        ca_cert_list = ssc.get_ca_certs()
        rwe_server_auth_ca_list = [i for i, cert in enumerate(ca_cert_list) if cert["subject"][-1][0][1] == 'RWE Server Auth Issuing CA']
        if rwe_server_auth_ca_list:
            cert_bin = ssc.get_ca_certs(True)[rwe_server_auth_ca_list[0]]
            return "".join(codecs.encode(cert_bin, "base64").decode("utf-8").split())  # this is the certificate
        else:
            return None
    except ImportError:
        return None

class CookieMiddlewareFactory(flight.ClientMiddlewareFactory):
    """Factory for creating CookieMiddleware instances."""
    
    def __init__(self):
        self.cookies = {}
        super().__init__()

    def start_call(self, info):
        return CookieMiddleware(self)

class CookieMiddleware(flight.ClientMiddleware):
    """Middleware for handling cookies in Flight requests."""
    
    def __init__(self, factory):
        self.factory = factory
        self.cookies = {}
        super().__init__()

    def received_headers(self, headers):
        # Handle headers in the format provided by Arrow Flight
        for key in headers:
            if key.lower() == 'set-cookie':
                cookie = SimpleCookie()
                for item in headers.get(key):
                    cookie.load(item)
                
                # Update cookies dictionary with new values
                self.factory.cookies.update(cookie.items())

    def sending_headers(self):
        if self.factory.cookies:
            cookie_string = '; '.join("{!s}={!s}".format(key, val.value) for (key, val) in self.factory.cookies.items())
            return {b'cookie': cookie_string.encode('utf-8')}
        return {}

class DremioConnector:
    """
    Connect to Dremio and execute queries.
    
    Provides a PyArrow connection to query Dremio and return results as pandas dataframes.
    
    Examples:
        # Initialize connection
        connection = DremioConnector(user_id="UI123456", token="your_token")
        
        # Execute query
        df = connection.query("SELECT * FROM my_dataset LIMIT 10")
        
        # Close connection when done
        connection.close()
    """
    
    def __init__(self, user_id=None, token=None, host="dremio.lid-prod.aws-eu1.energy.local", port=32010, use_ssl=True):
        """
        Initialize a connection to Dremio.
        
        Args:
            user_id (str): Dremio username
            token (str): Dremio authentication token
            host (str): Dremio host
            port (int): Dremio port
            use_ssl (bool): Whether to use SSL for the connection
        """
        # Load environment variables if credentials not provided
        if not any([user_id, token]):
            load_dotenv()
            user_id = os.getenv("DREMIO_USER")
            token = os.getenv("DREMIO_TOKEN")
        
        self.host = host
        self.port = port
        self.user_id = user_id
        self.token = token
        self.use_ssl = use_ssl
        self.client = None
        self.connect()
    
    def connect(self):
        # Establish a connection to Dremio
        try:
            # Set up the Flight client
            cookie_factory = CookieMiddlewareFactory()
            
            if self.use_ssl:
                location = f"grpc+tls://{self.host}:{self.port}"
                cert = get_rwe_certificate()
                connection_args = {}
                if cert:
                    connection_args = {'tls_root_certs': f'-----BEGIN CERTIFICATE-----\n{cert}\n-----END CERTIFICATE-----'}
                else:
                    connection_args = {'disable_server_verification': True}
                
                self.client = flight.FlightClient(
                    location=location,
                    middleware=[cookie_factory],
                    **connection_args
                )
            else:
                location = f"grpc://{self.host}:{self.port}"
                self.client = flight.FlightClient(
                    location=location,
                    middleware=[cookie_factory]
                )
            
            # Use the official authentication method
            flight_call_options = flight.FlightCallOptions(headers=[])
            try:
                bearer_token = self.client.authenticate_basic_token(
                    self.user_id, 
                    self.token, 
                    flight_call_options
                )
                print(f"Connected to Dremio at {self.host}:{self.port}")
                return True
            except Exception as auth_error:
                print(f"Error authenticating with token: {auth_error}")
                return False
        
        except Exception as e:
            print(f"Error connecting to Dremio: {e}")
            return False
    
    def query(self, sql_query, return_pandas_dataframe=True, pandas_options_override=None):
        if pandas_options_override is None:
            pandas_options_override = {}
        # Execute a SQL query and return the results as a pandas DataFrame.

        try:
            if not self.client:
                self.connect()
            
            # Authenticate with token using the official method
            flight_call_options = flight.FlightCallOptions(headers=[])
            bearer_token = self.client.authenticate_basic_token(self.user_id, self.token, flight_call_options)
            
            # Use the token for the query
            authenticated_headers = [bearer_token]
            flight_options = flight.FlightCallOptions(headers=authenticated_headers)
            
            # Execute the query
            flight_info = self.client.get_flight_info(
                flight.FlightDescriptor.for_command(sql_query),
                flight_options
            )
            
            # Get the results
            reader = self.client.do_get(flight_info.endpoints[0].ticket, flight_options)
            
            # Process results and convert to pandas
            if return_pandas_dataframe:
                return reader.read_pandas(**pandas_options_override)
            else:
                return reader.read_all()
        
        except Exception as e:
            print(f"Error executing query: {e}")
            print(f"Query: {sql_query}")
            if return_pandas_dataframe:
                return pd.DataFrame()
            else:
                return None
    
    def close(self):
        """Close the connection to Dremio."""
        if self.client:
            self.client.close()
            self.client = None
            print("Dremio connection closed")

#=====================================================================
# CACHING FUNCTIONALITY
#=====================================================================

class DremioCacheManager:
    """
    Cache manager for Dremio query results.
    
    Stores query results as parquet files for faster access and reduced load on Dremio.
    
    Examples:
        # Initialize cache manager
        cache_manager = DremioCacheManager(cache_dir="my_cache")
        
        # Execute query with caching
        df = cache_manager.get_data(
            "SELECT * FROM my_table LIMIT 100",
            max_age_hours=24,
            force_refresh=False
        )
        
        # Clear old cache files
        cache_manager.clear_cache(older_than_hours=72)
    """
    
    def __init__(self, cache_dir="dremio_cache", user_id=None, token=None):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir (str): Directory to store cache files
            user_id (str): Dremio username
            token (str): Dremio authentication token
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.user_id = user_id
        self.token = token
        self.connector = None
    
    def _get_cache_path(self, query):
        """
        Get the cache file path for a query.
        
        Args:
            query (str): SQL query
            
        Returns:
            Path: Path to the cache file
        """
        # Create a hash of the query to use as the filename
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return self.cache_dir / f"{query_hash}.parquet"
    
    def _is_cache_valid(self, cache_path, max_age_hours):
        """
        Check if a cache file is valid (exists and is not too old).
        
        Args:
            cache_path (Path): Path to the cache file
            max_age_hours (int): Maximum age of the cache in hours
            
        Returns:
            bool: True if the cache is valid, False otherwise
        """
        if not cache_path.exists():
            return False
        
        # Check if the cache is too old
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        max_age = timedelta(hours=max_age_hours)
        return datetime.now() - file_time < max_age
    
    def get_data(self, query, max_age_hours=1, force_refresh=False):
        """
        Get data for a query, using cache if available and not too old.
        
        Args:
            query (str): SQL query
            max_age_hours (int): Maximum age of the cache in hours
            force_refresh (bool): Whether to force a refresh from Dremio
            
        Returns:
            pandas.DataFrame: Query results
        """
        cache_path = self._get_cache_path(query)
        
        # Check if we can use the cache
        if not force_refresh and self._is_cache_valid(cache_path, max_age_hours):
            try:
                print(f"Using cached data from {cache_path}")
                start_time = time.time()  # Start timing
                df = pd.read_parquet(cache_path)
                elapsed_time = time.time() - start_time  # Calculate elapsed time
                print(f"Query completed in {elapsed_time:.1f} seconds (from cache)")
                return df
            except Exception as e:
                print(f"Error reading cache file: {e}")
                # If there's an error reading the cache, continue to fetch from Dremio
    
        # If we get here, we need to fetch from Dremio
        if not self.connector:
            self.connector = DremioConnector(user_id=self.user_id, token=self.token)
        
        # Execute the query
        print("Fetching data from Dremio...")
        start_time = time.time()  # Start timing
        df = self.connector.query(query)
        elapsed_time = time.time() - start_time  # Calculate elapsed time
        print(f"Query completed in {elapsed_time:.1f} seconds (from Dremio)")
        
        # Save to cache if we got results
        if not df.empty:
            try:
                df.to_parquet(cache_path)
                print(f"Saved query results to cache: {cache_path}")
            except Exception as e:
                print(f"Error saving to cache: {e}")
        
        return df
    
    def clear_cache(self, older_than_hours=None):
        """
        Clear the cache, optionally only files older than a certain age.
        
        Args:
            older_than_hours (int, optional): Only clear files older than this many hours
            
        Returns:
            int: Number of files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.parquet"):
            if older_than_hours is not None:
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                max_age = timedelta(hours=older_than_hours)
                if datetime.now() - file_time < max_age:
                    continue
            
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                print(f"Error deleting cache file {cache_file}: {e}")
        
        print(f"Cleared {count} cache files")
        return count

# Check if we're in a local environment or Databricks
def is_running_in_databricks():
    """
    Determine if the code is running in a Databricks environment.
    
    Returns:
        bool: True if running in Databricks, False otherwise
    """
    return os.path.exists("/dbfs")

def is_running_locally():
    """
    Determine if the code is running in a local environment.
    
    Returns:
        bool: True if running locally, False otherwise
    """
    # Check if path starts with C: drive (Windows local environment)
    return sys.path[0].startswith("C:")

def query_dremio(query_str):
    """
    Query Dremio using the appropriate method based on the current environment.
    
    In a local environment, uses the default_cache_manager from dremio_client.
    In Databricks, uses the lidservices.api.dremio_databricks_loader.
    
    Args:
        query_str (str): SQL query to execute
        
    Returns:
        pandas.DataFrame: Query results
    """
    if is_running_in_databricks():
        # Import Databricks-specific libraries
         
        from lidservices.api.dremio_databricks_loader import run_dremio_query, get_databricks_username, get_dremio_token
        
        # Execute query using Databricks method
        df = run_dremio_query(query_str)
        # Convert to pandas DataFrame
        df = df.toPandas()
    else:
        # Execute query using local method
        df = default_cache_manager.get_data(query_str)
    
    return df

#=====================================================================
# DEFAULT INSTANCES & EXPORTS
#=====================================================================

# Create a default cache manager instance for convenience
default_cache_manager = DremioCacheManager()

# Load environment variables for default credentials
load_dotenv()
user_id = os.getenv("DREMIO_USER")
token = os.getenv("DREMIO_TOKEN")

# Update default cache manager with credentials if available
if user_id and token:
    default_cache_manager.user_id = user_id
    default_cache_manager.token = token 

# Export the query_dremio function for easy access
__all__ = ['DremioConnector', 'DremioCacheManager', 'default_cache_manager', 'query_dremio']
