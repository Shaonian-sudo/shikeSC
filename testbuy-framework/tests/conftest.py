# -*- coding: utf-8 -*-
"""pytest fixtures：浏览器驱动、基地址、失败截图、自愈句柄。"""
import pytest

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
