# -*- coding: utf-8 -*-
"""业务操作层：跨页面业务流，供用例复用。

典型场景：登录 → 搜索商品 → 加入购物车 → 结算 → 提交订单，返回订单号。
"""
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.index_page import IndexPage
from pages.login_page import LoginPage
from pages.order_page import OrderPage
from pages.product_page import ProductPage


class TradeFlow:
    """核心交易业务流封装。"""

    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url
        self.login_page = LoginPage(driver)
        self.index_page = IndexPage(driver)
        self.product_page = ProductPage(driver)
        self.cart_page = CartPage(driver)
        self.checkout_page = CheckoutPage(driver)
        self.order_page = OrderPage(driver)

    def login(self, username: str, password: str):
        self.login_page.open_login(self.base_url)
        self.login_page.login(username, password)
        return self

    def clear_cart(self):
        """清空购物车，保证用例从干净的购物车状态开始。"""
        self.cart_page.open_cart(self.base_url)
        self.cart_page.clear_all()
        return self

    def search_and_open_product(self, keyword: str, index: int = 0):
        """搜索商品并打开第 index 个结果。"""
        self.index_page.open_index(self.base_url)
        self.index_page.search(keyword)
        names = self.index_page.product_names()
        assert names, f"搜索 '{keyword}' 无结果"
        # 按名称定位商品卡点击（比固定下标更稳健）
        self.index_page.open_first_product()
        return names[index] if index < len(names) else names[0]

    def add_to_cart(self, quantity: int = 1):
        self.product_page.add_to_cart(quantity)

    def checkout(self, receiver: str, phone: str, address: str):
        """购物车 → 结算 → 提交订单。"""
        self.cart_page.open_cart(self.base_url)
        self.cart_page.go_checkout()
        self.checkout_page.fill(receiver, phone, address)
        self.checkout_page.submit()

    def buy(self, username: str, password: str, keyword: str,
            receiver: str, phone: str, address: str, quantity: int = 1) -> str:
        """一站式购买流程，返回订单号。"""
        self.login(username, password)
        self.search_and_open_product(keyword)
        self.add_to_cart(quantity)
        self.checkout(receiver, phone, address)
        assert self.order_page.is_success(), "下单失败，未出现成功页"
        return self.order_page.order_no()
