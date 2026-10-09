# -*- coding: utf-8 -*-
"""日志模块：控制台 + 文件双输出。"""
import logging
from datetime import datetime

from config.settings import LOG_DIR


def get_logger(name: str = "testbuy") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    file_handler = logging.FileHandler(
        LOG_DIR / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger


log = get_logger()
