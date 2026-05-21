from __future__ import annotations

import csv
import io
import json
import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import DATA_SOURCES, CRAWL_MODE
from app.database import get_db
from app.models.company import Company, CrawlLog, SearchRecord
from app.schemas import (
    CompanyBrief,
    CompanyDetail,
    CrawlLogBrief,
    ConfigResponse,
    SearchRequest,
    SearchResponse,
)
from app.spiders.base import CompanySearchResult
from app.spiders.manager import get_company_detail, search_companies

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/companies", tags=["companies"])


def _to_orm(result: CompanySearchResult, db_company: Company | None = None) -> Company:
    """Ensure a Company ORM instance exists in DB for a search result."""
    if db_company:
        return db_company
    company = Company(
        name=result.name,
        credit_code=result.credit_code,
        address=result.address,
        industry=result.industry,
        source=result.source,
        source_url=result.source_url,
    )
    return company


def _log_crawl(db: Session, task_type: str, source: str, url: str, status: str, duration_ms: int, error: str = ""):
    """Record a crawl log entry."""
    entry = CrawlLog(
        task_type=task_type,
        source=source,
        url=url,
        status=status,
        duration_ms=duration_ms,
        error=error,
    )
    db.add(entry)
    db.commit()


@router.post("/search", response_model=SearchResponse)
async def search_companies_api(req: SearchRequest, db: Session = Depends(get_db)):
    """Search companies by keyword across enabled data sources."""
    start = time.time()
    try:
        filters = req.filters or {}
        mode = req.mode or CRAWL_MODE
        results = await search_companies(req.keyword, mode=mode, **filters)

        # Record search
        record = SearchRecord(
            keyword=req.keyword,
            filters=str(req.filters) if req.filters else None,
            result_count=len(results),
        )
        db.add(record)

        # Store/update companies in DB
        orm_ids = []
        for r in results:
            existing = db.query(Company).filter(
                Company.credit_code == r.credit_code,
                Company.source == r.source,
            ).first() if r.credit_code else None
            company = _to_orm(r, existing)
            if not company.id:
                db.add(company)
                db.flush()
            orm_ids.append(company.id)

        db.commit()

        # Build response
        companies = [
            CompanyBrief(
                id=company_id,
                name=r.name,
                credit_code=r.credit_code,
                address=r.address,
                industry=r.industry,
                source=r.source,
                source_url=r.source_url,
            )
            for company_id, r in zip(orm_ids, results)
        ]

        duration_ms = int((time.time() - start) * 1000)
        _log_crawl(db, "search", "all", "", "success", duration_ms)

        return SearchResponse(total=len(companies), companies=companies)

    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        _log_crawl(db, "search", "all", "", "failed", duration_ms, str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """Get current crawler configuration."""
    return ConfigResponse(
        crawl_mode=CRAWL_MODE,
        sources=DATA_SOURCES,
    )


@router.get("/{company_id}/detail", response_model=CompanyDetail)
async def get_detail_api(company_id: int, db: Session = Depends(get_db)):
    """Fetch full detail for a company, scraping if not cached."""
    start = time.time()
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if we already have detail fields cached
    has_detail = company.legal_representative or company.registered_capital or company.business_scope
    if has_detail:
        return CompanyDetail(
            id=company.id,
            name=company.name,
            credit_code=company.credit_code,
            legal_representative=company.legal_representative,
            registered_capital=company.registered_capital,
            establish_date=company.establish_date,
            address=company.address,
            business_scope=company.business_scope,
            status=company.status,
            industry=company.industry,
            phone=company.phone,
            email=company.email,
            website=company.website,
            source=company.source,
            source_url=company.source_url,
            created_at=company.created_at,
            updated_at=company.updated_at,
        )

    # Scrape from source
    search_result = CompanySearchResult(
        name=company.name,
        credit_code=company.credit_code,
        address=company.address,
        industry=company.industry,
        source=company.source,
        source_url=company.source_url,
    )

    try:
        detail = await get_company_detail(search_result)

        # Update company record
        company.legal_representative = detail.legal_representative
        company.registered_capital = detail.registered_capital
        company.establish_date = detail.establish_date
        company.business_scope = detail.business_scope
        company.status = detail.status
        company.phone = detail.phone
        company.email = detail.email
        company.website = detail.website
        db.commit()

        duration_ms = int((time.time() - start) * 1000)
        _log_crawl(db, "detail", detail.source, detail.source_url, "success", duration_ms)

        return CompanyDetail(
            id=company.id,
            name=company.name,
            credit_code=company.credit_code,
            legal_representative=company.legal_representative,
            registered_capital=company.registered_capital,
            establish_date=company.establish_date,
            address=company.address,
            business_scope=company.business_scope,
            status=company.status,
            industry=company.industry,
            phone=company.phone,
            email=company.email,
            website=company.website,
            source=company.source,
            source_url=company.source_url,
            created_at=company.created_at,
            updated_at=company.updated_at,
        )

    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        _log_crawl(db, "detail", company.source, company.source_url, "failed", duration_ms, str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_companies(
    fmt: str = Query("csv", regex="^(csv|json)$"),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Export company search results as CSV or JSON."""
    query = db.query(Company)
    if keyword:
        query = query.filter(Company.name.contains(keyword) | Company.business_scope.contains(keyword))
    companies = query.all()

    if fmt == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "id", "name", "credit_code", "legal_representative", "registered_capital",
            "establish_date", "address", "business_scope", "status", "industry",
            "phone", "email", "website", "source",
        ])
        for c in companies:
            writer.writerow([
                c.id, c.name, c.credit_code, c.legal_representative, c.registered_capital,
                c.establish_date, c.address, c.business_scope, c.status, c.industry,
                c.phone, c.email, c.website, c.source,
            ])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=companies.csv"},
        )

    elif fmt == "json":
        data = [
            {
                "id": c.id,
                "name": c.name,
                "credit_code": c.credit_code,
                "legal_representative": c.legal_representative,
                "registered_capital": c.registered_capital,
                "establish_date": c.establish_date,
                "address": c.address,
                "business_scope": c.business_scope,
                "status": c.status,
                "industry": c.industry,
                "phone": c.phone,
                "email": c.email,
                "website": c.website,
                "source": c.source,
            }
            for c in companies
        ]
        return StreamingResponse(
            iter([json.dumps(data, ensure_ascii=False, indent=2)]),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=companies.json"},
        )


@router.get("/logs", response_model=list[CrawlLogBrief])
async def get_crawl_logs(limit: int = Query(50, le=200), db: Session = Depends(get_db)):
    """Return recent crawl logs."""
    logs = db.query(CrawlLog).order_by(CrawlLog.id.desc()).limit(limit).all()
    return [
        CrawlLogBrief(
            id=l.id,
            task_type=l.task_type,
            source=l.source,
            status=l.status,
            duration_ms=l.duration_ms,
            error=l.error,
            created_at=l.created_at,
        )
        for l in logs
    ]
