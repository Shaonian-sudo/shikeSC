# 试客商城 TestBuy Mall

自研轻量电商 Web 系统，作为《基于 Selenium 与 Pytest 的电商 Web 系统 UI 自动化测试框架设计与实现》毕设的被测系统（SUT）。

## 功能模块

- 用户：注册 / 登录 / 退出（Session + 密码哈希）
- 商品：列表 / 分类筛选 / 关键词搜索 / 分页 / 详情
- 购物车：加购 / 修改数量 / 删除 / 合计
- 订单：提交订单 / 订单列表 / 订单详情 / 取消订单（待付款、待发货可取消）
- 后台管理：商品增删改（上下架）/ 订单总览（仅管理员）

## 测试友好设计

所有关键交互元素均带 `data-testid` 属性（如 `data-testid="login-submit"`），
为 UI 自动化测试提供稳定、语义化的定位标识，是框架测试用例的定位基础。

## 快速开始

```bash
pip install -r requirements.txt
python seed.py        # 初始化数据库与演示数据
python app.py         # 启动，访问 http://127.0.0.1:5000
```

## 内置账号

| 角色 | 用户名 | 密码 |
|---|---|---|
| 管理员 | admin | Admin@123 |
| 测试用户 | buyer | Test@123 |

## 目录结构

```
testbuy-mall/
├── app.py            # Flask 应用入口与路由
├── models.py         # SQLite 数据访问层（DAO）
├── seed.py           # 数据初始化脚本
├── templates/        # Jinja2 页面模板
│   ├── base.html     # 导航 / 提示 / 页脚
│   ├── index.html    # 商品列表
│   ├── product.html  # 商品详情
│   ├── cart.html     # 购物车
│   ├── checkout.html # 结算
│   ├── orders.html   # 我的订单
│   └── admin/        # 后台管理页面
├── static/css/       # 样式
└── requirements.txt
```
