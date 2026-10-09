# -*- coding: utf-8 -*-
"""注册页页面对象。"""
from selenium.webdriver.common.by import By

from core.base_page import BasePage


class RegisterPage(BasePage):
    USERNAME = (By.CSS_SELECTOR, "[data-testid='register-username']")
    PASSWORD = (By.CSS_SELECTOR, "[data-testid='register-password']")
    EMAIL = (By.CSS_SELECTOR, "[data-testid='register-email']")
    SUBMIT = (By.CSS_SELECTOR, "[data-testid='register-submit']")
    FLASH = (By.CSS_SELECTOR, "[data-testid='flash-message']")
    GO_LOGIN = (By.CSS_SELECTOR, "[data-testid='go-login']")

    def open_register(self, base_url: str):
        self.open(f"{base_url}/register", expect="/register")
        return self

    def register(self, username: str, password: str, email: str = ""):
        self.input_text(*self.USERNAME, username)
        self.input_text(*self.PASSWORD, password)
        if email:
            self.input_text(*self.EMAIL, email)
        self.click(*self.SUBMIT)

    def has_success_flash(self) -> bool:
        return self.is_visible(*self.FLASH, timeout=3) and "成功" in self.get_text(*self.FLASH)
