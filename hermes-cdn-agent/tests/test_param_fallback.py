#!/usr/bin/env python
"""测试参数回退钩子"""

import pytest
from hooks.param_fallback import extract_params_from_input


def test_extract_city():
    """测试城市提取"""
    result = extract_params_from_input(
        "北京今天天气怎么样",
        ["city"],
        {"city": {"type": "string", "description": "城市"}}
    )
    assert result["city"] == "北京"


def test_extract_date():
    """测试日期提取"""
    result = extract_params_from_input(
        "明天上海天气",
        ["city", "date"],
        {
            "city": {"type": "string", "description": "城市"},
            "date": {"type": "string", "description": "日期"}
        }
    )
    assert result["city"] == "上海"
    assert result["date"] == "明天"


def test_extract_route():
    """测试路线提取"""
    result = extract_params_from_input(
        "从北京到上海的路线",
        ["from", "to"],
        {
            "from": {"type": "string", "description": "起点"},
            "to": {"type": "string", "description": "终点"}
        }
    )
    assert result["from"] == "北京"
    assert result["to"] == "上海"


def test_extract_node():
    """测试节点提取"""
    result = extract_params_from_input(
        "节点cdn-bj-01的延迟情况",
        ["node"],
        {"node": {"type": "string", "description": "CDN节点"}}
    )
    assert result["node"] == "cdn-bj-01"


def test_extract_ip():
    """测试IP提取"""
    result = extract_params_from_input(
        "192.168.1.1这个节点的状态",
        ["node"],
        {"node": {"type": "string", "description": "节点"}}
    )
    assert result["node"] == "192.168.1.1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
