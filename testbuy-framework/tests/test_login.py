# -*- coding: utf-8 -*-
"""登录模块测试：数据驱动 + 注册新用户流程。"""
import pytest

from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.index_page import IndexPage
from utils.data_loader import load_users


@pytest.mark.regression
@pytest.mark.parametrize("case", load_users(),
                         ids=lambda c: c["scenario"])
def test_login_cases(driver, base_url, case):
    """数据驱动登录用例：成功跳转首页，失败提示错误。"""
    page = LoginPage(driver)
    page.open_login(base_url)
    page.login(case["username"], case["password"])

    if case["expect"] == "success":
        index = IndexPage(driver)
        assert index.is_visible(*(IndexPage.HERO_TITLE)), "登录成功但未进入首页"
    else:
        assert page.has_error(), "非法登录未给出错误提示"
        assert page.current_url().endswith("/login"), "登录失败后未停留在登录页"


@pytest.mark.smoke
def test_register_and_login(driver, base_url):
    """注册新用户并成功登录。"""
    import time
    username = f"tester_{int(time.time())}"
    register = RegisterPage(driver)
    register.open_register(base_url)
    register.register(username, "Passw0rd!", "auto@testbuy.local")
    assert register.has_success_flash(), "注册后未出现成功提示"

    login = LoginPage(driver)
    login.open_login(base_url)
    login.login(username, "Passw0rd!")
    index = IndexPage(driver)
    assert index.is_visible(*(IndexPage.HERO_TITLE)), "新用户注册后无法登录"
