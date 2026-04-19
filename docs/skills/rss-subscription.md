# RSS 订阅方案

> RSS MCP 及其他订阅方案调研结果

---

## 结论

**目前无现成 RSS MCP Server，建议自研轻量级 MCP。**

| 方案 | 可行性 | 说明 |
|------|--------|------|
| 现有 RSS MCP | ❌ 无 | 官方/社区均无 RSS MCP |
| 自研 MCP Server | ✅ 推荐 | Python feedparser + FastMCP，工作量约 1-2 天 |
| CLI Skill | ✅ 备选 | 封装 feedparser，灵活但需手动调用 |

---

## 调研结果

### 1. 官方 MCP Servers

参考 servers 仓库：[modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)

**Reference Servers（无 RSS）**：
- Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time

**Archived Servers（无 RSS）**：
- AWS KB Retrieval, Brave Search, EverArt, GitHub, GitLab, Google Drive, Google Maps, PostgreSQL, Puppeteer, Redis, Sentry, Slack, SQLite

**结论**：官方无 RSS 相关实现

### 2. 社区 MCP Servers

搜索 GitHub 未发现专门的 RSS/Feed MCP Server 实现。

---

## 技术选型

### RSS 解析库

**Python feedparser** - 成熟稳定，推荐使用

```bash
pip install feedparser
```

| 特性 | 说明 |
|------|------|
| 协议支持 | RSS 0.9x, 1.0, 2.0, Atom 0.3, 1.0, CDF |
| 解析方式 | 自动检测格式 |
| 输出格式 | 统一的字典结构 |
| 维护状态 | 活跃维护 |

### MCP 框架

| 框架 | 语言 | 推荐度 |
|------|------|--------|
| FastMCP | Python | ⭐⭐⭐⭐⭐ 简洁易用 |
| mcp (官方 SDK) | Python | ⭐⭐⭐⭐ 标准 |
| @modelcontextprotocol/sdk | TypeScript | ⭐⭐⭐⭐ 前端友好 |

---

## 自研 MCP 工作量评估

### 核心功能设计

```
RSS MCP Server
├── Tools
│   ├── add_feed(url, name?)      # 添加订阅
│   ├── remove_feed(name)          # 删除订阅
│   ├── list_feeds()               # 列出订阅
│   ├── get_entries(name, limit?)  # 获取文章
│   └── search_entries(query)      # 搜索文章
├── Resources
│   └── feeds://{name}/entries     # 订阅源文章列表
└── Prompts
    └── summarize_feed             # 总结订阅内容
```

### 工作量估算

| 功能模块 | 工作量 | 说明 |
|----------|--------|------|
| 基础 RSS 读取 | 2-4 小时 | feedparser 解析 |
| 订阅管理 | 2-3 小时 | 增删查改 + 持久化 |
| MCP 接口封装 | 2-3 小时 | Tools + Resources |
| 定时更新 + 缓存 | 2-3 小时 | 可选 |
| 测试 + 文档 | 2-3 小时 | |
| **总计** | **1-2 天** | |

---

## 实现示例

### 基础 MCP Server（FastMCP）

```python
# rss_mcp_server.py
from fastmcp import FastMCP
import feedparser
from typing import Optional

mcp = FastMCP("rss-server")

# 内存存储（生产环境可用 SQLite）
feeds: dict[str, str] = {}

@mcp.tool
def add_feed(url: str, name: Optional[str] = None) -> str:
    """添加 RSS 订阅源"""
    feed = feedparser.parse(url)
    if feed.bozo:  # 解析错误
        return f"解析失败: {feed.bozo_exception}"

    feed_name = name or feed.feed.get("title", "unnamed")
    feeds[feed_name] = url
    return f"已添加: {feed_name} ({len(feed.entries)} 篇文章)"

@mcp.tool
def list_feeds() -> list[str]:
    """列出所有订阅"""
    return list(feeds.keys())

@mcp.tool
def get_entries(name: str, limit: int = 10) -> list[dict]:
    """获取订阅的最新文章"""
    if name not in feeds:
        return [{"error": f"未找到订阅: {name}"}]

    feed = feedparser.parse(feeds[name])
    entries = []
    for entry in feed.entries[:limit]:
        entries.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", "")[:200],
            "published": entry.get("published", ""),
        })
    return entries

if __name__ == "__main__":
    mcp.run()
```

### 运行方式

```bash
# 安装 FastMCP
pip install fastmcp

# 运行 Server
fastmcp run rss_mcp_server.py

# 或使用 npx inspector 调试
npx @modelcontextprotocol/inspector python rss_mcp_server.py
```

---

## 配置到 Claude Desktop

```json
{
  "mcpServers": {
    "rss": {
      "command": "python",
      "args": ["/path/to/rss_mcp_server.py"]
    }
  }
}
```

---

## 替代方案

### 方案一：CLI Skill（轻量）

```bash
# rss-reader.py
import feedparser
import sys

url = sys.argv[1]
feed = feedparser.parse(url)

for entry in feed.entries[:10]:
    print(f"## {entry.title}")
    print(f"链接: {entry.link}")
    print(f"摘要: {entry.summary[:100]}...")
    print()
```

调用方式：
```bash
python rss-reader.py "https://example.com/feed.xml"
```

### 方案二：使用现有 Fetch MCP

理论上可用 Fetch MCP 获取 RSS XML，但需要额外解析，不推荐。

---

## 推荐方案

| 场景 | 推荐方案 |
|------|----------|
| 需要自动订阅管理 | 自研 MCP Server |
| 偶尔查看 RSS | CLI Skill |
| 快速验证可行性 | feedparser 直接使用 |

**最终建议**：自研轻量级 RSS MCP Server，核心功能约 200 行 Python。

---

## 参考资源

- [feedparser 文档](https://feedparser.readthedocs.io/)
- [FastMCP GitHub](https://github.com/pydantic/fastmcp)
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Servers 仓库](https://github.com/modelcontextprotocol/servers)

---

*更新时间：2026-04-19*
