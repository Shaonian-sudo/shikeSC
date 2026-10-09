# 试客商城电商 Web 系统 UI 自动化测试设计与实践

> 毕业设计项目：自研电商 Web 被测系统 + 基于 Selenium 与 Pytest 的四层 UI 自动化测试框架，含混合自愈定位机制。

## 项目简介

本课题针对现有 UI 自动化测试项目中"被测系统与测试框架割裂、演示站点高度同质化"的问题，自研电商被测系统 **试客商城（TestBuy Mall）**，并配套设计实现一套可落地的 UI 自动化测试框架。项目包含两大组成部分：

| 模块 | 目录 | 说明 |
|---|---|---|
| 被测系统 | `testbuy-mall/` | Flask + SQLite 自研电商站：注册登录、商品浏览/搜索/筛选/分页、购物车、下单结算、订单管理、后台管理 |
| 测试框架 | `testbuy-framework/` | Selenium 4 + pytest 四层架构：基础封装层 → 页面对象层 → 业务操作层 → 测试用例层，含数据驱动与混合自愈定位 |

## 技术栈

- **被测系统**：Python 3.13 / Flask / SQLite / Jinja2
- **测试框架**：Selenium 4 / pytest / pytest-html / Page Object Model
- **特色能力**：data-testid 测试标识规范、规则级 + LLM 级混合自愈定位、JSON 数据驱动、冒烟/回归分级

## 快速开始

```bash
# 1. 安装依赖
pip install -r testbuy-mall/requirements.txt -r testbuy-framework/requirements.txt

# 2. 初始化被测系统数据库并启动
cd testbuy-mall
python seed.py        # 生成管理员/测试用户与 16 件演示商品
python app.py         # 服务默认运行于 http://127.0.0.1:5000

# 3. 运行 UI 自动化测试（另开终端）
cd ../testbuy-framework
pip install -r requirements.txt
# 下载与本地 Chrome 版本匹配的 chromedriver 放入 drivers/ 目录
pytest tests/ -v --html=reports/report.html
```

## 框架架构

```
tests/            测试用例层（登录/商品/购物车/结算订单 4 大模块 24 用例，JSON 数据驱动）
  ↓
business/         业务操作层（TradeFlow 一站式购买业务流）
  ↓
pages/            页面对象层（7 大页面对象，POM 封装）
  ↓
core/             基础封装层（显式等待/定位/截图/日志/自愈定位回退链）
  ↓
testbuy-mall      被测系统（data-testid 测试标识，Selenium 驱动交互）
```

## 验收结果

全量 24 个用例通过（1 个正向场景由端到端用例覆盖而跳过），运行时长约 2.7 分钟，详见 `testbuy-framework/reports/report.html`。

## 目录结构

```
毕业设计/
├── testbuy-mall/           # 被测系统（Flask + SQLite）
├── testbuy-framework/      # 测试框架（Selenium + pytest 四层架构）
└── 开题报告_试客商城电商Web系统UI自动化测试设计与实践.docx
```

## 说明

- 浏览器驱动（chromedriver）需与本地 Chrome 版本匹配，下载后置于 `testbuy-framework/drivers/`。
- 被测系统所有交互元素均带 `data-testid` 属性，为自愈定位回退链提供首选定位依据。
