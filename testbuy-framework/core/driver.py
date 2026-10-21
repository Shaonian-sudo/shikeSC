# -*- coding: utf-8 -*-
"""浏览器驱动管理：本机 Chrome/Firefox/Edge，支持无头模式。

优先使用项目 drivers/ 目录下的本地浏览器驱动（离线可用），
未找到时回退 Selenium Manager 自动下载。
"""
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from config.settings import BROWSER, HEADLESS, IMPLICIT_WAIT, ROOT
from core.logger import log

DRIVERS_DIR = ROOT / "drivers"
LOCAL_DRIVERS = {
    "chrome": DRIVERS_DIR / "chromedriver.exe",
    "firefox": DRIVERS_DIR / "geckodriver.exe",
    "edge": DRIVERS_DIR / "msedgedriver.exe",
}


def _service(browser: str):
    path = LOCAL_DRIVERS.get(browser)
    if path and path.is_file():
        log.info("使用本地驱动: %s", path)
        return ChromeService(str(path)) if browser == "chrome" else None
    log.info("本地驱动不存在，回退 Selenium Manager 自动下载")
    return None


def create_driver(browser: str = BROWSER, headless: bool = HEADLESS):
    if browser not in LOCAL_DRIVERS:
        raise ValueError(f"不支持的浏览器: {browser}，可选 {list(LOCAL_DRIVERS)}")

    cls, opts_cls = _browser_entry(browser)
    opts = opts_cls()
    opts.add_argument("--window-size=1440,900")
    opts.add_argument("--no-first-run")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-dev-shm-usage")
    if headless:
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")

    kwargs = {"options": opts}
    svc = _service(browser)
    if svc is not None:
        kwargs["service"] = svc

    driver = cls(**kwargs)
    driver.implicitly_wait(IMPLICIT_WAIT)
    driver.set_page_load_timeout(30)
    log.info("浏览器已启动: %s headless=%s", browser, headless)
    return driver


def _browser_entry(browser: str):
    return {
        "chrome": (webdriver.Chrome, ChromeOptions),
        "firefox": (webdriver.Firefox, FirefoxOptions),
        "edge": (webdriver.Edge, EdgeOptions),
    }[browser]
