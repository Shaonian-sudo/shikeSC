# -*- coding: utf-8 -*-
"""全局配置：被测系统地址、浏览器、超时、目录等。"""
import os
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent

# 被测系统（试客商城）
BASE_URL = os.environ.get("TESTBUY_URL", "http://127.0.0.1:5000")

# 浏览器配置
BROWSER = os.environ.get("TESTBUY_BROWSER", "chrome")   # chrome / firefox / edge
HEADLESS = os.environ.get("TESTBUY_HEADLESS", "0") == "1"

# 等待超时（秒）
IMPLICIT_WAIT = 5
EXPLICIT_WAIT = 10
POLL_FREQUENCY = 0.5

# 目录
SCREENSHOT_DIR = ROOT / "screenshots"
LOG_DIR = ROOT / "logs"
REPORT_DIR = ROOT / "reports"

# 自愈定位开关（亮点模块）
SELF_HEALING_ENABLED = os.environ.get("TESTBUY_SELF_HEAL", "1") == "1"
SELF_HEALING_LLM = os.environ.get("TESTBUY_SELF_HEAL_LLM", "0") == "1"
LLM_API_URL = os.environ.get("LLM_API_URL", "")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "doubao-seed")

for d in (SCREENSHOT_DIR, LOG_DIR, REPORT_DIR):
    d.mkdir(parents=True, exist_ok=True)
