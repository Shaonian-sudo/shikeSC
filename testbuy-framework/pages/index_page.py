# -*- coding: utf-8 -*-
"""首页（商品列表）页面对象。"""
from selenium.webdriver.common.by import By

from core.base_page import BasePage


class IndexPage(BasePage):
    SEARCH_INPUT = (By.CSS_SELECTOR, "[data-testid='search-input']")
    SEARCH_BTN = (By.CSS_SELECTOR, "[data-testid='search-btn']")
    HERO_TITLE = (By.CSS_SELECTOR, "[data-testid='hero-title']")
    PRODUCT_CARDS = (By.CSS_SELECTOR, "[data-testid='product-card']")
    PRODUCT_NAMES = (By.CSS_SELECTOR, "[data-testid='product-name']")
    PRODUCT_PRICES = (By.CSS_SELECTOR, "[data-testid='product-price']")
    EMPTY_TIP = (By.CSS_SELECTOR, "[data-testid='empty-tip']")
    PAGE_INFO = (By.CSS_SELECTOR, "[data-testid='page-info']")
    PAGE_NEXT = (By.CSS_SELECTOR, "[data-testid='page-next']")
    CATEGORY_BAR = (By.CSS_SELECTOR, "[data-testid='category-bar']")

    def open_index(self, base_url: str):
        self.open(base_url, expect="/")
        return self

    def search(self, keyword: str):
        self.input_text(*self.SEARCH_INPUT, keyword)
        self.click(*self.SEARCH_BTN)
        # 等待搜索导航真正完成：URL 携带关键词且 DOM 就绪，避免读取旧页面元素
        try:
            from urllib.parse import quote
            self.wait.until(
                lambda d: quote(keyword, safe="") in d.current_url
                and d.execute_script("return document.readyState") == "complete")
        except Exception:
            pass
        # 再等结果卡或空提示渲染完成
        try:
            self.wait.until(lambda d: ec.presence_of_element_located(self.PRODUCT_CARDS)(d)
                            or ec.presence_of_element_located(self.EMPTY_TIP)(d))
        except Exception:
            pass

    def product_count(self) -> int:
        return len(self.find_all(*self.PRODUCT_CARDS))

    def product_names(self) -> list[str]:
        return [el.text.strip() for el in self.find_all(*self.PRODUCT_NAMES)]

    def first_product_name(self) -> str:
        return self.product_names()[0]

    def open_first_product(self):
        self.find_all(*self.PRODUCT_CARDS)[0].click()
        self.wait_for_url("/product/")

    def has_empty_tip(self) -> bool:
        return self.is_visible(*self.EMPTY_TIP, timeout=3)

    def page_info_text(self) -> str:
        return self.get_text(*self.PAGE_INFO)

    def click_next_page(self):
        self.click(*self.PAGE_NEXT)

    def categories(self) -> list[str]:
        bar = self.find(*self.CATEGORY_BAR)
        return [el.text.strip() for el in bar.find_elements(By.TAG_NAME, "a")]
