# NetSpider

企业信息网络爬虫系统 — 根据关键词在公网检索公司列表，并抓取目标公司的详细信息。

## 快速开始

```bash
# 1. 安装依赖
python3 -m pip install -r requirements.txt

# 2. 启动服务
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问：
- **前端界面**：http://localhost:8000
FastAPI 基于以下信息自动生成 OpenAPI 规范（JSON），再由 Swagger UI 渲染为可视化页面
- **API 文档**：http://localhost:8000/docs （Swagger UI，可在线调试接口）
- **Redoc 文档**：http://localhost:8000/redoc （Redoc UI，更美观的静态文档排版，适合阅读）

## 项目结构

```
app/
  main.py          # FastAPI 应用入口
  config.py        # 配置项
  database.py      # 数据库连接
  schemas.py       # Pydantic 数据模型
  models/
    company.py     # SQLAlchemy ORM 模型
  routers/
    companies.py   # API 路由
  spiders/
    base.py        # 爬虫基类
    mock_spider.py # Mock 数据源（MVP 用）
    manager.py     # 爬虫调度器
static/
  index.html       # 前端界面
```

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/companies/search | 搜索公司列表 |
| GET  | /api/companies/{id}/detail | 获取公司详情 |
| GET  | /api/companies/export?format=csv | 导出结果 |
| GET  | /api/companies/logs | 爬取日志 |

## 扩展数据源

在 `app/spiders/` 下新建爬虫文件，继承 `BaseSpider` 实现 `search()` 和 `get_detail()` 方法，然后在 `manager.py` 的 `SPIDER_REGISTRY` 中注册，并在 `config.py` 的 `DATA_SOURCES` 中启用即可。
