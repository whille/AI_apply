# B站字幕提取调研报告

> 调研日期：2026-04-19
> 任务 ID：T002
> 状态：已完成

---

## 核心发现

### ⚠️ 重要：bilibili-API-collect 项目已关闭

**2026年1月28日**，bilibili-API-collect（GitHub 超过 20k stars 的第三方 API 收集项目）维护者收到 B站委托律师事务所的律师函，被指控侵权，项目已**停止维护并删除代码**。

> 指控内容："通过技术手段对哔哩哔哩平台非公开的 API 接口及其调用逻辑、参数结构、访问控制及安全认证机制进行系统性收集、整理，并以技术文档、代码示例等形式向不特定公众传播"

**结论**：该项目不可再用，需要寻找替代方案。

---

## 字幕提取技术方案

### 方案一：官方 API 路径（推荐）

#### 步骤

1. **获取视频 cid**
   ```bash
   # 根据 BV 号获取
   curl "https://api.bilibili.com/x/web-interface/view?bvid=BV1xxx"

   # 或根据 aid 获取分 P 信息
   curl "https://api.bilibili.com/x/player/pagelist?aid=36146180"
   ```

   返回示例：
   ```json
   {
     "code": 0,
     "data": [{
       "cid": 63455604,
       "page": 1,
       "part": "视频标题",
       "duration": 401
     }]
   }
   ```

2. **获取 CC 字幕信息**
   ```bash
   curl "https://api.bilibili.com/x/player/v2?bvid=BV1xxx&cid=63455604"
   ```

   返回的 JSON 中包含 `subtitle` 字段，内有字幕下载 URL。

3. **下载字幕文件**
   - 字幕格式：JSON（B站原生）或 SRT
   - 字幕 URL 通常为：`https://.../*.json`

#### Python 示例代码

```python
import requests

def get_bilibili_subtitle(bvid: str) -> dict:
    """获取 B站视频 CC 字幕"""
    # Step 1: 获取视频信息
    video_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://www.bilibili.com/video/{bvid}"
    }
    video_info = requests.get(video_url, headers=headers).json()
    cid = video_info["data"]["cid"]

    # Step 2: 获取字幕信息
    player_url = f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}"
    player_info = requests.get(player_url, headers=headers).json()

    # Step 3: 下载字幕
    if player_info["data"].get("subtitle"):
        subtitle_url = player_info["data"]["subtitle"]["subtitles"][0]["subtitle_url"]
        subtitle = requests.get(subtitle_url, headers=headers).json()
        return subtitle
    return None
```

### 方案二：第三方命令行工具

#### BiliBiliCCSubtitle（推荐）

GitHub: https://github.com/nathanli97/BiliBiliCCSubtitle

```bash
# 安装
pip install BiliBiliCCSubtitle

# 使用
ccdown -d -c https://www.bilibili.com/video/BV1Jt411P77c?p=2
```

**优点**：
- 支持批量下载
- 输出 JSON 和 SRT 两种格式
- 纯命令行，易于集成

**局限**：
- 仅支持有 CC 字幕的视频
- 需要视频上传者提供字幕

### 方案三：浏览器扩展

#### bili-subtitle-copier

GitHub: https://github.com/chenx2code/bili-subtitle-copier

**功能**：
- 在 B站视频页面添加"复制全部字幕"按钮
- 一键复制 SRT 格式字幕文本
- Chrome 扩展，无需安装 Python

**适用场景**：手动提取，非自动化

### 方案四：综合下载工具

#### you-get

GitHub: https://github.com/soimort/you-get

```bash
pip install you-get
you-get https://www.bilibili.com/video/BV1xxx
```

**特点**：
- 支持视频+字幕+弹幕+封面下载
- 支持多平台（YouTube、B站等）
- Python 库可直接调用

#### yt-dlp（功能更强大）

GitHub: https://github.com/yt-dlp/yt-dlp

```bash
pip install yt-dlp
yt-dlp --write-sub --sub-lang zh https://www.bilibili.com/video/BV1xxx
```

---

## 字幕类型说明

| 类型 | 说明 | 获取难度 |
|------|------|----------|
| **CC 字幕** | 上传者提供的官方字幕 | 简单（API 直接获取） |
| **AI 字幕** | B站 AI 小助手自动生成 | 简单（同 CC 字幕接口） |
| **弹幕** | 用户发送的实时评论 | 简单（`/x/v1/dm/list.so`） |

---

## API 接口汇总

| 接口 | 用途 | 认证 |
|------|------|------|
| `/x/web-interface/view` | 获取视频基本信息 | 无需 |
| `/x/player/pagelist` | 获取分 P 信息 | 无需 |
| `/x/player/v2` | 获取字幕信息（核心） | 无需 |
| `/x/v1/dm/list.so` | 获取弹幕 XML | 无需 |

**注意**：以上接口均为公开接口，但 B站可能随时变更。

---

## 推荐方案

### 自动化脚本开发

创建自定义 Python 脚本，使用官方 API 路径：

1. 解析 BV 号
2. 调用 `/x/web-interface/view` 获取 cid
3. 调用 `/x/player/v2` 获取字幕 URL
4. 下载并解析 JSON 字幕
5. 可选转换为 SRT 格式

### 集成到 Claude Skill

将上述脚本封装为 Claude Skill，支持：
- 输入 B站视频链接
- 自动判断有无字幕
- 返回字幕文本供 AI 分析

---

## 法律风险提示

1. **避免使用非公开 API**：bilibili-API-collect 被律师函警告，说明 B站对 API 逆向持否定态度
2. **仅使用公开接口**：上述推荐的接口均为网页端正常加载视频时调用的接口
3. **合理使用**：字幕提取用于个人学习，不建议大规模爬取或商业化

---

## 相关资源

- [B站视频字幕API获取指南](https://blog.csdn.net/Fighting_Dreamer/article/details/86252730)
- [你不知道的黑科技系列:导出下载 b 站视频字幕和弹幕](https://zhuanlan.zhihu.com/p/603293653)
- [bili-subtitle-copier](https://github.com/chenx2code/bili-subtitle-copier)
- [BiliBiliCCSubtitle](https://github.com/nathanli97/BiliBiliCCSubtitle)
- [you-get](https://github.com/soimort/you-get)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

---

## 结论

| 评估项 | 结果 |
|--------|------|
| B站官方 API | 有，但无文档公开 |
| bilibili-API-collect | **已关闭**（律师函） |
| 第三方工具 | 丰富，推荐 BiliBiliCCSubtitle |
| 实现复杂度 | 中等 |
| 法律风险 | 低（使用公开接口） |

**建议**：开发基于 `/x/player/v2` 接口的自定义脚本，避免使用第三方 API 文档项目。
