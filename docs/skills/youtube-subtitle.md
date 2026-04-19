# YouTube 字幕提取

> yt-dlp 字幕下载能力调研结果

---

## 结论

**yt-dlp 支持中文字幕下载，可直接使用。**

| 能力 | 支持情况 | 说明 |
|------|----------|------|
| 手动上传字幕 | ✅ 支持 | --write-subs |
| 自动生成字幕 | ✅ 支持 | --write-auto-subs (仅 YouTube) |
| 中文字幕 | ✅ 支持 | --sub-langs zh / zh-Hans / zh-Hant |
| 字幕格式选择 | ✅ 支持 | --sub-format srt/ass/vtt |

---

## 安装

```bash
# macOS (Homebrew)
brew install yt-dlp

# Python pip
pip install yt-dlp

# 验证安装
yt-dlp --version
```

---

## 核心命令

### 1. 查看可用字幕

```bash
# 列出视频可用的所有字幕
yt-dlp --list-subs "https://www.youtube.com/watch?v=VIDEO_ID"
```

输出示例：
```
Available subtitles for VIDEO_ID:
Language formats
en       vtt, ttml, srv3, srv2, srv1
zh-Hans  vtt, ttml, srv3, srv2, srv1
zh-Hant  vtt, ttml, srv3, srv2, srv1
```

### 2. 下载字幕（不下载视频）

```bash
# 只下载字幕，跳过视频
yt-dlp --write-subs --skip-download "URL"

# 下载手动上传的中文字幕
yt-dlp --write-subs --sub-langs zh --skip-download "URL"

# 下载简体中文字幕
yt-dlp --write-subs --sub-langs zh-Hans --skip-download "URL"

# 下载所有中文字幕变体
yt-dlp --write-subs --sub-langs "zh.*" --skip-download "URL"
```

### 3. 下载自动生成字幕

```bash
# YouTube 自动生成的字幕（如果视频没有上传字幕）
yt-dlp --write-auto-subs --sub-langs zh --skip-download "URL"

# 同时下载手动和自动生成字幕
yt-dlp --write-subs --write-auto-subs --sub-langs zh --skip-download "URL"
```

### 4. 指定字幕格式

```bash
# 下载 SRT 格式
yt-dlp --write-subs --sub-format srt --sub-langs zh --skip-download "URL"

# 格式优先级（优先 srt，备选 ass）
yt-dlp --write-subs --sub-format "srt/ass" --sub-langs zh --skip-download "URL"
```

### 5. 下载视频 + 字幕

```bash
# 下载视频和字幕
yt-dlp --write-subs --sub-langs zh "URL"

# 下载低分辨率视频 + 中文字幕
yt-dlp -S res:480 --write-subs --sub-langs zh --merge-output-format mp4 "URL"

# 完整示例：视频 + 音频 + 简体中文字幕 + mp4 格式
yt-dlp -S res:144 --write-subs --sub-langs zh --merge-output-format mp4 "URL"
```

---

## 字幕语言代码

| 代码 | 语言 |
|------|------|
| `zh` | 中文（通用） |
| `zh-Hans` | 简体中文 |
| `zh-Hant` | 繁体中文 |
| `zh-CN` | 简体中文（大陆） |
| `zh-TW` | 繁体中文（台湾） |
| `en` | 英文 |
| `ja` | 日文 |
| `all` | 所有可用字幕 |

**正则匹配**：
```bash
# 匹配所有中文变体
--sub-langs "zh.*"

# 匹配中文和英文
--sub-langs "zh.*,en"
```

---

## 注意事项

### 1. 字幕可用性

- **手动上传字幕**：需要视频作者上传，可用性不确定
- **自动生成字幕**：仅 YouTube 支持，依赖 YouTube 的语音识别
- **中文自动字幕**：YouTube 对中文语音识别质量一般，建议优先尝试手动字幕

### 2. 网络环境

```bash
# 如果需要代理
yt-dlp --proxy socks5://127.0.0.1:1080 --write-subs --sub-langs zh "URL"

# 或使用 HTTP 代理
yt-dlp --proxy http://127.0.0.1:7890 --write-subs --sub-langs zh "URL"
```

### 3. 字幕质量

| 来源 | 质量评估 | 建议 |
|------|----------|------|
| 手动上传字幕 | ⭐⭐⭐⭐⭐ | 首选 |
| YouTube 自动生成 | ⭐⭐⭐ | 可用，需校对 |
| Whisper 转录 | ⭐⭐⭐⭐ | 备选方案 |

---

## Whisper 备选方案

如果视频没有字幕：

```bash
# 1. 先下载音频
yt-dlp -x --audio-format mp3 "URL"

# 2. 使用 Whisper 转录
whisper audio.mp3 --language Chinese --model medium
```

**推荐工具**：
- [OpenAI Whisper](https://github.com/openai/whisper) - 开源，本地运行
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - 更快的实现
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) - C++ 实现，跨平台

---

## 决策：封装方式

| 方案 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| MCP Server | 自动化程度高 | 开发成本高 | ⭐⭐ |
| CLI Skill | 灵活、可定制 | 需手动调用 | ⭐⭐⭐ |
| 手动使用 | 无开发成本 | 效率低 | ⭐ |

**建议**：封装为 CLI Skill，提供以下能力：

```bash
# 推荐封装
yt-subtitle <url> --lang zh --output transcript.md

# 功能
1. 自动检测可用字幕
2. 优先下载手动字幕
3. 无字幕时提示使用 Whisper
4. 输出为 Markdown 格式
```

---

## 快速参考

```bash
# 查看可用字幕
yt-dlp --list-subs "URL"

# 下载中文字幕（仅字幕）
yt-dlp --write-subs --sub-langs zh --skip-download "URL"

# 下载自动生成中文字幕
yt-dlp --write-auto-subs --sub-langs zh --skip-download "URL"

# 下载视频 + 字幕
yt-dlp --write-subs --sub-langs zh "URL"

# 使用代理
yt-dlp --proxy socks5://127.0.0.1:1080 --write-subs --sub-langs zh "URL"
```

---

## 参考资源

- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp 文档 - Subtitle Options](https://github.com/yt-dlp/yt-dlp#subtitle-options)
- [OpenAI Whisper](https://github.com/openai/whisper)

---

*更新时间：2026-04-19*
