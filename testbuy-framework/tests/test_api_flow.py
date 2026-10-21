# -*- coding: utf-8 -*-
"""接口自动化测试：requests 直调试客商城 HTTP 接口。

覆盖：商品浏览与搜索、注册登录、会话权限控制、购物车、下单结算、订单管理。
与 UI 测试（Selenium）互补：接口层验证业务链路与状态码，UI 层验证界面交互。
运行前提：被测系统已启动（python seed.py && python app.py）。
"""
import time

import pytest
import requests

from config.settings import BASE_URL

pytestmark = [pytest.mark.api, pytest.mark.regression]


# ================= 商品浏览与搜索 =================

@pytest.mark.smoke
def test_homepage_ok(api_anon, api_base_url):
    """首页返回 200 且渲染商品区。"""
    r = api_anon.get(f"{api_base_url}/")
    assert r.status_code == 200
    assert "试客商城" in r.text


@pytest.mark.parametrize("pid", [1, 2, 3])
def test_product_detail_ok(api_anon, api_base_url, pid):
    """在售商品详情页可访问。"""
    r = api_anon.get(f"{api_base_url}/product/{pid}")
    assert r.status_code == 200


def test_product_detail_404(api_anon, api_base_url):
    """不存在的商品返回 404。"""
    r = api_anon.get(f"{api_base_url}/product/99999")
    assert r.status_code == 404


def test_search_keyword(api_anon, api_base_url):
    """关键词搜索命中商品。"""
    r = api_anon.get(f"{api_base_url}/", params={"keyword": "耳机"})
    assert r.status_code == 200
    assert "无线降噪耳机" in r.text


def test_unknown_route_404(api_anon, api_base_url):
    """未知路由返回 404 错误页。"""
    r = api_anon.get(f"{api_base_url}/no-such-page")
    assert r.status_code == 404


# ================= 注册与登录 =================

@pytest.mark.smoke
def test_register_new_user(api_anon, api_base_url):
    """注册新用户成功后重定向到登录页。"""
    r = api_anon.post(
        f"{api_base_url}/register",
        data={"username": f"reg_{time.time():.0f}",
              "password": "Passw0rd!",
              "email": "reg@testbuy.local"},
        allow_redirects=False,
    )
    assert r.status_code == 302
    assert "/login" in r.headers.get("Location", "")


@pytest.mark.smoke
def test_login_success(api_base_url):
    """seed 用户 buyer 正确密码登录成功，重定向到首页。

    使用独立会话，避免登录态污染共享的 api_anon（权限校验用例依赖其保持未登录）。
    """
    s = requests.Session()
    r = s.post(
        f"{api_base_url}/login",
        data={"username": "buyer", "password": "Test@123"},
        allow_redirects=False,
    )
    assert r.status_code == 302
    assert "/login" not in r.headers.get("Location", "")


def test_login_wrong_password(api_base_url):
    """错误密码登录失败：渲染登录页并给出错误提示（Flask 表单应用返回 200）。"""
    s = requests.Session()
    r = s.post(
        f"{api_base_url}/login",
        data={"username": "buyer", "password": "Wrong@123"},
        allow_redirects=False,
    )
    assert r.status_code == 200
    assert "用户名或密码错误" in r.text


# ================= 会话权限控制 =================

def test_cart_requires_login(api_anon, api_base_url):
    """未登录访问购物车被重定向到登录页（接口级权限校验）。"""
    r = api_anon.get(f"{api_base_url}/cart", allow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers.get("Location", "")


def test_checkout_requires_login(api_anon, api_base_url):
    """未登录提交结算被重定向到登录页。"""
    r = api_anon.post(
        f"{api_base_url}/checkout",
        data={"receiver": "x", "phone": "13800000000", "address": "x"},
        allow_redirects=False,
    )
    assert r.status_code == 302
    assert "/login" in r.headers.get("Location", "")


# ================= 购物车 / 下单 / 订单管理（完整业务链路） =================

@pytest.mark.smoke
def test_full_trade_flow(api_user, api_base_url):
    """登录 → 加购 → 购物车 → 结算下单 → 订单详情 → 取消订单 全链路。"""
    s = api_user["session"]

    # 加购
    r = s.post(f"{api_base_url}/cart/add",
               data={"product_id": 1, "quantity": 2}, allow_redirects=False)
    assert r.status_code == 302, "加购应重定向"

    # 购物车页面包含该商品
    r = s.get(f"{api_base_url}/cart")
    assert r.status_code == 200
    assert "智能手表 Pro" in r.text

    # 结算下单（空购物车校验：先确认能访问）
    r = s.post(
        f"{api_base_url}/checkout",
        data={"receiver": "接口测试", "phone": "13800000000",
              "address": "重庆市渝北区"},
        allow_redirects=False,
    )
    assert r.status_code == 302, "下单应重定向到订单成功页"
    loc = r.headers.get("Location", "")
    assert "/order/success/" in loc
    order_id = int(loc.rsplit("/", 1)[-1])

    # 订单详情可访问
    r = s.get(f"{api_base_url}/order/{order_id}")
    assert r.status_code == 200

    # 订单列表包含订单号
    r = s.get(f"{api_base_url}/orders")
    assert r.status_code == 200

    # 取消订单后状态变为已取消
    r = s.post(f"{api_base_url}/order/{order_id}/cancel", allow_redirects=False)
    assert r.status_code == 302
    r = s.get(f"{api_base_url}/order/{order_id}")
    assert "已取消" in r.text
