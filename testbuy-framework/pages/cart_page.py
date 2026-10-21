# -*- coding: utf-8 -*-
"""购物车页页面对象。"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from core.base_page import BasePage


class CartPage(BasePage):
    ITEMS = (By.CSS_SELECTOR, "[data-testid='cart-item']")
    ITEM_NAMES = (By.CSS_SELECTOR, "[data-testid='cart-item-name']")
    QTY_INPUT = (By.CSS_SELECTOR, "[data-testid='cart-qty']")
    QTY_UPDATE = (By.CSS_SELECTOR, "[data-testid='cart-qty-update']")
    REMOVE_BTN = (By.CSS_SELECTOR, "[data-testid='cart-remove']")
    TOTAL = (By.CSS_SELECTOR, "[data-testid='cart-total']")
    GO_CHECKOUT = (By.CSS_SELECTOR, "[data-testid='go-checkout']")
    EMPTY = (By.CSS_SELECTOR, "[data-testid='empty-cart']")

    def open_cart(self, base_url: str):
        self.open(f"{base_url}/cart", expect="/cart")
        return self

    def wait_loaded(self, timeout: float = 8):
        """等待购物车列表或空提示渲染完成。"""
        try:
            self.wait.until(lambda d: self.find_all(*self.ITEMS) or self.is_visible(*self.EMPTY, timeout=0.5))
        except Exception:
            pass

    def item_count(self) -> int:
        self.wait_loaded()
        return len(self.find_all(*self.ITEMS))

    def item_names(self) -> list[str]:
        self.wait_loaded()
        return [el.text.strip() for el in self.find_all(*self.ITEM_NAMES)]

    def update_first_qty(self, quantity: int):
        self.input_text(*self.QTY_INPUT, str(quantity))
        self.click(*self.QTY_UPDATE)

    def wait_qty_value(self, expected: str, timeout: float = 8):
        """等待第一个数量输入框的值更新到期望值（表单提交后页面刷新）。"""
        from selenium.common.exceptions import StaleElementReferenceException

        def _pred(_d):
            try:
                items = self.find_all(*self.QTY_INPUT)
                return bool(items) and items[0].get_attribute("value") == expected
            except StaleElementReferenceException:
                return False  # 页面刷新中，继续轮询

        WebDriverWait(self.driver, timeout).until(_pred)

    def remove_first(self):
        self.click(*self.REMOVE_BTN)

    def clear_all(self, max_items: int = 20):
        """逐行删除购物车商品直至为空；每次删除后等待新页面渲染完成。"""
        self.wait_loaded()
        for _ in range(max_items):
            items = self.find_all(*self.ITEMS)
            if not items:
                return
            before = len(items)
            self.click(*self.REMOVE_BTN)
            # 等待本次删除生效：购物车项减少或变空（新页面），避免旧 DOM 误判
            try:
                self.wait.until(
                    lambda d: not self.find_all(*self.ITEMS)
                    or len(self.find_all(*self.ITEMS)) != before)
            except Exception:
                pass
        if self.find_all(*self.ITEMS):
            raise AssertionError("购物车未能清空")

    def total_text(self) -> str:
        return self.get_text(*self.TOTAL)

    def go_checkout(self):
        self.click(*self.GO_CHECKOUT)

    def is_empty(self) -> bool:
        return self.is_visible(*self.EMPTY, timeout=3)
