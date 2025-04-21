import os
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path
from ..config.firecrawl_config import FIRECRAWL_CONFIG

class CacheManager:
    def __init__(self):
        self.config = FIRECRAWL_CONFIG['cache']
        self.cache_dir = Path(self.config['directory'])
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key"""
        # Create a safe filename from the key
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return self.cache_dir / f"{safe_key}.json"
    
    def get(self, key: str) -> Optional[Dict]:
        """
        Get data from cache if it exists and hasn't expired
        """
        if not self.config['enabled']:
            return None
            
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None
            
        try:
            with cache_path.open('r') as f:
                cached_data = json.load(f)
                
            # Check if cache has expired
            if time.time() - cached_data['timestamp'] > self.config['expiry']:
                return None
                
            return cached_data['data']
        except Exception as e:
            print(f"Cache read error: {e}")
            return None
    
    def set(self, key: str, data: Dict):
        """
        Save data to cache with current timestamp
        """
        if not self.config['enabled']:
            return
            
        cache_path = self._get_cache_path(key)
        try:
            cache_data = {
                'timestamp': time.time(),
                'data': data
            }
            with cache_path.open('w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def clear(self, key: str = None):
        """
        Clear specific cache entry or all cache if no key provided
        """
        if key:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
        else:
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
                
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        """
        stats = {
            'total_entries': 0,
            'total_size': 0,
            'expired_entries': 0
        }
        
        current_time = time.time()
        for cache_file in self.cache_dir.glob('*.json'):
            stats['total_entries'] += 1
            stats['total_size'] += cache_file.stat().st_size
            
            try:
                with cache_file.open('r') as f:
                    cached_data = json.load(f)
                if current_time - cached_data['timestamp'] > self.config['expiry']:
                    stats['expired_entries'] += 1
            except:
                stats['expired_entries'] += 1
                
        return stats
