"""Crawler manager: dispatches search/detail requests to registered spiders."""
from __future__ import annotations

import asyncio
import logging
import time

from app.config import DATA_SOURCES
from app.spiders.base import BaseSpider, CompanySearchResult, CompanyDetailResult
from app.spiders.mock_spider import QichachaMockSpider

logger = logging.getLogger(__name__)

# Registry of available spiders
SPIDER_REGISTRY: dict[str, type[BaseSpider]] = {
    "mock": QichachaMockSpider,
}

# Try to register aiqicha spider (requires playwright)
try:
    from app.spiders.aiqicha_spider import AiqichaSpider
    SPIDER_REGISTRY["aiqicha"] = AiqichaSpider
except ImportError:
    logger.warning("Playwright not installed. aiqicha spider is disabled. "
                   "Run: python3 -m pip install playwright -i https://mirrors.aliyun.com/pypi/simple/")


def get_spider(source: str) -> BaseSpider:
    """Instantiate a spider by source name."""
    spider_cls = SPIDER_REGISTRY.get(source)
    if not spider_cls:
        raise ValueError(f"Unknown data source: {source}")
    return spider_cls()


async def search_companies(keyword: str, mode: str = "live", **filters) -> list[CompanySearchResult]:
    """Search across all enabled data sources concurrently, deduplicate, return merged results."""
    if mode == "mock":
        sources = ["mock"]
    else:
        sources = [s for s in DATA_SOURCES if s in SPIDER_REGISTRY]
        # Fallback to mock if no live sources available
        if not sources:
            logger.warning("No live data sources available, falling back to mock")
            sources = ["mock"]
    if not sources:
        logger.warning("No data sources available")
        return []

    async def _search_one(source: str) -> list[CompanySearchResult]:
        try:
            spider = get_spider(source)
            return await spider.search(keyword, **filters)
        except Exception as e:
            logger.error(f"Search failed on source {source}: {e}")
            return []

    tasks = [_search_one(s) for s in sources]
    results = await asyncio.gather(*tasks)

    # Flatten and deduplicate by credit_code (or name if no credit_code)
    seen = set()
    merged = []
    for items in results:
        for item in items:
            key = item.credit_code or item.name
            if key not in seen:
                seen.add(key)
                merged.append(item)
    return merged


async def get_company_detail(company: CompanySearchResult) -> CompanyDetailResult:
    """Fetch full detail for a company from its source."""
    spider = get_spider(company.source)
    return await spider.get_detail(company)
