# -*- coding: utf-8 -*-
"""结算与订单模块测试：完整下单、参数缺失、订单状态流转。"""
import pytest

from business.trade_flow import TradeFlow
from pages.cart_page import CartPage
from pages.order_page import OrderPage
from pages.product_page import ProductPage
from utils.data_loader import load_checkout_cases


@pytest.fixture()
def flow(driver, base_url):
    return TradeFlow(driver, base_url)


@pytest.mark.smoke
def test_full_checkout(driver, base_url, flow):
    """端到端核心流程：登录→搜索→加购→结算→下单成功。"""
    order_no = flow.buy(
        "buyer", "Test@123", "智能手表",
        "张三", "13800138000", "重庆市渝北区测试大道 1 号", quantity=1)
    assert order_no.startswith("TB"), f"订单号格式异常: {order_no}"


@pytest.mark.regression
@pytest.mark.parametrize("case", load_checkout_cases(),
                         ids=lambda c: c["scenario"])
def test_checkout_param_missing(driver, base_url, flow, case):
    """数据驱动：收货信息缺失时下单被拦截。"""
    if case["expect"] == "success":
        pytest.skip("正向场景由 test_full_checkout 覆盖")
    flow.login("buyer", "Test@123")
    flow.search_and_open_product("保温杯")
    ProductPage(driver).add_to_cart(1)
    flow.checkout(case["receiver"], case["phone"], case["address"])
    assert not flow.order_page.is_success(), "缺参数仍下单成功"
    assert flow.checkout_page.has_error(), "未出现错误提示"


@pytest.mark.regression
def test_cart_cleared_after_order(driver, base_url, flow):
    """下单成功后购物车被清空。"""
    flow.buy("buyer", "Test@123", "香薰加湿器",
             "李四", "13900139000", "重庆市南岸区测试路 8 号")
    cart = CartPage(driver)
    cart.open_cart(base_url)
    assert cart.is_empty(), "下单后购物车未清空"


@pytest.mark.regression
def test_order_status_pending(driver, base_url, flow):
    """新订单初始状态为待付款。"""
    flow.buy("buyer", "Test@123", "帆布包",
             "王五", "13700137000", "重庆市九龙坡区测试街 6 号")
    orders = flow.order_page
    orders.open_orders(base_url)
    assert orders.first_status() == "待付款", "新订单状态不正确"


@pytest.mark.regression
def test_cancel_order(driver, base_url, flow):
    """待付款订单可取消，状态变为已取消。"""
    flow.buy("buyer", "Test@123", "台灯",
             "赵六", "13600136000", "重庆市沙坪坝区测试巷 3 号")
    order = flow.order_page
    order.open_orders(base_url)
    order.open_first_detail()
    order.cancel_order()
    order.wait_status("已取消")
    assert order.status_text() == "已取消", "取消订单后状态未更新"


@pytest.mark.regression
def test_orders_list_shows_history(driver, base_url, flow):
    """下单后订单列表出现记录。"""
    flow.buy("buyer", "Test@123", "面膜",
             "孙七", "13500135000", "重庆市江北区测试院 2 号")
    orders = flow.order_page
    orders.open_orders(base_url)
    assert orders.order_count() >= 1, "订单列表为空"
