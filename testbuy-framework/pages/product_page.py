# -*- coding: utf-8 -*-
"""商品详情页页面对象。"""
from selenium.webdriver.common.by import By

from core.base_page import BasePage


class ProductPage(BasePage):
    NAME = (By.CSS_SELECTOR, "[data-testid='product-name']")
    PRICE = (By.CSS_SELECTOR, "[data-testid='product-price']")
    STOCK = (By.CSS_SELECTOR, "[data-testid='product-stock']")
    QUANTITY = (By.CSS_SELECTOR, "[data-testid='buy-quantity']")
    ADD_TO_CART = (By.CSS_SELECTOR, "[data-testid='add-to-cart']")
    FLASH = (By.CSS_SELECTOR, "[data-testid='flash-message']")

    def open_product(self, base_url: str, pid: int):
        self.open(f"{base_url}/product/{pid}", expect=f"/product/{pid}")
        return self

    def name(self) -> str:
        return self.get_text(*self.NAME)

    def price(self) -> str:
        return self.get_text(*self.PRICE)

    def stock(self) -> str:
        return self.get_text(*self.STOCK)

    def add_to_cart(self, quantity: int = 1):
        self.input_text(*self.QUANTITY, str(quantity))
        self.click(*self.ADD_TO_CART)
        # 等待加购完成的 flash 提示，确保 POST 已落地、购物车已写入
        try:
            self.wait.until(lambda d: self.is_visible(*self.FLASH, timeout=0.5))
        except Exception:
            pass

    def get_flash_text(self) -> str:
        return self.get_text(*self.FLASH)
