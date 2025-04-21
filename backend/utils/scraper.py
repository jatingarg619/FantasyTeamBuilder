"""
Scraper utility functions for getting match data
"""

import os
import sys
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.config.firecrawl_config import FIRECRAWL_CONFIG, FANTASY_CONFIG
import requests

# Configure logging
logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        logger.info("Initializing CacheManager")
        self.config = FIRECRAWL_CONFIG['cache']
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.config['directory'])
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.debug(f"Cache directory: {self.cache_dir}")

    def _get_cache_path(self, key: str) -> str:
        """Get the file path for a cache key"""
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed_key}.json")

    def get(self, key: str) -> Dict[str, Any]:
        """Get data from cache"""
        if not self.config['enabled']:
            logger.debug("Cache is disabled")
            return None

        cache_path = self._get_cache_path(key)
        logger.debug(f"Looking for cache at: {cache_path}")

        if not os.path.exists(cache_path):
            logger.debug("Cache miss: file not found")
            return None

        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                
            # Check if cache has expired
            cached_time = datetime.fromisoformat(data['timestamp'])
            if (datetime.now() - cached_time).total_seconds() > self.config['expiry']:
                logger.debug("Cache miss: data expired")
                os.remove(cache_path)
                return None
                
            logger.info(f"Cache hit for key: {key}")
            return data['content']
            
        except Exception as e:
            logger.error(f"Error reading cache: {str(e)}", exc_info=True)
            return None

    def set(self, key: str, data: Dict[str, Any]):
        """Save data to cache"""
        if not self.config['enabled']:
            logger.debug("Cache is disabled")
            return

        cache_path = self._get_cache_path(key)
        logger.debug(f"Saving cache to: {cache_path}")

        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'content': data
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
                
            logger.info(f"Cached data for key: {key}")
            
        except Exception as e:
            logger.error(f"Error writing cache: {str(e)}", exc_info=True)

class FirecrawlScraper:
    def __init__(self):
        logger.info("Initializing FirecrawlScraper")
        self.config = FIRECRAWL_CONFIG
        self.api_key = self.config['api_key']
        self.cache = CacheManager()
        logger.debug(f"Firecrawl API Key Loaded")

    def scrape_url(self, url: str, options: dict = None) -> dict:
        """Scrape any URL using the official Firecrawl API, with caching."""
        logger.info(f"Scraping URL via Firecrawl: {url}")
        options = options or {}
        cache_key = f"scrape_{url}_{json.dumps(options, sort_keys=True)}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.info(f"Returning cached scrape for {url}")
            return cached_data

        api_endpoint = "https://api.firecrawl.dev/v1/scrape"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {"url": url}
        payload.update(options)

        logger.debug(f"Calling Firecrawl API: {api_endpoint} with payload: {payload}")
        resp = requests.post(api_endpoint, headers=headers, json=payload)
        if resp.status_code != 200:
            logger.error(f"Firecrawl API error: {resp.status_code} - {resp.text}")
            raise Exception(f"Firecrawl API error: {resp.text}")
        data = resp.json()
        self.cache.set(cache_key, data)
        logger.info(f"Scrape successful, data cached for {url}")
        return data

def get_match_data(query: str) -> Dict[str, Any]:
    """
    Get match data for a specific query
    """
    logger.info(f"Getting match data for query: {query}")
    scraper = FirecrawlScraper()
    return scraper.scrape_url(query)
