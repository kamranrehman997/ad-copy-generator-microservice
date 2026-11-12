import ipaddress
import logging
import socket
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_MAX_BYTES = 500_000
_MAX_CHARS = 4_000
_USER_AGENT = "ad-copy-microservice/1.0"


class PageFetchError(Exception):
    pass


def _host_is_public(hostname: str) -> bool:
    try:
        literal = ipaddress.ip_address(hostname)
    except ValueError:
        literal = None
    if literal is not None:
        return literal.is_global

    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise PageFetchError(f"Could not resolve {hostname}") from exc

    addresses = {ipaddress.ip_address(item[4][0]) for item in infos}
    return bool(addresses) and all(address.is_global for address in addresses)


async def fetch_page_text(url: str) -> str | None:
    """Return visible page text, or None when the page cannot be used."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        logger.info("Skipping product URL with unsupported scheme")
        return None
    if not _host_is_public(parsed.hostname):
        logger.info("Skipping product URL that does not resolve to a public address")
        return None

    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=False) as client:
            response = await client.get(url, headers={"User-Agent": _USER_AGENT})
            response.raise_for_status()
    except (httpx.HTTPError, PageFetchError) as exc:
        logger.info("Product page fetch failed: %s", exc)
        return None

    content_type = response.headers.get("content-type", "")
    if content_type and not content_type.startswith(("text/html", "text/plain", "application/xhtml")):
        logger.info("Skipping product URL with content type %s", content_type)
        return None

    soup = BeautifulSoup(response.content[:_MAX_BYTES], "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ", strip=True).split())
    if not text:
        return None
    return text[:_MAX_CHARS]
