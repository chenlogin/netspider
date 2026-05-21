"""Aiqicha (百度爱企查) spider using Playwright headless browser."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from app.spiders.base import BaseSpider, CompanySearchResult, CompanyDetailResult

logger = logging.getLogger(__name__)

# Regex to extract embedded JSON from search result page <script> tags
SEARCH_DATA_RE = re.compile(r'window\.(?:pageData|searchData)\s*=\s*({.*?})\s*;?\s*</script>', re.DOTALL)
DETAIL_DATA_RE = re.compile(r'window\.(?:pageData|detailData)\s*=\s*({.*?})\s*;?\s*</script>', re.DOTALL)


class AiqichaSpider(BaseSpider):
    """Scrape company data from aiqicha.baidu.com using Playwright."""

    source_name = "aiqicha"

    # Reuse a single browser instance across calls
    _browser: Optional[Browser] = None
    _context: Optional[BrowserContext] = None

    async def _get_page(self) -> Page:
        """Get or create a browser page."""
        if self._browser is None:
            pw = await async_playwright().start()
            self._browser = await pw.chromium.launch(headless=True)
            self._context = await self._browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ),
            )
        page = await self._context.new_page()
        return page

    async def _extract_json_from_page(self, page: Page, pattern: re.Pattern) -> Optional[dict]:
        """Extract embedded JSON data from page HTML using regex."""
        html = await page.content()
        match = pattern.search(html)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                logger.warning("Failed to parse embedded JSON from page")
        return None

    async def search(self, keyword: str, **filters) -> list[CompanySearchResult]:
        """Search companies on aiqicha.baidu.com by keyword."""
        page = await self._get_page()
        url = f"https://aiqicha.baidu.com/s?q={keyword}"
        results = []

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait for search results to render
            await page.wait_for_selector(".search-table, .company-list, .result-list", timeout=10000)

            # Try to extract embedded JSON first
            data = await self._extract_json_from_page(page, SEARCH_DATA_RE)
            if data and "result" in data:
                for item in data["result"].get("list", []):
                    results.append(CompanySearchResult(
                        name=item.get("entName", ""),
                        credit_code=item.get("taxNo", "") or item.get("orgid", ""),
                        address=item.get("regAddr", "") or item.get("address", ""),
                        industry=item.get("industry", ""),
                        source=self.source_name,
                        source_url=f"https://aiqicha.baidu.com/company_detail_{item.get('pid', '')}",
                        extra=item,
                    ))
                return results

            # Fallback: parse HTML directly
            items = await page.query_selector_all(".search-table .search-result-item, .company-list .item")
            for item in items:
                name_el = await item.query_selector(".name, .entName, a.title")
                name = (await name_el.inner_text()).strip() if name_el else ""
                if not name:
                    continue

                link_el = await item.query_selector("a")
                href = (await link_el.get_attribute("href")) if link_el else ""
                pid_match = re.search(r"(\d+)", href) if href else None
                pid = pid_match.group(1) if pid_match else ""

                credit_el = await item.query_selector(".credit-code, .taxNo, .regNo")
                credit_code = (await credit_el.inner_text()).strip() if credit_el else ""

                results.append(CompanySearchResult(
                    name=name,
                    credit_code=credit_code,
                    source=self.source_name,
                    source_url=f"https://aiqicha.baidu.com/company_detail_{pid}" if pid else href,
                ))
        except Exception as e:
            logger.error(f"Search failed for keyword '{keyword}': {e}")
        finally:
            await page.close()

        return results

    async def get_detail(self, company: CompanySearchResult) -> CompanyDetailResult:
        """Scrape full company detail from aiqicha.baidu.com."""
        page = await self._get_page()
        url = company.source_url
        if not url and company.credit_code:
            url = f"https://aiqicha.baidu.com/s?q={company.credit_code}"

        detail = CompanyDetailResult(
            name=company.name,
            credit_code=company.credit_code,
            source=self.source_name,
            source_url=url,
        )

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Try embedded JSON extraction
            data = await self._extract_json_from_page(page, DETAIL_DATA_RE)
            if data:
                basic = data.get("basicInfo", data.get("data", {}))
                detail = CompanyDetailResult(
                    name=basic.get("entName", company.name),
                    credit_code=basic.get("taxNo", company.credit_code),
                    legal_representative=basic.get("legalPerson", basic.get("operator", "")),
                    registered_capital=basic.get("regCapital", basic.get("regCapitalAmount", "")),
                    establish_date=basic.get("startDate", basic.get("startDatePub", "")),
                    address=basic.get("regAddr", basic.get("address", "")),
                    business_scope=basic.get("businessScope", basic.get("scope", "")),
                    status=basic.get("regStatus", basic.get("openStatus", "")),
                    industry=basic.get("industry", ""),
                    phone=basic.get("telephone", ""),
                    email=basic.get("email", ""),
                    website=basic.get("website", ""),
                    source=self.source_name,
                    source_url=url,
                )
                return detail

            # Fallback: parse HTML detail fields
            field_map = {
                "法定代表人": "legal_representative",
                "注册资本": "registered_capital",
                "成立日期": "establish_date",
                "注册地址": "address",
                "经营范围": "business_scope",
                "经营状态": "status",
                "所属行业": "industry",
                "联系电话": "phone",
                "邮箱": "email",
                "网址": "website",
            }

            for label, field_name in field_map.items():
                el = await page.query_selector(f"text='{label}' >> .. .content, text='{label}' >> + *")
                if el:
                    value = (await el.inner_text()).strip()
                    if value and value != "--":
                        setattr(detail, field_name, value)
        except Exception as e:
            logger.error(f"Detail scrape failed for {company.name}: {e}")
        finally:
            await page.close()

        return detail

    async def close(self):
        """Clean up browser resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._context = None
