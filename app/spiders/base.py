from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class CompanySearchResult:
    """Minimal company info returned from search."""
    name: str
    credit_code: str = ""
    address: str = ""
    industry: str = ""
    source: str = ""
    source_url: str = ""
    extra: dict = field(default_factory=dict)


@dataclass
class CompanyDetailResult:
    """Full company detail from detail scraping."""
    name: str = ""
    credit_code: str = ""
    legal_representative: str = ""
    registered_capital: str = ""
    establish_date: str = ""
    address: str = ""
    business_scope: str = ""
    status: str = ""
    industry: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    source: str = ""
    source_url: str = ""
    extra: dict = field(default_factory=dict)


class BaseSpider(ABC):
    """Abstract base for all crawlers."""

    source_name: str = "base"

    @abstractmethod
    async def search(self, keyword: str, **filters) -> list[CompanySearchResult]:
        """Search companies by keyword."""
        ...

    @abstractmethod
    async def get_detail(self, company: CompanySearchResult) -> CompanyDetailResult:
        """Scrape full detail for a company."""
        ...
