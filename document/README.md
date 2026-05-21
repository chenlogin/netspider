# NetSpider PRD 生成记录

## 背景

创建 NetSpider（网络爬虫项目）的产品需求文档（PRD），以 HTML 格式导出。

## 项目需求

1. 根据输入诉求在公网上查找满足条件的公司列表
2. 选中某个公司抓取该公司的详细信息

## 对话过程

### 第 1 轮：创建 PRD 文档

**用户输入：**
> 这是一个网路爬虫项目，目前需要创建项目prd，以html形式导出。项目要求：1、根据输入诉求在公网上查找满足条件的公司列表2、选中某个公司抓取该公司的详细信息

**处理过程：**
- 查看项目目录结构，确认 `document/` 目录存在且为空
- 创建完整的 PRD 文档，包含以下章节：
  1. 产品概述
  2. 用户角色
  3. 功能需求（F-001 ~ F-005）
  4. 功能优先级总览
  5. 系统架构（逻辑架构图 + 技术选型建议）
  6. 非功能需求
  7. 数据模型设计（3 张表）
  8. 接口设计（3 个 API 端点）
  9. 项目规划（MVP / V1.1 / V1.2）
  10. 风险与约束
- 文件初始保存位置：`document/prd.html`

### 第 3 轮：根据 PRD 补充业务代码

**用户输入：**
> 根据PRD补充业务代码

**处理过程：**
- 按照 PRD 的 MVP 范围（F-001 + F-002）设计四层架构：
  - **抽象契约层**（`app/spiders/base.py`）：定义 `BaseSpider` 抽象基类，强制实现 `search()` 和 `get_detail()` 方法
  - **爬虫调度层**（`app/spiders/manager.py`）：支持多数据源并发查询（`asyncio.gather`）、结果去重合并、降级容错
  - **具体实现层**（`app/spiders/mock_spider.py`）：Mock 数据源，8 条预设公司数据，用于 MVP 阶段测试
  - **API 路由层**（`app/routers/companies.py`）：实现 4 个端点 — 搜索、详情、导出、日志
- 定义数据模型（`app/models/company.py`）：`Company`、`SearchRecord`、`CrawlLog` 三张表
- 实现缓存机制：详情首次爬取后落库，后续直接从 SQLite 读取，避免重复请求外部网站
- 前端界面（`static/index.html`）：搜索框 + 左侧结果列表 + 右侧详情面板，纯 HTML/CSS/JS，无外部依赖
- 入口文件（`app/main.py`）：FastAPI 应用启动，自动创建数据库表，挂载静态文件和路由
- 依赖文件（`requirements.txt`）：FastAPI + Uvicorn + httpx + BeautifulSoup4 + SQLAlchemy + Pydantic

### 第 4 轮：详细解释爬数据逻辑

**用户输入：**
> 详细解释爬数据逻辑是如何实现的

**处理过程：**
- 撰写并输出 `document/crawl_logic.html` 文档，包含：
  1. 四层架构图（路由层 → 调度层 → Spider 层 → 抽象契约）
  2. 逐层详解（每层的核心方法、输入输出、执行步骤、文件位置）
  3. 关键设计决策总结（并发、去重、降级、缓存、限频、扩展性）
  4. 数据流转时序图（从用户请求到数据库返回的完整交互流程）
  5. 从 Mock 到真实爬虫的迁移路径（6 步操作指南）

### 第 5 轮：快速开始项目

**用户输入：**
> 快速开始项目

**处理过程：**
- 修复 Python 3.9 兼容性问题：
  - `str | None` 语法在 Python 3.9 的 Pydantic 2.x 下报错，改为 `Optional[str]`
  - 所有文件头部添加 `from __future__ import annotations`
- 安装依赖（因网络超时重试），成功安装所有包
- 启动服务并验证：
  - 搜索 API 返回 4 条匹配"科技"的公司结果 ✅
  - 详情 API 返回完整工商信息 ✅
  - 前端页面正常加载 ✅
- 更新 `README.md` 快速开始部分：修正启动命令为 `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

### 第 6 轮：API 文档是如何生成的

**用户输入：**
> api文档是如何生成的

**处理过程：**
- 撰写并输出 `document/api_doc_discussion.html` 文档，解释：
  1. FastAPI 自动生成原理（路由装饰器 + Pydantic 模型 + FastAPI 参数三要素）
  2. 代码与文档对应关系（以搜索接口为例逐行拆解）
  3. Swagger UI（可调试）和 ReDoc（美观阅读）两个访问地址
  4. Pydantic 模型翻译为 JSON Schema 的完整示例

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
