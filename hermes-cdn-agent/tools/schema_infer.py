# -*- coding: utf-8 -*-
"""
Infer OPENAI_SCHEMA from run() signature. Cursor-style: no hand-written schema.
Requires Python 3.9+.
"""

import inspect
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
    get_args,
    get_origin,
)


def _py_type_to_json_type(hint: Any) -> str:
    """Map Python type hint to JSON schema type string."""
    origin = get_origin(hint)
    args = get_args(hint)

    if origin is type(None) or hint is type(None):
        return "string"  # fallback

    if hint is None or (origin is None and hint is type(None)):
        return "string"

    # Optional[X] = Union[X, None]
    if origin is Union and type(None) in args:
        args = [a for a in args if a is not type(None)]
        if len(args) == 1:
            return _py_type_to_json_type(args[0])
        return _py_type_to_json_type(args[0]) if args else "string"

    if origin is Union and args:
        return _py_type_to_json_type(args[0])

    # Concrete types
    if hint is str or (origin is None and inspect.isclass(hint) and hint is str):
        return "string"
    if hint is int:
        return "integer"
    if hint is float:
        return "number"
    if hint is bool:
        return "boolean"
    if inspect.isclass(hint):
        if issubclass(hint, str):
            return "string"
        if issubclass(hint, int):
            return "integer"
        if issubclass(hint, float):
            return "number"
        if issubclass(hint, bool):
            return "boolean"

    return "string"  # default


def infer_schema(
    run_fn: Callable,
    tool_name: str,
    tool_description: str,
    required: Optional[List[str]] = None,
    param_descriptions: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Build OPENAI_SCHEMA from run() signature and optional overrides.

    Args:
        run_fn: The run(*, ...) function.
        tool_name: Tool name (e.g. "pdf_ocr_to_markdown").
        tool_description: Tool description for LLM.
        required: List of required param names. If None, inferred from signature
                  (params with no default or default=inspect.Parameter.empty).
        param_descriptions: Optional {param_name: description} overrides.

    Returns:
        OPENAI_SCHEMA dict suitable for ToolManager/AgentScope.
    """
    sig = inspect.signature(run_fn)
    hints = {}
    try:
        from typing import get_type_hints as typing_get_type_hints
        hints = typing_get_type_hints(run_fn)
    except Exception:
        pass

    properties = {}
    inferred_required = []

    for name, param in sig.parameters.items():
        if name in ("kwargs", "args") or param.kind == param.VAR_KEYWORD or param.kind == param.VAR_POSITIONAL:
            continue

        hint = hints.get(name, str)
        json_type = _py_type_to_json_type(hint)

        prop = {"type": json_type}
        if param_descriptions and name in param_descriptions:
            prop["description"] = param_descriptions[name]
        else:
            # Default description from param name
            prop["description"] = name.replace("_", " ")

        default = param.default
        if default is not inspect.Parameter.empty:
            if default is not None and not (isinstance(default, str) and default == ""):
                prop["default"] = default

        properties[name] = prop

    if required is not None:
        required_list = [p for p in required if p in properties]
    else:
        required_list = [
            name for name, param in sig.parameters.items()
            if name not in ("kwargs", "args")
            and param.kind not in (param.VAR_KEYWORD, param.VAR_POSITIONAL)
            and param.default is inspect.Parameter.empty
        ]

    return {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": tool_description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required_list,
            },
        },
    }
