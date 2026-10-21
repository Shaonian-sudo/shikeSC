# -*- coding: utf-8 -*-
"""结算页页面对象。"""
from selenium.webdriver.common.by import By

from core.base_page import BasePage


class CheckoutPage(BasePage):
    RECEIVER = (By.CSS_SELECTOR, "[data-testid='checkout-receiver']")
    PHONE = (By.CSS_SELECTOR, "[data-testid='checkout-phone']")
    ADDRESS = (By.CSS_SELECTOR, "[data-testid='checkout-address']")
    SUBMIT = (By.CSS_SELECTOR, "[data-testid='submit-order']")
    TOTAL = (By.CSS_SELECTOR, "[data-testid='checkout-total']")
    FLASH = (By.CSS_SELECTOR, "[data-testid='flash-message']")

    def open_checkout(self, base_url: str):
        self.open(f"{base_url}/checkout", expect="/checkout")
        return self

    def fill(self, receiver: str, phone: str, address: str):
        self.input_text(*self.RECEIVER, receiver)
        self.input_text(*self.PHONE, phone)
        self.input_text(*self.ADDRESS, address)

    def submit(self):
        self.click(*self.SUBMIT)

    def total_text(self) -> str:
        return self.get_text(*self.TOTAL)

    def get_flash_text(self) -> str:
        return self.get_text(*self.FLASH)

    def has_error(self) -> bool:
        return self.is_visible(*self.FLASH, timeout=3)
