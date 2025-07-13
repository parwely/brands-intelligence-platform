# backend/app/core/cache.py
import redis.asyncio as redis
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import timedelta
import hashlib
from ..core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service for ML inference results and API responses"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._default_ttl = 3600  # 1 hour default TTL
        self._connect()
    
    def _connect(self):
        """Connect to Redis server"""
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            logger.info(f"Redis cache service initialized: {redis_url}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
    
    def _generate_cache_key(self, prefix: str, data: Any) -> str:
        """Generate a consistent cache key"""
        if isinstance(data, str):
            hash_input = data
        else:
            hash_input = json.dumps(data, sort_keys=True)
        
        hash_obj = hashlib.md5(hash_input.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    async def is_available(self) -> bool:
        """Check if Redis is available"""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False
    
    async def get(self, key: str) -> Optional[Dict]:
        """Get cached data"""
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache read error for key {key}: {e}")
        
        return None
    
    async def set(
        self, 
        key: str, 
        data: Dict, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set cache data with TTL"""
        if not self.redis_client:
            return False
        
        try:
            serialized_data = json.dumps(data, default=str)
            ttl = ttl or self._default_ttl
            
            await self.redis_client.setex(key, ttl, serialized_data)
            return True
        except Exception as e:
            logger.warning(f"Cache write error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cached data"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    async def get_sentiment_cache(self, text: str) -> Optional[Dict]:
        """Get cached sentiment analysis result"""
        cache_key = self._generate_cache_key("sentiment", text)
        return await self.get(cache_key)
    
    async def set_sentiment_cache(
        self, 
        text: str, 
        result: Dict, 
        ttl: int = 7200  # 2 hours for sentiment
    ) -> bool:
        """Cache sentiment analysis result"""
        cache_key = self._generate_cache_key("sentiment", text)
        return await self.set(cache_key, result, ttl)
    
    async def get_analytics_cache(self, cache_params: Dict) -> Optional[Dict]:
        """Get cached analytics result"""
        cache_key = self._generate_cache_key("analytics", cache_params)
        return await self.get(cache_key)
    
    async def set_analytics_cache(
        self, 
        cache_params: Dict, 
        result: Dict, 
        ttl: int = 1800  # 30 minutes for analytics
    ) -> bool:
        """Cache analytics result"""
        cache_key = self._generate_cache_key("analytics", cache_params)
        return await self.set(cache_key, result, ttl)
    
    async def get_bert_cache(self, text: str, model_name: str) -> Optional[Dict]:
        """Get cached BERT analysis result"""
        cache_key = self._generate_cache_key(f"bert:{model_name}", text)
        return await self.get(cache_key)
    
    async def set_bert_cache(
        self, 
        text: str, 
        model_name: str, 
        result: Dict, 
        ttl: int = 14400  # 4 hours for BERT (expensive computation)
    ) -> bool:
        """Cache BERT analysis result"""
        cache_key = self._generate_cache_key(f"bert:{model_name}", text)
        return await self.set(cache_key, result, ttl)
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache pattern invalidation error for {pattern}: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.redis_client:
            return {"available": False}
        
        try:
            info = await self.redis_client.info()
            return {
                "available": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
                ) * 100
            }
        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {"available": False, "error": str(e)}
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()

# Global cache instance
cache_service = CacheService()
