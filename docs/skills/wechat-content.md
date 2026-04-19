# 微信公众号内容获取方案

> 调研日期：2026-04-19
> 状态：已完成调研

---

## 背景说明

微信公众号生态封闭，官方未开放文章内容获取 API。本文档调研可行的获取方案，分为自动化工具和手动方案两类。

---

## 方案对比

| 方案 | 自动化程度 | 稳定性 | 复杂度 | 推荐场景 |
|------|-----------|--------|--------|----------|
| wechat-download-api | 高 | 中 | 高 | 需要批量订阅、RSS 同步 |
| mcp-server-wechat-reader | 高 | 中 | 中 | AI Agent 集成、单篇解析 |
| 微信读书 MCP | 高 | 高 | 低 | 读书笔记、划线提取 |
| 浏览器打印 PDF | 无 | 高 | 低 | 偶尔使用、单篇保存 |
| 第三方工具导出 | 中 | 低 | 低 | 批量导出历史文章 |

---

## 方案一：wechat-download-api（推荐）

### 简介

开源的微信公众号文章获取与 RSS 订阅 API 服务。

**GitHub**: https://github.com/tmwgsicp/wechat-download-api

### 核心功能

- RSS 订阅 — 订阅任意公众号，自动拉取新文章，生成标准 RSS 2.0 源
- 文章内容获取 — 通过 URL 获取文章完整内容（标题、作者、正文、图片）
- 文章列表获取 — 获取任意公众号历史文章列表，支持分页
- 公众号搜索 — 按名称搜索公众号
- 反风控体系 — Chrome TLS 指纹模拟 + SOCKS5 代理池

### 安装部署

```bash
# Docker 部署（推荐）
git clone https://github.com/tmwgsicp/wechat-download-api.git
cd wechat-download-api
cp env.example .env
docker-compose up -d

# 或一键脚本
bash start.sh  # Linux/macOS
start.bat      # Windows
```

### 使用流程

1. 启动后访问 `http://localhost:5000/login.html`
2. 使用管理员微信扫码登录（需拥有公众号）
3. 登录凭证自动保存，有效期约 4 天

### API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/article` | 获取文章内容 |
| GET | `/api/public/searchbiz` | 搜索公众号 |
| GET | `/api/public/articles` | 获取文章列表 |
| GET | `/api/rss/{fakeid}` | 获取 RSS 源 |
| POST | `/api/rss/subscribe` | 添加 RSS 订阅 |

### MCP 集成（可选）

可以将此 API 封装为 MCP Server 供 AI Agent 调用。

---

## 方案二：mcp-server-wechat-reader

### 简介

专为 AI Agent 设计的微信公众号文章解析 MCP 服务器。

**GitHub**: https://github.com/jessyone/mcp-server-wechat-reader

### 核心功能

- 从公众号文章 URL 提取完整内容
- 支持 Markdown 和纯文本输出
- 自动移除广告、分享按钮等干扰
- 支持代理池和 Cookie 管理

### 安装配置

```bash
# 克隆项目
git clone https://github.com/jessyone/mcp-server-wechat-reader.git
cd mcp-server-wechat-reader

# 安装依赖（需要 Python 3.10+）
uv pip install -e .
```

### MCP 配置

在 `~/.claude/claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "wechat-reader": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "mcp_server_wechat_reader.server"]
    }
  }
}
```

### 工具调用参数

| 参数 | 必需 | 说明 |
|------|------|------|
| url | 是 | 微信公众号文章链接 |
| output_format | 否 | "markdown" 或 "text"，默认 markdown |
| include_images | 否 | 是否包含图片链接，默认 false |

---

## 方案三：微信读书 MCP（mcp-server-weread）

### 简介

用于获取微信读书书架、笔记、划线数据的 MCP Server。

**GitHub**: https://github.com/ChenyqThu/mcp-server-weread

> 注意：微信公众号文章可导入微信读书，通过此方案间接获取。

### 核心功能

- 获取书架书籍信息
- 搜索书架中的图书
- 获取图书的笔记和划线
- 获取图书热门书评

### 安装配置

```json
{
  "mcpServers": {
    "mcp-server-weread": {
      "command": "npx",
      "args": ["-y", "mcp-server-weread"],
      "env": {
        "WEREAD_COOKIE": "你的微信读书Cookie"
      }
    }
  }
}
```

### Cookie 获取方法

1. 登录微信读书网页版 (https://weread.qq.com)
2. F12 打开开发者工具 → Network 标签
3. 刷新页面，找到 weread.qq.com 请求
4. 复制 Headers 中的 Cookie 字段

### CookieCloud 自动刷新（推荐）

安装 CookieCloud 浏览器插件，配置后可自动更新 Cookie：

- 服务器地址：配置自建或公共服务
- 同步域名关键词：`weread`

---

## 方案四：手动导出 + AI 整理（备选）

### 适用场景

- 偶尔使用
- 无需批量处理
- 对自动化要求不高

### 操作步骤

#### 方法 A：浏览器打印 PDF

1. 在微信中打开文章，分享到电脑版微信
2. 点击"用默认浏览器打开"
3. 等待所有图片加载完成
4. Ctrl+P 打印 → 选择"另存为 PDF"

#### 方法 B：复制到笔记软件

1. 全选文章内容复制
2. 粘贴到 Obsidian/Notion/有道云笔记
3. 使用笔记软件的导出功能

#### 方法 C：第三方在线工具

使用在线转换工具（如公众号文章转 PDF 工具）：
- 粘贴文章链接
- 一键生成 PDF/Markdown

### AI 整理流程

导出后可让 AI Agent 帮助：

```
请帮我整理这篇公众号文章：
1. 提取核心观点
2. 生成摘要（200字以内）
3. 整理成结构化笔记
```

---

## 推荐方案

### 根据 use case 选择

| Use Case | 推荐方案 |
|----------|----------|
| AI Agent 自动获取文章内容 | mcp-server-wechat-reader |
| 批量订阅公众号、RSS 同步 | wechat-download-api |
| 获取读书笔记、划线 | mcp-server-weread |
| 偶尔保存单篇文章 | 浏览器打印 PDF |

### 最佳实践

1. **优先使用 MCP Server**：与 Claude 无缝集成
2. **Cookie 定期刷新**：使用 CookieCloud 自动管理
3. **遵守平台规则**：合理控制抓取频率
4. **尊重版权**：仅用于个人学习研究

---

## 风险提示

- Cookie 有效期有限（约 4 天），需要定期刷新
- 过度抓取可能导致账号风控
- 第三方工具可能存在稳定性问题
- 微信平台政策变化可能导致方案失效

---

## 相关资源

- [wechat-download-api](https://github.com/tmwgsicp/wechat-download-api)
- [mcp-server-wechat-reader](https://github.com/jessyone/mcp-server-wechat-reader)
- [mcp-server-weread](https://github.com/ChenyqThu/mcp-server-weread)
- [wereader（Python 客户端）](https://github.com/arry-lee/wereader)
- [Obsidian Weread Plugin](https://github.com/) - 微信读书同步插件

---

## 更新记录

- 2026-04-19：完成初期调研，输出方案对比和推荐
