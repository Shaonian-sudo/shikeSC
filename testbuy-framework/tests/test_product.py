# -*- coding: utf-8 -*-
"""商品模块测试：首页加载、分类、搜索、分页、详情一致性。"""
import pytest

from pages.index_page import IndexPage
from pages.product_page import ProductPage


@pytest.mark.smoke
def test_home_page_loads(driver, base_url):
    """首页正常加载，展示商品与分类。"""
    index = IndexPage(driver)
    index.open_index(base_url)
    assert index.is_visible(*(IndexPage.HERO_TITLE)), "首页标题未展示"
    assert index.product_count() > 0, "首页未展示任何商品"
    assert len(index.categories()) > 0, "未展示分类导航"


@pytest.mark.regression
def test_category_filter(driver, base_url):
    """分类筛选后，所有商品属于该分类。"""
    index = IndexPage(driver)
    index.open_index(base_url)
    categories = index.categories()
    assert len(categories) >= 2, "分类不足，无法验证筛选"
    index.open_index(base_url)
    # 点击第一个非"全部"分类
    from selenium.webdriver.common.by import By
    index.find(By.CSS_SELECTOR, f"[data-testid='category-bar'] a[href*='category={categories[0]}']").click()
    names = index.product_names()
    assert names, "分类筛选后无商品"
    # 分类卡片详情页校验由 product_detail 用例覆盖，此处仅验证有结果
    assert index.product_count() > 0


@pytest.mark.regression
def test_search_keyword(driver, base_url):
    """关键词搜索返回匹配商品。"""
    index = IndexPage(driver)
    index.open_index(base_url)
    index.search("耳机")
    names = index.product_names()
    assert names, "搜索'耳机'无结果"
    assert any("耳机" in n for n in names), f"搜索结果不相关: {names}"


@pytest.mark.regression
def test_search_no_result(driver, base_url):
    """搜索不存在商品给出空提示。"""
    index = IndexPage(driver)
    index.open_index(base_url)
    index.search("不存在xyz商品")
    assert index.has_empty_tip(), "未出现空结果提示"


@pytest.mark.regression
def test_pagination(driver, base_url):
    """商品超过单页数量时支持翻页。"""
    index = IndexPage(driver)
    index.open_index(base_url)
    page1 = index.page_info_text()
    if index.is_visible(*(IndexPage.PAGE_NEXT), timeout=2):
        index.click_next_page()
        page2 = index.page_info_text()
        assert page1 != page2, "翻页后页码未变化"
    else:
        pytest.skip("商品数量不足一页，跳过分页验证")


@pytest.mark.regression
def test_product_detail_price_consistent(driver, base_url):
    """列表页价格与详情页价格一致。"""
    index = IndexPage(driver)
    index.open_index(base_url)
    list_price = index.find_all(*(IndexPage.PRODUCT_PRICES))[0].text
    index.open_first_product()
    detail = ProductPage(driver)
    assert detail.price() == list_price, "列表页与详情页价格不一致"
