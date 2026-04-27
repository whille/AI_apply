#!/usr/bin/env python
"""
参数回退钩子 — 解决 LLM 空参数调用问题

当 LLM 传入空参数 {} 调用工具时，从用户输入中提取缺失参数。
"""

import re
from typing import Dict, Any, Optional

# 常用城市列表
CITIES = [
    "北京", "上海", "深圳", "广州", "杭州", "成都",
    "武汉", "南京", "苏州", "西安", "重庆", "天津"
]


def extract_params_from_input(
    user_input: str,
    missing_params: list,
    properties: dict
) -> dict:
    """
    从用户输入中提取缺失参数

    Args:
        user_input: 用户原始输入
        missing_params: 缺失的参数名列表
        properties: 工具参数 Schema

    Returns:
        提取出的参数字典
    """
    result = {}
    text = user_input or ""

    for param in missing_params:
        param_info = properties.get(param, {})
        param_type = param_info.get("type", "string")
        param_desc = param_info.get("description", "").lower()

        # 根据参数描述推断类型
        if "城市" in param_desc or param == "city":
            result[param] = _extract_city(text)
        elif "日期" in param_desc or param == "date":
            result[param] = _extract_date(text)
        elif "起点" in param_desc or param == "from":
            result[param] = _extract_location(text, "from")
        elif "终点" in param_desc or param == "to":
            result[param] = _extract_location(text, "to")
        elif "节点" in param_desc or param == "node":
            result[param] = _extract_node(text)

    return result


def _extract_city(text: str) -> Optional[str]:
    """提取城市名"""
    for city in CITIES:
        if city in text:
            return city
    return None


def _extract_date(text: str) -> Optional[str]:
    """提取日期"""
    patterns = [
        ("今天", "今天"),
        ("明天", "明天"),
        ("昨天", "昨天"),
    ]

    for keyword, value in patterns:
        if keyword in text:
            return value

    # 匹配 "X月X日"
    m = re.search(r"(\d{1,2})月(\d{1,2})日?", text)
    if m:
        return f"{m.group(1)}月{m.group(2)}日"

    # 匹配 "YYYY-MM-DD"
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return m.group(0)

    return None


def _extract_location(text: str, loc_type: str) -> Optional[str]:
    """提取地点（起点/终点）"""
    # 匹配 "从X到Y"
    m = re.search(r"从\s*([^\s到]+?)\s*到\s*([^\s的，。！？]+)", text)
    if m:
        return m.group(1) if loc_type == "from" else m.group(2)
    return None


def _extract_node(text: str) -> Optional[str]:
    """提取CDN节点名"""
    # 匹配 IP
    m = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text)
    if m:
        return m.group(1)

    # 匹配 "节点XXX" 或 "XXX节点"
    m = re.search(r"节点[：:]?\s*([^\s的，。！？]+)", text)
    if m:
        return m.group(1)

    m = re.search(r"([a-zA-Z0-9\-]+)\s*节点", text)
    if m:
        return m.group(1)

    return None


# --- Hermes 钩子类 ---

class ParamFallbackHook:
    """
    Hermes before_tool_call 钩子

    用法：
    ```python
    from hermes import HermesAgent
    from hooks.param_fallback import ParamFallbackHook

    agent = HermesAgent()
    hook = ParamFallbackHook(agent)
    agent.register_hook("before_tool_call", hook)
    ```
    """

    def __init__(self, agent):
        self.agent = agent

    async def __call__(self, tool_name: str, tool_args: dict, context: dict) -> dict:
        """钩子入口"""
        if not tool_args or tool_args == {}:
            user_input = context.get("user_input", "")
            tool_schema = self._get_tool_schema(tool_name)

            if tool_schema:
                missing = tool_schema.get("parameters", {}).get("required", [])
                properties = tool_schema.get("parameters", {}).get("properties", {})

                extracted = extract_params_from_input(user_input, missing, properties)
                if extracted:
                    tool_args.update(extracted)

        return tool_args

    def _get_tool_schema(self, tool_name: str) -> Optional[dict]:
        """获取工具 Schema"""
        # Hermes API: 获取已注册工具的 Schema
        if hasattr(self.agent, 'tools') and hasattr(self.agent.tools, 'get_schema'):
            return self.agent.tools.get_schema(tool_name)
        return None


# 便捷函数
def setup_param_fallback(agent):
    """为 Agent 设置参数回退钩子"""
    hook = ParamFallbackHook(agent)

    # 检查 Hermes 是否支持钩子注册
    if hasattr(agent, 'register_hook'):
        agent.register_hook("before_tool_call", hook)
    else:
        print("Warning: Hermes Agent does not support hooks")

    return hook
