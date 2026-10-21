# -*- coding: utf-8 -*-
"""自愈定位模块（答辩亮点）。

问题背景：页面元素改版（属性/层级变化）导致定位器失效，用例大面积失败，维护成本高。
方案：混合自愈策略，两级修复——
  1) 规则级（默认开启）：按属性优先级回退链在 DOM 中重新匹配候选元素，
     优先 data-testid，依次回退 id / name / class / 可见文本；
  2) LLM 级（可选开启）：将页面元素快照交给大模型，语义化推理出新的定位器。

所有自愈事件会被记录，供测试报告统计"自愈率"，量化框架的维护成本收益。
"""
import json
import re
import time
from dataclasses import dataclass, field

import requests
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from config.settings import (SELF_HEALING_ENABLED, SELF_HEALING_LLM,
                             LLM_API_URL, LLM_API_KEY, LLM_MODEL)
from core.logger import log

# 属性回退链（优先 data-testid —— 试客商城的测试友好设计约定）
ATTRIBUTE_CHAIN = ["data-testid", "id", "name", "class", "aria-label"]


@dataclass
class HealRecord:
    """一次自愈事件记录。"""
    failed_locator: str
    healed_locator: str
    strategy: str            # rule / llm
    target_text: str = ""    # 原始意图文本（用于规则级文本匹配）
    timestamp: float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "failed_locator": self.failed_locator,
            "healed_locator": self.healed_locator,
            "strategy": self.strategy,
            "target_text": self.target_text,
        }


class SelfHealing:
    """页面元素自愈查找器。"""

    def __init__(self, driver, enabled: bool = SELF_HEALING_ENABLED,
                 use_llm: bool = SELF_HEALING_LLM):
        self.driver = driver
        self.enabled = enabled
        self.use_llm = use_llm and bool(LLM_API_URL)
        self.records: list[HealRecord] = []

    # ---------------- 对外入口 ----------------
    def find(self, by: str, value: str, timeout: float = 10.0):
        """先常规查找，失败则触发自愈；仍失败抛出 NoSuchElementException。"""
        if not self.enabled:
            return self.driver.find_element(by, value)

        try:
            element = self._try_find(by, value, timeout)
            return element
        except (NoSuchElementException, TimeoutException):
            healed = self._heal(by, value)
            if healed is not None:
                return healed
            raise NoSuchElementException(
                f"常规定位与自愈均失败: {by}={value}")

    # ---------------- 常规查找 ----------------
    def _try_find(self, by: str, value: str, timeout: float):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as ec
        wait = WebDriverWait(self.driver, timeout, poll_frequency=0.5)
        return wait.until(ec.presence_of_element_located((by, value)))

    # ---------------- 自愈 ----------------
    def _heal(self, by: str, value: str):
        if by == By.CSS_SELECTOR:
            # 提取 data-testid / id 等目标值，作为语义意图
            target = self._extract_testid(value)
        else:
            target = value

        # 1) 规则级修复
        record = self._heal_by_rule(target)
        if record:
            log.warning("[自愈-规则] %s=%s -> %s", by, value, record.healed_locator)
            self.records.append(record)
            return self.driver.find_element(*self._parse(record.healed_locator))

        # 2) LLM 级修复
        if self.use_llm:
            record = self._heal_by_llm(target)
            if record:
                log.warning("[自愈-LLM] %s=%s -> %s", by, value, record.healed_locator)
                self.records.append(record)
                return self.driver.find_element(*self._parse(record.healed_locator))

        log.error("[自愈-失败] 无法修复定位: %s=%s", by, value)
        return None

    def _heal_by_rule(self, target: str):
        """按属性回退链寻找唯一候选元素；无唯一候选则按可见文本匹配。"""
        for attr in ATTRIBUTE_CHAIN:
            candidates = self.driver.find_elements(By.CSS_SELECTOR, f"[{attr}]")
            hits = [el for el in candidates if el.get_attribute(attr) == target]
            if len(hits) == 1:
                return HealRecord(
                    failed_locator=target,
                    healed_locator=f"{attr}={target}",
                    strategy="rule",
                    target_text=target)
        # 文本回退
        texts = self.driver.find_elements(By.CSS_SELECTOR, "a,button,span,h1,h2,div")
        hits = [el for el in texts if el.text.strip() == target]
        if len(hits) == 1:
            return HealRecord(
                failed_locator=target,
                healed_locator=f"text={target}",
                strategy="rule",
                target_text=target)
        return None

    def _heal_by_llm(self, target: str):
        """LLM 语义修复：把页面元素快照交给大模型，输出新定位器。"""
        snapshot = self._dom_snapshot(target)
        prompt = (
            "你是一个UI自动化测试定位器修复专家。被测电商系统页面元素改版导致定位器失效。\n"
            f"失效的定位目标: {target}\n"
            "以下是页面关键元素快照(格式: 标签|data-testid|id|name|可见文本):\n"
            f"{snapshot}\n"
            "请找到与失效目标语义最匹配的元素，只输出一行 CSS 定位器(属性选择器)，"
            "不要任何解释。"
        )
        try:
            resp = requests.post(
                LLM_API_URL,
                headers={"Authorization": f"Bearer {LLM_API_KEY}"},
                json={
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                },
                timeout=20)
            resp.raise_for_status()
            locator = resp.json()["choices"][0]["message"]["content"].strip()
            locator = re.sub(r"^`+|`+$", "", locator).strip()
            if not locator or not self.driver.find_elements(By.CSS_SELECTOR, locator):
                return None
            return HealRecord(failed_locator=target, healed_locator=locator,
                              strategy="llm", target_text=target)
        except Exception as e:  # LLM 不可用时静默降级
            log.warning("LLM 自愈不可用: %s", e)
            return None

    # ---------------- 工具 ----------------
    def _extract_testid(self, css: str):
        m = re.search(r"\[data-testid=['\"]([^'\"]+)['\"]\]", css)
        return m.group(1) if m else css

    def _parse(self, locator: str):
        if "=" in locator and not locator.startswith("["):
            attr, _, val = locator.partition("=")
            return By.CSS_SELECTOR, f"[{attr}='{val}']"
        return By.CSS_SELECTOR, locator

    def _dom_snapshot(self, target: str, limit: int = 200):
        rows = []
        for el in self.driver.find_elements(By.CSS_SELECTOR, "input,button,a,span,h1,h2,div")[:limit]:
            tag = el.tag_name
            testid = el.get_attribute("data-testid") or ""
            eid = el.get_attribute("id") or ""
            name = el.get_attribute("name") or ""
            text = (el.text or "")[:40]
            rows.append(f"{tag}|{testid}|{eid}|{name}|{text}")
        return "\n".join(rows)

    def heal_summary(self) -> dict:
        """自愈统计：事件数、规则/LLM 占比，用于报告展示。"""
        n_rule = sum(1 for r in self.records if r.strategy == "rule")
        n_llm = sum(1 for r in self.records if r.strategy == "llm")
        return {"total": len(self.records), "rule": n_rule, "llm": n_llm,
                "records": [r.to_dict() for r in self.records]}
