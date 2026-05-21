from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SearchRequest(BaseModel):
    keyword: str
    filters: Optional[dict] = None


class CompanyBrief(BaseModel):
    id: int
    name: str
    credit_code: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class CompanyDetail(BaseModel):
    id: int
    name: str
    credit_code: Optional[str] = None
    legal_representative: Optional[str] = None
    registered_capital: Optional[str] = None
    establish_date: Optional[str] = None
    address: Optional[str] = None
    business_scope: Optional[str] = None
    status: Optional[str] = None
    industry: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SearchResponse(BaseModel):
    total: int
    companies: list[CompanyBrief]


class CrawlLogBrief(BaseModel):
    id: int
    task_type: str
    source: str
    status: str
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    created_at: datetime
