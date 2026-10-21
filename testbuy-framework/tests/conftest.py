# -*- coding: utf-8 -*-
"""pytest fixtures：浏览器驱动、基地址、失败截图、自愈句柄、接口会话。"""
import time

import pytest
import requests

from config.settings import BASE_URL
from core.driver import create_driver
from core.logger import log
from core.self_healing import SelfHealing


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture()
def driver():
    """每个用例独立浏览器，隔离状态；失败自动截图。"""
    drv = create_driver()
    healing = SelfHealing(drv)
    drv._testbuy_healing = healing
    yield drv
    try:
        drv.quit()
    except Exception:
        pass


@pytest.fixture()
def healing(driver) -> SelfHealing:
    return driver._testbuy_healing


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = getattr(item, "funcargs", {}).get("driver")
        if drv is not None:
            try:
                from core.base_page import BasePage
                path = BasePage(drv).screenshot()
                log.error("用例 %s 失败，截图: %s", item.name, path)
            except Exception as e:
                log.warning("失败截图失败: %s", e)


# ---------------- 接口自动化 fixtures（requests 直调被测系统 HTTP 接口） ----------------

@pytest.fixture(scope="session")
def api_base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def api_anon(api_base_url):
    """未登录的裸会话（无 cookie），用于商品浏览 / 注册 / 权限校验场景。"""
    s = requests.Session()
    s.headers["User-Agent"] = "testbuy-api-tests/1.0"
    yield s
    s.close()


@pytest.fixture(scope="session")
def api_user(api_base_url):
    """注册一个独立接口测试用户并完成登录，返回带登录态的会话。

    使用自建会话（不复用 api_anon），避免登录态污染权限校验用例；
    只在接口测试内创建订单，不影响 UI 用例使用的 buyer 数据。
    """
    s = requests.Session()
    s.headers["User-Agent"] = "testbuy-api-tests/1.0"
    username = f"apitest_{int(time.time())}"
    password = "ApiTest@123"

    r = s.post(
        f"{api_base_url}/register",
        data={"username": username, "password": password,
              "email": f"{username}@testbuy.local"},
        allow_redirects=False,
    )
    assert r.status_code == 302, "接口注册应重定向到登录页"

    r = s.post(
        f"{api_base_url}/login",
        data={"username": username, "password": password},
        allow_redirects=False,
    )
    assert r.status_code == 302, "接口登录应重定向到首页"

    return {"username": username, "password": password, "session": s}
