# NetSpider PRD 生成记录

## 背景

创建 NetSpider（网络爬虫项目）的产品需求文档（PRD），以 HTML 格式导出。

## 项目需求

1. 根据输入诉求在公网上查找满足条件的公司列表
2. 选中某个公司抓取该公司的详细信息

## 对话过程

### 1. 创建 PRD

**输入：** 爬虫项目创建 PRD（HTML），需求：根据关键词查找公司列表 + 抓取公司详情

**产出：** `document/prd.html` — 包含产品概述、功能需求（F-001~F-005）、系统架构、数据模型、API 设计、项目规划

### 2. 实现 MVP 代码

**输入：** 根据 PRD 实现代码

**产出：**
- 四层架构：抽象基类（base.py）→ 爬虫调度器（manager.py）→ Mock 数据源（mock_spider.py）→ API 路由（companies.py）
- 数据模型：Company / SearchRecord / CrawlLog 三张 SQLite 表
- 前端：搜索框 + 结果列表 + 详情面板（纯 HTML/CSS/JS）
- 缓存机制：详情首次爬取后落库，后续直接从 DB 读取

### 3. 详解爬取逻辑

**输入：** 详解爬取逻辑

**产出：** `document/crawl_logic.html` — 四层架构图、逐层流程、时序图、Mock 到真实爬虫的迁移路径

### 4. 启动验证 & 依赖优化

**输入：** 启动项目跑通流程；依赖安装太慢添加国内镜像

**处理：**
- 修复 Python 3.9 兼容性（`str | None` → `Optional[str]`）
- 所有 pip 命令添加阿里云镜像 `-i https://mirrors.aliyun.com/pypi/simple/`
- 验证通过：搜索"科技"返回 4 条结果 ✅，详情 API ✅，前端 ✅

### 5. API 文档原理

**输入：** API 文档如何自动生成

**产出：** `document/api_doc_discussion.html` — FastAPI 三要素（路由装饰器 + Pydantic 模型 + Query/Path 参数）如何映射为 OpenAPI 规范

### 6. 接入爱企查 + Mock/Live 切换

**输入：** 用爱企查实时抓取替换 Mock；保留 Mock，增加页面切换按钮

**处理：**
- 创建 `aiqicha_spider.py`（Playwright 无头浏览器，绕过 JS 加密）
- `SearchRequest` 新增 `mode` 字段，前端增加 Mock/爱企查切换按钮
- Playwright 延迟导入，未安装时自动降级到 Mock 模式
- 新增 `/api/companies/config` 配置端点

## 最终产物

```
document/
├── README.md              # 本文件：对话过程记录
├── prd.html               # 产品需求文档（PRD）V1.0
├── crawl_logic.html       # 爬取逻辑详解文档
└── api_doc_discussion.html # FastAPI 自动生成 API 文档详解
```

## 功能需求清单

| 编号 | 功能 | 优先级 | 里程碑 |
|------|------|--------|--------|
| F-001 | 公司列表检索 | P0 | MVP |
| F-002 | 公司详情抓取 | P0 | MVP |
| F-003 | 数据源管理 | P1 | V1.1 |
| F-004 | 结果导出 | P1 | V1.1 |
| F-005 | 爬取日志与监控 | P2 | V1.2 |
