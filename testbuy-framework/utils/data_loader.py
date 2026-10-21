# -*- coding: utf-8 -*-
"""JSON 测试数据加载工具。"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "config" / "test_data"


def load_json(name: str) -> list:
    """加载 config/test_data 下的 JSON 文件（支持 .json / .json5 宽松解析）。"""
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"测试数据文件不存在: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_users() -> list:
    return load_json("users.json")


def load_checkout_cases() -> list:
    return load_json("checkout.json")
