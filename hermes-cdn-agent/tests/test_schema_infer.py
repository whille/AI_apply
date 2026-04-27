#!/usr/bin/env python
"""测试 schema_infer"""

import pytest
from tools.schema_infer import infer_schema


def test_basic_function():
    """测试基本函数推断"""

    def run(*, city: str, date: str = None) -> str:
        """获取天气"""
        return f"{city} 天气"

    schema = infer_schema(run, "weather", "获取天气")

    # OpenAI Tools 格式
    assert schema["type"] == "function"
    func = schema["function"]
    assert func["name"] == "weather"
    assert func["description"] == "获取天气"
    assert "city" in func["parameters"]["properties"]
    assert "date" in func["parameters"]["properties"]
    assert func["parameters"]["required"] == ["city"]


def test_multiple_required():
    """测试多必填参数"""

    def run(*, from_city: str, to_city: str, date: str = None) -> str:
        """查询路线"""
        return f"{from_city} -> {to_city}"

    schema = infer_schema(run, "route", "查询路线")

    func = schema["function"]
    assert set(func["parameters"]["required"]) == {"from_city", "to_city"}


def test_type_inference():
    """测试类型推断"""

    def run(*, name: str, count: int, ratio: float, enabled: bool) -> str:
        """测试类型"""
        return "ok"

    schema = infer_schema(run, "test", "测试类型")

    props = schema["function"]["parameters"]["properties"]
    assert props["name"]["type"] == "string"
    assert props["count"]["type"] == "integer"
    assert props["ratio"]["type"] == "number"
    assert props["enabled"]["type"] == "boolean"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
