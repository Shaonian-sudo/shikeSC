# -*- coding: utf-8 -*-
"""购物车模块测试：加购、数量、删除、登录拦截。"""
import pytest

from business.trade_flow import TradeFlow
from pages.cart_page import CartPage
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.index_page import IndexPage


@pytest.fixture()
def logged_in(driver, base_url):
    """已登录且购物车已清空的会话上下文。"""
    flow = TradeFlow(driver, base_url)
    flow.login("buyer", "Test@123")
    flow.clear_cart()
    return flow


@pytest.mark.smoke
def test_add_to_cart(driver, base_url, logged_in):
    """从商品详情加购 1 件，购物车出现该商品。"""
    logged_in.search_and_open_product("智能手表")
    product = ProductPage(driver)
    name = product.name()
    product.add_to_cart(1)

    cart = CartPage(driver)
    cart.open_cart(base_url)
    assert cart.item_count() >= 1, "购物车无商品"
    assert name in cart.item_names(), f"购物车缺少商品 {name}"


@pytest.mark.regression
def test_add_multiple_quantity(driver, base_url, logged_in):
    """加购数量 3，小计与数量一致。"""
    logged_in.search_and_open_product("保温杯")
    ProductPage(driver).add_to_cart(3)
    cart = CartPage(driver)
    cart.open_cart(base_url)
    assert cart.item_count() == 1, "同商品重复加购应合并为一行"
    assert "合计" in cart.total_text(), "购物车合计未展示"


@pytest.mark.regression
def test_update_quantity(driver, base_url, logged_in):
    """修改购物车数量并保存。"""
    logged_in.search_and_open_product("T恤")
    ProductPage(driver).add_to_cart(1)
    cart = CartPage(driver)
    cart.open_cart(base_url)
    cart.update_first_qty(5)
    # 等待表单提交后数量输入框刷新，再读取
    cart.wait_qty_value("5")
    qty = cart.find_all(*(CartPage.QTY_INPUT))[0].get_attribute("value")
    assert qty == "5", f"数量更新失败，当前 {qty}"


@pytest.mark.regression
def test_remove_item(driver, base_url, logged_in):
    """删除购物车商品后购物车为空。"""
    logged_in.search_and_open_product("台灯")
    ProductPage(driver).add_to_cart(1)
    cart = CartPage(driver)
    cart.open_cart(base_url)
    cart.remove_first()
    assert cart.is_empty(), "删除后购物车未清空"


@pytest.mark.regression
def test_cart_requires_login(driver, base_url):
    """未登录访问购物车，跳转登录页。"""
    cart = CartPage(driver)
    cart.open_cart(base_url)
    login = LoginPage(driver)
    assert login.is_visible(*(LoginPage.USERNAME), timeout=3), "未登录未跳转登录页"
