# -*- coding: utf-8 -*-
"""登录页页面对象。"""
from selenium.webdriver.common.by import By

from core.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = (By.CSS_SELECTOR, "[data-testid='login-username']")
    PASSWORD = (By.CSS_SELECTOR, "[data-testid='login-password']")
    SUBMIT = (By.CSS_SELECTOR, "[data-testid='login-submit']")
    FLASH = (By.CSS_SELECTOR, "[data-testid='flash-message']")
    NAV_LOGIN = (By.CSS_SELECTOR, "[data-testid='nav-login']")
    GO_REGISTER = (By.CSS_SELECTOR, "[data-testid='go-register']")

    def open_login(self, base_url: str):
        self.open(f"{base_url}/login", expect="/login")
        return self

    def login(self, username: str, password: str):
        """执行登录操作，返回是否出现错误提示。"""
        self.input_text(*self.USERNAME, username)
        self.input_text(*self.PASSWORD, password)
        self.click(*self.SUBMIT)
        # 等待登录结果落地（跳转首页或出现错误提示），避免后续操作竞态
        try:
            self.wait.until(lambda d: "/login" not in d.current_url
                            or self.is_visible(*self.FLASH, timeout=1))
        except Exception:
            pass

    def get_flash_text(self) -> str:
        return self.get_text(*self.FLASH)

    def has_error(self) -> bool:
        return self.is_visible(*self.FLASH)

    def go_register(self):
        self.click(*self.GO_REGISTER)
