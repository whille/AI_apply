#!/usr/bin/env python
"""
Hermes CDN Agent 入口

基于 Hermes Agent 的 CDN 调度智能助手

使用方式：
1.完整模式（需要 Hermes Agent）：
   python main.py --hermes

2. 简化模式（独立运行）：
   python main.py
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def create_simple_agent():
    """创建简化版 Agent（不依赖 Hermes）"""

    class SimpleAgent:
        """简化版 Agent，用于测试和独立运行"""

        def __init__(self):
            self.tools = {}

        def register_tool(self, schema: dict, handler):
            """注册工具"""
            name = schema.get("function", {}).get("name", "unknown")
            self.tools[name] = {"schema": schema, "handler": handler}

        async def chat(self, message: str) -> str:
            """处理消息（简化版，直接返回帮助信息）"""
            return f"""收到: {message}

当前已注册工具: {list(self.tools.keys())}

提示: 使用 --hermes 参数启动完整模式连接 LLM"""

    return SimpleAgent()


def create_hermes_agent():
    """创建 Hermes Agent（需要安装 Hermes）"""
    try:
        # 尝试导入 Hermes
        sys.path.insert(0, os.path.expanduser("~/tmp/hermes-agent"))
        from run_agent import AIAgent

        # 创建 Agent
        agent = AIAgent(
            model=os.getenv("HERMES_MODEL", "claude-sonnet-4-6"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

        # 注册 CDN 工具
        from tools.cdn_tools import register_cdn_tools
        tool_count = register_cdn_tools(agent)
        print(f"已注册 {tool_count} 个 CDN 工具")

        return agent

    except ImportError as e:
        print(f"错误: 无法导入 Hermes Agent - {e}")
        print("请先安装 Hermes Agent:")
        print("  cd /tmp && git clone https://github.com/NousResearch/hermes-agent.git")
        print("  cd hermes-agent && pip install -e .")
        return None


def get_system_prompt() -> str:
    """获取系统提示词"""
    return """你是 CDN 调度智能助手，帮助运维工程师：

1. 监控 CDN 节点状态
2. 分析异常根因
3. 提供优化建议
4. 生成配置变更

你有以下工具可用：
- get_metrics: 获取节点监控数据
- get_anomalies: 获取异常列表
- analyze_root_cause: 分析问题根因
- create_config_change: 创建配置变更 PR

回答时请：
- 先确认问题范围
- 收集相关数据
- 分析根因
- 给出具体建议
"""


async def chat_loop(agent):
    """交互式聊天循环"""
    print("\n=== Hermes CDN Agent ===")
    print("输入问题，或输入 'quit' 退出\n")

    while True:
        try:
            user_input = input("用户: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ('quit', 'exit', 'q'):
                print("再见！")
                break

            # 调用 Agent
            if hasattr(agent, 'chat'):
                response = await agent.chat(user_input)
            else:
                # Hermes Agent 使用不同的API
                response = f"[Hermes模式] 收到: {user_input}"

            print(f"\n助手: {response}\n")

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}\n")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="Hermes CDN Agent")
    parser.add_argument("--hermes", action="store_true", help="使用 Hermes Agent 完整模式")
    args = parser.parse_args()

    if args.hermes:
        agent = create_hermes_agent()
    else:
        print("使用简化模式（--hermes 启动完整模式）")
        agent = create_simple_agent()# 注册 CDN 工具到简化 Agent
        from tools.cdn_tools import register_cdn_tools
        register_cdn_tools(agent)

    if not agent:
        sys.exit(1)

    asyncio.run(chat_loop(agent))


if __name__ == "__main__":
    main()
