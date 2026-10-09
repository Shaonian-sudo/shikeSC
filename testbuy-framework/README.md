# TestBuy-Framework

《基于 Selenium 与 Pytest 的电商 Web 系统 UI 自动化测试框架设计与实现》· 测试框架部分。
被测系统为 [试客商城 TestBuy Mall](../testbuy-mall)。

## 架构（四层解耦 + 横切能力）

```
tests/          测试用例层   pytest 用例 + JSON 数据驱动
business/       业务操作层   TradeFlow 跨页面业务流封装
pages/          页面对象层   POM，每页一个类，元素与操作封装
core/           基础封装层   driver / base_page / 自愈定位 / 日志
config/         配置与测试数据（settings.py / test_data/*.json）
```

## 核心特性

- **POM 四层架构**：页面操作与测试逻辑彻底分离，页面改版只改 pages/
- **数据驱动**：users.json / checkout.json + pytest 参数化
- **显式等待封装**：无硬编码 sleep，元素等待统一收敛到 BasePage
- **失败自动截图**：pytest hook 失败时自动截图并记录
- **日志双输出**：控制台 + 文件
- **AI 自愈定位（亮点）**：定位失败时按属性回退链自动修复（规则级），可选 LLM 语义修复（LLM 级）；自愈事件统计可写入报告
- **冒烟/回归分级**：`@pytest.mark.smoke` / `@pytest.mark.regression`
- **HTML 报告**：pytest-html 独立报告，含截图

## 运行

```bash
# 1. 启动被测系统
cd ../testbuy-mall && python seed.py && python app.py

# 2. 运行全部用例
cd ../testbuy-framework
pip install -r requirements.txt
pytest tests/ -v

# 冒烟 / 回归
pytest tests/ -m smoke -v
pytest tests/ -m regression -v

# 无头模式 / 自愈开关
set TESTBUY_HEADLESS=1
set TESTBUY_SELF_HEAL=1
```

## 用例覆盖（24 个）

| 模块 | 数量 | 覆盖内容 |
|---|---|---|
| 登录 | 6 | 数据驱动登录（成功/错误密码/空用户名/空密码/不存在用户）、注册新用户并登录 |
| 商品 | 6 | 首页加载、分类筛选、关键词搜索、空结果、分页、列表与详情价格一致 |
| 购物车 | 5 | 加购、多数量合并、修改数量、删除、未登录拦截 |
| 结算订单 | 7 | 端到端下单、缺收货人、缺地址、下单后清空购物车、订单状态、取消订单、订单列表 |
