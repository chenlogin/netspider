# NetSpider

企业信息网络爬虫系统 — 根据关键词在公网检索公司列表，并抓取目标公司的详细信息。

## 快速开始

```bash
# 1. 安装依赖（使用阿里云镜像加速）
python3 -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 2. 安装 Playwright 浏览器
python3 -m playwright install chromium --with-deps

# 3. 启动服务
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问：
- **前端界面**：http://localhost:8000
FastAPI 基于以下信息自动生成 OpenAPI 规范（JSON），再由 Swagger UI 渲染为可视化页面
- **API 文档**：http://localhost:8000/docs （Swagger UI，可在线调试接口）
- **Redoc 文档**：http://localhost:8000/redoc （Redoc UI，更美观的静态文档排版，适合阅读）

## 数据源模式

前端搜索栏右侧提供 **Mock / 爱企查** 切换按钮：

| 模式 | 说明 | 依赖 |
|------|------|------|
| **Mock 数据** | 内置 8 条模拟公司数据，用于快速演示和开发 | 无 |
| **爱企查实时** | 通过 Playwright 无头浏览器从 aiqicha.baidu.com 实时抓取 | `playwright` + Chromium |

> 如果 Playwright 未安装，切换到"爱企查实时"模式时会自动降级到 Mock 数据，并在日志中提示安装命令。

## 安装 Playwright（可选）

```bash
# 安装 playwright 包（使用阿里云镜像加速）
python3 -m pip install playwright -i https://mirrors.aliyun.com/pypi/simple/

# 下载 Chromium 浏览器
python3 -m playwright install chromium --with-deps
```

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
    base.py          # 爬虫基类
    mock_spider.py   # Mock 数据源（8 条样本）
    aiqicha_spider.py # 爱企查爬虫（Playwright）
    manager.py       # 爬虫调度器
static/
  index.html       # 前端界面
```

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/companies/search | 搜索公司列表（body 可传 mode: "mock"/"live"） |
| GET  | /api/companies/{id}/detail | 获取公司详情 |
| GET  | /api/companies/export?format=csv | 导出结果 |
| GET  | /api/companies/logs | 爬取日志 |
| GET  | /api/companies/config | 当前爬虫配置 |

## 扩展数据源

在 `app/spiders/` 下新建爬虫文件，继承 `BaseSpider` 实现 `search()` 和 `get_detail()` 方法，然后在 `manager.py` 的 `SPIDER_REGISTRY` 中注册，并在 `config.py` 的 `DATA_SOURCES` 中启用即可。
