"""Web-page extraction for URL-based memories."""

from __future__ import annotations

from dataclasses import dataclass

import requests
from html import unescape
from html.parser import HTMLParser
import re


class _PageParser(HTMLParser):
    """Extract page metadata and visible text without third-party parsers."""

    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.description = ""
        self._in_title = False
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag in {"script", "style", "noscript"}:
            self._ignored_depth += 1
        elif tag == "title" and not self._ignored_depth:
            self._in_title = True
        elif tag == "meta" and not self.description:
            name = (attributes.get("name") or "").lower()
            property_name = (attributes.get("property") or "").lower()
            if name == "description" or property_name == "og:description":
                self.description = (attributes.get("content") or "").strip()

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        if self._in_title:
            self.title_parts.append(data)
        else:
            self.text_parts.append(data)


@dataclass(frozen=True)
class ScrapedPage:
    url: str
    title: str
    description: str
    text: str


def scrape_url(url: str, max_chars: int = 20_000, timeout: float = 10.0) -> ScrapedPage:
    """Fetch a page and return its useful text and metadata."""
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than zero")

    response = requests.get(
        url,
        headers={"User-Agent": "Mr-PeaBody/1.0"},
        timeout=timeout,
    )
    response.raise_for_status()
    parser = _PageParser()
    parser.feed(response.text)
    parser.close()

    title = " ".join("".join(parser.title_parts).split())
    description = unescape(parser.description)
    text = re.sub(r"\s+", " ", " ".join(parser.text_parts).strip())[:max_chars]

    return ScrapedPage(url=url, title=title, description=description, text=text)