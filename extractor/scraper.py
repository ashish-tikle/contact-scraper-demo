import time
import logging
from pathlib import Path
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from typing import Optional, Tuple
import requests

"""
Fetcher class for retrieving HTML from HTTP(S) URLs or local file paths.
"""



class Fetcher:
    """
    Fetches HTML content from HTTP(S) URLs or local file paths.
    
    Features:
    - Respects robots.txt for HTTP(S) requests
    - Rate limiting per host
    - User-Agent headers
    - Local file support
    """
    
    def __init__(
        self,
        user_agent: str,
        delay: float = 0.5,
        respect_robots: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Fetcher.
        
        Args:
            user_agent: User-Agent string for HTTP requests
            delay: Delay in seconds between requests to the same host
            respect_robots: Whether to respect robots.txt rules
            logger: Optional logger instance
        """
        self.user_agent = user_agent
        self.delay = delay
        self.respect_robots = respect_robots
        self.logger = logger or logging.getLogger(__name__)
        
        # Per-host rate limiting
        self._last_request_time: dict[str, float] = {}
        
        # Robots.txt cache
        self._robots_cache: dict[str, RobotFileParser] = {}
    
    def get(self, url: str) -> Tuple[str, str]:
        """
        Fetch HTML content from a URL or local file path.
        
        Args:
            url: HTTP(S) URL or local file path
            
        Returns:
            Tuple of (html_text, final_url)
            
        Raises:
            requests.exceptions.RequestException: For HTTP errors
            FileNotFoundError: If local file doesn't exist
            PermissionError: If blocked by robots.txt
        """
        parsed = urlparse(url)
        
        # Handle local files
        if parsed.scheme in ('', 'file') or Path(url).exists():
            return self._fetch_local(url)
        
        # Handle HTTP(S)
        if parsed.scheme in ('http', 'https'):
            return self._fetch_http(url)
        
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")
    
    def _fetch_local(self, path: str) -> Tuple[str, str]:
        """Fetch content from a local file."""
        # Remove file:// prefix if present
        if path.startswith('file://'):
            path = path[7:]
        
        file_path = Path(path)
        html_text = file_path.read_text(encoding='utf-8')
        return html_text, f"file://{file_path.absolute()}"
    
    def _fetch_http(self, url: str) -> Tuple[str, str]:
        """Fetch content from an HTTP(S) URL."""
        parsed = urlparse(url)
        host = parsed.netloc
        
        # Check robots.txt
        if self.respect_robots and not self._is_allowed(url):
            self.logger.warning(f"Blocked by robots.txt: {url}")
            raise PermissionError(f"Blocked by robots.txt: {url}")
        
        # Rate limiting per host
        self._apply_rate_limit(host)
        
        # Prepare headers
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        # Make request
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # Set encoding to apparent_encoding for better detection
        if response.encoding != response.apparent_encoding:
            response.encoding = response.apparent_encoding
        
        return response.text, response.url
    
    def _is_allowed(self, url: str) -> bool:
        """Check if fetching the URL is allowed by robots.txt."""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Get or create robots parser for this base URL
        if base_url not in self._robots_cache:
            rp = RobotFileParser()
            robots_url = urljoin(base_url, '/robots.txt')
            try:
                rp.set_url(robots_url)
                rp.read()
                self._robots_cache[base_url] = rp
            except Exception as e:
                self.logger.debug(f"Failed to fetch robots.txt from {robots_url}: {e}")
                # If robots.txt can't be fetched, allow by default
                rp.allow_all = True
                self._robots_cache[base_url] = rp
        
        return self._robots_cache[base_url].can_fetch(self.user_agent, url)
    
    def _apply_rate_limit(self, host: str) -> None:
        """Apply rate limiting for the given host."""
        if host in self._last_request_time:
            elapsed = time.time() - self._last_request_time[host]
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
        
        self._last_request_time[host] = time.time()