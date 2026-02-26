"""
HTTP client.
"""
import requests
from typing import Optional, Dict, Any
from ..utils import get_logger, retry, get_default_headers

logger = get_logger(__name__)


class HttpClientError(Exception):
    pass


class HttpClient:
    """
    HTTP client with retry, timeout, and session management.

    Usage:
        with HttpClient(base_url="https://api.example.com") as client:
            res = client.get("/products")
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: int = 30,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = requests.Session()
        self._session.headers.update(headers or get_default_headers())
        logger.info(f"HttpClient initialized (timeout={timeout}, retries={max_retries})")

    def _build_url(self, url: str) -> str:
        if url.startswith("http"):
            return url
        return f"{self.base_url}/{url.lstrip('/')}"

    @retry(max_attempts=3, delay=1.0, exceptions=(requests.RequestException,))
    def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        full_url = self._build_url(url)
        logger.info(f"GET {full_url}")
        response = self._session.get(full_url, params=params, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response

    @retry(max_attempts=3, delay=1.0, exceptions=(requests.RequestException,))
    def post(self, url: str, data: Optional[Any] = None, json: Optional[Any] = None, **kwargs) -> requests.Response:
        full_url = self._build_url(url)
        logger.info(f"POST {full_url}")
        response = self._session.post(full_url, data=data, json=json, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response

    def set_headers(self, headers: Dict[str, str]) -> None:
        self._session.headers.update(headers)

    def set_auth(self, token: str, scheme: str = "Bearer") -> None:
        self._session.headers["Authorization"] = f"{scheme} {token}"

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"HttpClient(base_url={self.base_url!r}, timeout={self.timeout})"
