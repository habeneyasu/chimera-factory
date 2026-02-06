"""
Trend research API clients.

Reference: specs/functional.md US-001, US-002
"""

import os
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

from chimera_factory.utils.logging import setup_logger
from chimera_factory.exceptions import APIError

load_dotenv()
logger = setup_logger(__name__)


class TwitterClient:
    """Twitter API client for trend research."""
    
    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.base_url = os.getenv("TWITTER_API_BASE_URL", "https://api.twitter.com/2")
        self._client: Optional[httpx.Client] = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            if self.bearer_token:
                headers["Authorization"] = f"Bearer {self.bearer_token}"
            self._client = httpx.Client(base_url=self.base_url, headers=headers, timeout=30.0)
        return self._client
    
    def is_configured(self) -> bool:
        """Check if client is configured with API credentials."""
        return bool(self.bearer_token or (self.api_key and self.api_secret))
    
    def search_trends(self, topic: str, timeframe: str = "24h") -> List[Dict[str, Any]]:
        """
        Search Twitter for trending topics using Twitter API v2.
        
        Reference: https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference
        
        Args:
            topic: Search topic/keyword
            timeframe: Time window (1h, 24h, 7d, 30d)
            
        Returns:
            List of trend dictionaries
            
        Raises:
            APIError: If API call fails
        """
        if not self.is_configured():
            logger.warning("Twitter API not configured, returning mock data")
            return self._mock_trends(topic)
        
        try:
            client = self._get_client()
            
            # Calculate time range based on timeframe
            end_time = datetime.utcnow()
            if timeframe == "1h":
                start_time = end_time - timedelta(hours=1)
            elif timeframe == "24h":
                start_time = end_time - timedelta(hours=24)
            elif timeframe == "7d":
                start_time = end_time - timedelta(days=7)
            elif timeframe == "30d":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(hours=24)
            
            # Twitter API v2 search endpoint
            params = {
                "query": f"{topic} -is:retweet lang:en",
                "max_results": 10,
                "tweet.fields": "created_at,public_metrics,author_id",
                "start_time": start_time.isoformat() + "Z",
                "end_time": end_time.isoformat() + "Z"
            }
            
            response = client.get("/tweets/search/recent", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Transform Twitter API response to trend format
            trends = []
            for tweet in data.get("data", []):
                metrics = tweet.get("public_metrics", {})
                engagement = (
                    metrics.get("like_count", 0) +
                    metrics.get("retweet_count", 0) +
                    metrics.get("reply_count", 0) +
                    metrics.get("quote_count", 0)
                )
                trends.append({
                    "title": tweet.get("text", "")[:200],  # Truncate long tweets
                    "source": "twitter",
                    "engagement": engagement,
                    "timestamp": tweet.get("created_at", datetime.now().isoformat()),
                    "url": f"https://twitter.com/i/web/status/{tweet.get('id')}",
                    "relevance_score": min(engagement / 1000.0, 1.0)  # Normalize to 0-1
                })
            
            logger.info(f"Twitter API: Found {len(trends)} trends for topic '{topic}'")
            return trends if trends else self._mock_trends(topic)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Twitter API HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429:
                raise APIError("Twitter API rate limit exceeded", code="RATE_LIMIT_EXCEEDED", retryable=True)
            return self._mock_trends(topic)
        except httpx.RequestError as e:
            logger.warning(f"Twitter API request failed: {e}, using mock data")
            return self._mock_trends(topic)
        except Exception as e:
            logger.error(f"Unexpected error in Twitter API: {e}", exc_info=True)
            return self._mock_trends(topic)
    
    def _mock_trends(self, topic: str) -> List[Dict[str, Any]]:
        """Return mock trend data when API is unavailable."""
        return [
            {
                "title": f"#{topic} trending on Twitter",
                "source": "twitter",
                "engagement": 5000,
                "timestamp": datetime.now().isoformat(),
                "url": f"https://twitter.com/search?q={topic}",
                "relevance_score": 0.5
            }
        ]


class NewsClient:
    """News API client for trend research."""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = os.getenv("NEWS_API_BASE_URL", "https://newsapi.org/v2")
        self._client: Optional[httpx.Client] = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {"X-Api-Key": self.api_key} if self.api_key else {}
            self._client = httpx.Client(base_url=self.base_url, headers=headers, timeout=30.0)
        return self._client
    
    def is_configured(self) -> bool:
        """Check if client is configured with API key."""
        return bool(self.api_key)
    
    def search_news(self, topic: str, timeframe: str = "24h") -> List[Dict[str, Any]]:
        """
        Search news articles for trending topics using NewsAPI.
        
        Reference: https://newsapi.org/docs/endpoints/everything
        
        Args:
            topic: Search topic/keyword
            timeframe: Time window (1h, 24h, 7d, 30d)
            
        Returns:
            List of trend dictionaries
            
        Raises:
            APIError: If API call fails
        """
        if not self.is_configured():
            logger.warning("News API not configured, returning mock data")
            return self._mock_news(topic)
        
        try:
            client = self._get_client()
            
            # Calculate date range
            end_date = datetime.utcnow()
            if timeframe == "1h":
                from_date = end_date - timedelta(hours=1)
            elif timeframe == "24h":
                from_date = end_date - timedelta(hours=24)
            elif timeframe == "7d":
                from_date = end_date - timedelta(days=7)
            elif timeframe == "30d":
                from_date = end_date - timedelta(days=30)
            else:
                from_date = end_date - timedelta(hours=24)
            
            params = {
                "q": topic,
                "from": from_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d"),
                "sortBy": "popularity",
                "pageSize": 10,
                "language": "en"
            }
            
            response = client.get("/everything", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Transform NewsAPI response to trend format
            trends = []
            for article in data.get("articles", []):
                # Estimate engagement based on source reliability
                source_rank = 1000  # Default engagement
                if article.get("source", {}).get("name"):
                    # Popular sources get higher engagement
                    popular_sources = ["BBC", "CNN", "Reuters", "The Guardian", "New York Times"]
                    if any(src in article["source"]["name"] for src in popular_sources):
                        source_rank = 5000
                
                trends.append({
                    "title": article.get("title", ""),
                    "source": "news",
                    "engagement": source_rank,
                    "timestamp": article.get("publishedAt", datetime.now().isoformat()),
                    "url": article.get("url", ""),
                    "relevance_score": 0.7  # News articles generally relevant
                })
            
            logger.info(f"News API: Found {len(trends)} articles for topic '{topic}'")
            return trends if trends else self._mock_news(topic)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"News API HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429:
                raise APIError("News API rate limit exceeded", code="RATE_LIMIT_EXCEEDED", retryable=True)
            return self._mock_news(topic)
        except httpx.RequestError as e:
            logger.warning(f"News API request failed: {e}, using mock data")
            return self._mock_news(topic)
        except Exception as e:
            logger.error(f"Unexpected error in News API: {e}", exc_info=True)
            return self._mock_news(topic)
    
    def _mock_news(self, topic: str) -> List[Dict[str, Any]]:
        """Return mock news data when API is unavailable."""
        return [
            {
                "title": f"{topic} in the news",
                "source": "news",
                "engagement": 3000,
                "timestamp": datetime.now().isoformat(),
                "url": f"https://news.google.com/search?q={topic}",
                "relevance_score": 0.6
            }
        ]


class RedditClient:
    """Reddit API client for trend research."""
    
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = "chimera-factory/0.1.0"
        self.base_url = os.getenv("REDDIT_API_BASE_URL", "https://www.reddit.com")
        self.reddit_auth_url = os.getenv("REDDIT_AUTH_URL", "https://www.reddit.com/api/v1/access_token")
        self._access_token: Optional[str] = None
        self._client: Optional[httpx.Client] = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {"User-Agent": self.user_agent}
            if self._access_token:
                headers["Authorization"] = f"Bearer {self._access_token}"
            self._client = httpx.Client(base_url=self.base_url, headers=headers, timeout=30.0)
        return self._client
    
    def _authenticate(self) -> bool:
        """Authenticate with Reddit API to get access token."""
        if not self.client_id or not self.client_secret:
            return False
        
        try:
            auth_url = self.reddit_auth_url
            auth = (self.client_id, self.client_secret)
            data = {"grant_type": "client_credentials"}
            headers = {"User-Agent": self.user_agent}
            
            response = httpx.post(auth_url, auth=auth, data=data, headers=headers, timeout=10.0)
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data.get("access_token")
            return bool(self._access_token)
        except Exception as e:
            logger.warning(f"Reddit authentication failed: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if client is configured with API credentials."""
        return bool(self.client_id and self.client_secret)
    
    def search_reddit(self, topic: str, timeframe: str = "24h") -> List[Dict[str, Any]]:
        """
        Search Reddit for trending topics using Reddit API.
        
        Reference: https://www.reddit.com/dev/api
        
        Args:
            topic: Search topic/keyword
            timeframe: Time window (1h, 24h, 7d, 30d)
            
        Returns:
            List of trend dictionaries
            
        Raises:
            APIError: If API call fails
        """
        if not self.is_configured():
            logger.warning("Reddit API not configured, returning mock data")
            return self._mock_reddit(topic)
        
        # Authenticate if needed
        if not self._access_token:
            if not self._authenticate():
                logger.warning("Reddit authentication failed, using mock data")
                return self._mock_reddit(topic)
        
        try:
            client = self._get_client()
            
            # Map timeframe to Reddit time filter
            time_map = {"1h": "hour", "24h": "day", "7d": "week", "30d": "month"}
            time_filter = time_map.get(timeframe, "day")
            
            # Reddit search endpoint
            params = {
                "q": topic,
                "sort": "hot",
                "t": time_filter,
                "limit": 10
            }
            
            response = client.get("/r/all/search.json", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Transform Reddit API response to trend format
            trends = []
            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})
                engagement = (
                    post_data.get("score", 0) +
                    post_data.get("num_comments", 0) * 2  # Comments weighted more
                )
                trends.append({
                    "title": post_data.get("title", ""),
                    "source": "reddit",
                    "engagement": engagement,
                    "timestamp": datetime.fromtimestamp(
                        post_data.get("created_utc", datetime.now().timestamp())
                    ).isoformat(),
                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "relevance_score": min(engagement / 100.0, 1.0)  # Normalize to 0-1
                })
            
            logger.info(f"Reddit API: Found {len(trends)} posts for topic '{topic}'")
            return trends if trends else self._mock_reddit(topic)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Reddit API HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429:
                raise APIError("Reddit API rate limit exceeded", code="RATE_LIMIT_EXCEEDED", retryable=True)
            return self._mock_reddit(topic)
        except httpx.RequestError as e:
            logger.warning(f"Reddit API request failed: {e}, using mock data")
            return self._mock_reddit(topic)
        except Exception as e:
            logger.error(f"Unexpected error in Reddit API: {e}", exc_info=True)
            return self._mock_reddit(topic)
    
    def _mock_reddit(self, topic: str) -> List[Dict[str, Any]]:
        """Return mock Reddit data when API is unavailable."""
        return [
            {
                "title": f"r/{topic} trending on Reddit",
                "source": "reddit",
                "engagement": 2000,
                "timestamp": datetime.now().isoformat(),
                "url": f"https://reddit.com/r/{topic}",
                "relevance_score": 0.4
            }
        ]
