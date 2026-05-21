from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    credit_code = Column(String(64), index=True)
    legal_representative = Column(String(128))
    registered_capital = Column(String(256))
    establish_date = Column(String(32))
    address = Column(Text)
    business_scope = Column(Text)
    status = Column(String(64))
    industry = Column(String(128))
    phone = Column(String(64))
    email = Column(String(128))
    website = Column(String(256))
    source = Column(String(128))
    source_url = Column(Text)
    detail = Column(Text)  # JSON string for extra fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SearchRecord(Base):
    __tablename__ = "search_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(Text, nullable=False)
    filters = Column(Text)  # JSON
    result_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(32))  # search / detail
    source = Column(String(128))
    url = Column(Text)
    status = Column(String(32))  # success / failed
    duration_ms = Column(Integer)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
