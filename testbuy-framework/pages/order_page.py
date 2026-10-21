# -*- coding: utf-8 -*-
"""订单相关页面对象：下单成功页 / 我的订单 / 订单详情。"""
from selenium.webdriver.common.by import By

from core.base_page import BasePage


class OrderPage(BasePage):
    # 下单成功页
    SUCCESS_CARD = (By.CSS_SELECTOR, "[data-testid='order-success']")
    ORDER_NO = (By.CSS_SELECTOR, "[data-testid='order-no']")
    ORDER_AMOUNT = (By.CSS_SELECTOR, "[data-testid='order-amount']")
    # 订单列表
    ORDER_ROWS = (By.CSS_SELECTOR, "[data-testid='order-row']")
    ORDER_STATUS = (By.CSS_SELECTOR, "[data-testid='order-status']")
    ORDER_DETAIL_LINK = (By.CSS_SELECTOR, "[data-testid='order-detail-link']")
    EMPTY_ORDERS = (By.CSS_SELECTOR, "[data-testid='empty-orders']")
    # 订单详情
    CANCEL_BTN = (By.CSS_SELECTOR, "[data-testid='cancel-order']")
    ORDER_TOTAL = (By.CSS_SELECTOR, "[data-testid='order-total']")

    def open_orders(self, base_url: str):
        self.open(f"{base_url}/orders", expect="/orders")
        return self

    def is_success(self) -> bool:
        return self.is_visible(*self.SUCCESS_CARD, timeout=5)

    def order_no(self) -> str:
        return self.get_text(*self.ORDER_NO)

    def order_amount(self) -> str:
        return self.get_text(*self.ORDER_AMOUNT)

    def order_count(self) -> int:
        return len(self.find_all(*self.ORDER_ROWS))

    def first_status(self) -> str:
        return self.get_text(*self.ORDER_STATUS)

    def open_first_detail(self):
        self.click(*self.ORDER_DETAIL_LINK)
        self.wait_for_url("/order/")

    def cancel_order(self):
        self.click(*self.CANCEL_BTN)
        # 等待取消提交后的重定向刷新完成，避免读取到过期元素
        try:
            self.wait.until(lambda d: "/order/" in d.current_url
                            and d.execute_script("return document.readyState") == "complete")
        except Exception:
            pass

    def status_text(self) -> str:
        return self.get_text(*self.ORDER_STATUS)

    def wait_status(self, expected: str, timeout: float = 8):
        """轮询等待订单状态变为期望值；页面刷新期间的 stale 由 WebDriverWait 自动重试。"""
        try:
            self.wait.until(
                lambda d: d.find_element(*self.ORDER_STATUS).text.strip() == expected)
        except Exception:
            pass

    def total_text(self) -> str:
        return self.get_text(*self.ORDER_TOTAL)

    def has_empty_orders(self) -> bool:
        return self.is_visible(*self.EMPTY_ORDERS, timeout=3)
