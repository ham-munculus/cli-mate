import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any
import logging

logger: Any = logging.getLogger(__name__)


class WeatherCache:
    """Simple file-based cache for weather data."""

    def __init__(self, cache_dir=None, ttl_minutes: int = 30) -> None:
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "cli-mate"
            self.cache_dir: Path = Path(cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.ttl = timedelta(minutes=ttl_minutes)

    def _get_cache_key(self, city: str, state: str) -> str:
        """Generate cache key from city, state"""
        key: str = f"{city.lower()},{state.lower()}"
        return hashlib.md5(data=key.encode()).hexdigest()

    def _get_cache_path(self, city: str, state: str) -> Path:
        """Get full cache file path"""
        return self.cache_dir / f"{self._get_cache_key(city, state)}.json"

    def get(self, city: str, state: str) -> optional[dict[str, Any]]:
        """Get cached weather data if valid"""
        cache_path: Path = self._get_cache_path(city, state)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                data = json.load(f)

            timestamp = datetime.fromisoformat(data["_timestamp"])
            if datetime.now() - timestamp > self.ttl:
                logger.debug(f"cache expired for {city}, {state}")
                return None

            logger.debug(f"Cache hit for {city}, {state}")
            return data["data"]
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Cache read error: {e}")
            return None

    def set(self, city: str, state: str, data: dict[str, Any]) -> None:
        """Cache weather data"""
        cache_path = self._get_cache_path(city, state)

        try:
            cache_data = {
                "_timestamp": datetime.now().isoformat(),
                "data": data,
            }
            with open(cache_path, "w") as f:
                json.dump(cache_data, f)
                logger.debug(f"Cached wether for {city}, {state}")
        except IOError as e:
            logger.warning(f"Cache write error: {e}")
