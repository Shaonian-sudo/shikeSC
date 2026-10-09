# -*- coding: utf-8 -*-
"""页面对象基类：统一元素查找（含自愈）、显式等待、点击、输入、截图。"""
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import StaleElementReferenceException

from config.settings import EXPLICIT_WAIT, SCREENSHOT_DIR
from core.logger import log
from core.self_healing import SelfHealing


class BasePage:
    """所有页面对象的基类，封装 WebDriver 常用操作。"""

    def __init__(self, driver, healing: SelfHealing | None = None):
        self.driver = driver
        self.healing = healing or SelfHealing(driver)
        self.wait = WebDriverWait(driver, EXPLICIT_WAIT, poll_frequency=0.5)

    # ---------------- 定位 ----------------
    def find(self, by: By = By.CSS_SELECTOR, value: str = "", timeout: float = EXPLICIT_WAIT):
        """查找元素：常规显式等待 + 自愈兜底。"""
        try:
            return self.wait.until(ec.presence_of_element_located((by, value)))
        except Exception:
            return self.healing.find(by, value, timeout)

    def find_all(self, by: By, value: str):
        return self.driver.find_elements(by, value)

    # ---------------- 常用操作 ----------------
    def open(self, url: str, expect: str = "", retries: int = 2):
        """打开页面，并校验 URL 到达目标路径；未到达则重试（缓解浏览器导航竞态）。"""
        for i in range(retries + 1):
            self.driver.get(url)
            if not expect:
                return
            try:
                WebDriverWait(self.driver, 8).until(
                    lambda d: expect in d.current_url)
                return
            except Exception:
                log.warning("导航校验未通过(%s), 重试 %d/%d", expect, i + 1, retries)
        raise AssertionError(f"打开页面后 URL 未到达 {expect}：当前 {self.driver.current_url}")

    def wait_for_url(self, keyword: str, timeout: float = EXPLICIT_WAIT):
        """等待 URL 包含指定关键字。"""
        WebDriverWait(self.driver, timeout).until(
            lambda d: keyword in d.current_url)

    def click(self, by: By, value: str, retries: int = 3):
        """点击元素；页面刷新导致的元素过期自动重试。"""
        for _ in range(retries):
            try:
                el = self.find(by, value)
                self.wait.until(ec.element_to_be_clickable((by, value)))
                el.click()
                return
            except StaleElementReferenceException:
                continue
        raise StaleElementReferenceException(f"点击失败（元素持续过期）: {by}={value}")

    def input_text(self, by: By, value: str, text: str):
        el = self.find(by, value)
        el.clear()
        el.send_keys(text)

    def get_text(self, by: By, value: str) -> str:
        return self.find(by, value).text.strip()

    def is_visible(self, by: By, value: str, timeout: float = 5.0) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                ec.visibility_of_element_located((by, value)))
            return True
        except Exception:
            return False

    # ---------------- 截图 ----------------
    def screenshot(self, name: str = "") -> str:
        fname = name or f"shot_{datetime.now().strftime('%H%M%S_%f')}"
        path = SCREENSHOT_DIR / f"{fname}.png"
        self.driver.save_screenshot(str(path))
        log.info("截图已保存: %s", path)
        return str(path)

    # ---------------- 页面状态 ----------------
    def page_title(self) -> str:
        return self.driver.title

    def current_url(self) -> str:
        return self.driver.current_url
