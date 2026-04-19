# B站信息获取方案

> bilibili-api 库调研结果

---

## 结论

**bilibili-api 库可直接使用，支持获取 UP 主信息和视频统计数据。**

| 能力 | 支持情况 | 方法 |
|------|----------|------|
| 用户基本信息 | ✅ 支持 | `User.get_user_info()` |
| 粉丝/关注数 | ✅ 支持 | `User.get_relation_info()` |
| UP主数据统计 | ✅ 支持 | `User.get_up_stat()` |
| 视频统计数据 | ✅ 支持 | `Video.get_info()` |
| 视频字幕 | ⚠️ 需登录 | `Video.get_subtitle()` |

---

## 库信息

| 项目 | 信息 |
|------|------|
| 仓库 | github.com/Nemo2011/bilibili-api |
| Stars | 3,826 |
| Forks | 543 |
| Language | Python |
| 更新频率 | 活跃（最近更新：2026-04-19） |
| 特点 | 全异步、覆盖全、维护活跃 |

---

## 安装

```bash
pip install bilibili-api

# 或从源码安装
pip install git+https://github.com/Nemo2011/bilibili-api.git
```

---

## 核心能力

### 1. 获取 UP 主信息

```python
from bilibili_api import user

# 初始化用户（通过 UID）
u = user.User(uid=208259)

# 获取用户基本信息
info = await u.get_user_info()
# 返回字段：mid, name, sex, face, sign, level, official, vip

# 获取用户关系信息（关注数、粉丝数）
relation = await u.get_relation_info()
# 返回字段：mid, following, follower

# 获取 UP 主数据统计
stat = await u.get_up_stat()
# 返回字段：archive（视频播放量）, article（文章阅读量）, likes（总点赞数）
```

### 2. 用户信息字段详解

```json
{
  "mid": 208259,           // 用户 UID
  "name": "碧诗",          // 昵称
  "sex": "男",             // 性别
  "face": "http://...",    // 头像链接
  "sign": "签名内容",      // 个人签名
  "level": 6,              // 等级 (0-6)
  "official": {
    "role": 2,              // 认证类型
    "title": "bilibili创始人",
    "desc": "认证描述"
  },
  "vip": {
    "type": 2,              // 0普通 1大会员 2年度大会员
    "status": 1             // 1有效 0无效
  }
}
```

### 3. 粉丝/关注数据

```json
{
  "mid": 208259,
  "following": 123,        // 关注数
  "follower": 456789,      // 粉丝数
  "whisper": 0,            // 悄悄关注数
  "black": 0               // 黑名单数
}
```

### 4. UP 主统计数据

```json
{
  "archive": {
    "view": 12345678       // 视频总播放量
  },
  "article": {
    "view": 12345          // 文章总阅读量
  },
  "likes": 987654          // 总点赞数
}
```

### 5. 视频信息获取

```python
from bilibili_api import video

# 通过 BV 号初始化
v = video.Video(bvid="BV1xx411c7mC")

# 获取视频信息
info = await v.get_info()
```

视频信息字段：

```json
{
  "bvid": "BV1xx411c7mC",
  "aid": 362830,
  "title": "视频标题",
  "pic": "封面链接",
  "pubdate": 1234567890,    // 发布时间戳
  "desc": "视频描述",
  "duration": 600,          // 时长（秒）
  "owner": {
    "mid": 208259,
    "name": "UP主名称",
    "face": "头像链接"
  },
  "stat": {
    "view": 123456,         // 播放量
    "danmaku": 1234,        // 弹幕数
    "reply": 456,           // 评论数
    "favorite": 789,        // 收藏数
    "coin": 123,             // 投币数
    "share": 456,           // 分享数
    "like": 7890            // 点赞数
  },
  "tname": "分区名称"
}
```

---

## 知名度判断方案

### 判断维度

| 维度 | 字段 | 权重建议 | 说明 |
|------|------|----------|------|
| **粉丝数** | `follower` | 40% | 核心指标 |
| **等级** | `level` | 15% | 0-6级，反映活跃度 |
| **认证状态** | `official.role` | 20% | 0无/1个人/2机构 |
| **总播放量** | `archive.view` | 15% | 内容影响力 |
| **大会员** | `vip.type` | 10% | 付费意愿参考 |

### 知名度分级

```python
def calculate_credibility(user_info: dict, relation_info: dict, up_stat: dict) -> dict:
    """
    计算 UP 主信服力分数

    返回:
        score: 0-100 分数
        level: S/A/B/C/D 等级
        factors: 各维度得分
    """
    factors = {}

    # 1. 粉丝数 (40分)
    follower = relation_info.get("follower", 0)
    if follower >= 1000000:
        factors["follower"] = 40
    elif follower >= 100000:
        factors["follower"] = 30
    elif follower >= 10000:
        factors["follower"] = 20
    elif follower >= 1000:
        factors["follower"] = 10
    else:
        factors["follower"] = 5

    # 2. 等级 (15分)
    level = user_info.get("level", 0)
    factors["level"] = min(level * 2.5, 15)

    # 3. 认证状态 (20分)
    official_role = user_info.get("official", {}).get("role", 0)
    if official_role == 2:  # 机构认证
        factors["official"] = 20
    elif official_role == 1:  # 个人认证
        factors["official"] = 15
    else:
        factors["official"] = 5

    # 4. 总播放量 (15分)
    archive_view = up_stat.get("archive", {}).get("view", 0)
    if archive_view >= 10000000:
        factors["archive"] = 15
    elif archive_view >= 1000000:
        factors["archive"] = 10
    elif archive_view >= 100000:
        factors["archive"] = 5
    else:
        factors["archive"] = 2

    # 5. 大会员 (10分)
    vip_type = user_info.get("vip", {}).get("type", 0)
    factors["vip"] = 10 if vip_type >= 1 else 3

    score = sum(factors.values())

    # 分级
    if score >= 80:
        level_letter = "S"
    elif score >= 60:
        level_letter = "A"
    elif score >= 40:
        level_letter = "B"
    elif score >= 20:
        level_letter = "C"
    else:
        level_letter = "D"

    return {
        "score": score,
        "level": level_letter,
        "factors": factors
    }
```

### 分级含义

| 等级 | 分数 | 粉丝参考 | 信服力描述 |
|------|------|----------|------------|
| **S** | ≥80 | 100万+ | 头部 UP 主，高度可信 |
| **A** | 60-79 | 10万-100万 | 知名 UP 主，较可信 |
| **B** | 40-59 | 1万-10万 | 活跃 UP 主，一般可信 |
| **C** | 20-39 | 1千-1万 | 普通用户，谨慎参考 |
| **D** | <20 | <1千 | 新用户/低活跃，需验证 |

---

## 使用示例

### 完整示例：获取 UP 主信服力

```python
import asyncio
from bilibili_api import user

async def get_uploader_credibility(uid: int) -> dict:
    """获取 UP 主信服力评估"""

    u = user.User(uid=uid)

    # 并发获取所有信息
    user_info = await u.get_user_info()
    relation_info = await u.get_relation_info()
    up_stat = await u.get_up_stat()

    # 计算信服力
    credibility = calculate_credibility(user_info, relation_info, up_stat)

    return {
        "uid": uid,
        "name": user_info.get("name"),
        "face": user_info.get("face"),
        "follower": relation_info.get("follower"),
        "level": user_info.get("level"),
        "official": user_info.get("official", {}).get("title"),
        "archive_view": up_stat.get("archive", {}).get("view"),
        "credibility": credibility
    }

# 运行
result = asyncio.run(get_uploader_credibility(208259))
print(result)
```

### 从视频 URL 获取 UP 主信息

```python
import asyncio
from bilibili_api import video, user

async def get_video_uploader_info(bvid: str) -> dict:
    """从视频获取 UP 主信息和信服力"""

    # 获取视频信息
    v = video.Video(bvid=bvid)
    video_info = await v.get_info()

    # 提取 UP 主 UID
    owner_mid = video_info["owner"]["mid"]

    # 获取 UP 主详细信息
    u = user.User(uid=owner_mid)
    user_info = await u.get_user_info()
    relation_info = await u.get_relation_info()
    up_stat = await u.get_up_stat()

    return {
        "video": {
            "title": video_info["title"],
            "view": video_info["stat"]["view"],
            "like": video_info["stat"]["like"],
            "pubdate": video_info["pubdate"]
        },
        "uploader": {
            "mid": owner_mid,
            "name": user_info.get("name"),
            "follower": relation_info.get("follower"),
            "level": user_info.get("level"),
            "credibility": calculate_credibility(user_info, relation_info, up_stat)
        }
    }
```

---

## 注意事项

### 1. 无需登录的接口

以下接口**不需要登录即可调用**：

| 接口 | 方法 |
|------|------|
| 用户基本信息 | `get_user_info()` |
| 用户关系信息 | `get_relation_info()` |
| UP 主统计数据 | `get_up_stat()` |
| 视频信息 | `get_info()` |

### 2. 需要登录的接口

| 接口 | 方法 | 用途 |
|------|------|------|
| 视频字幕 | `get_subtitle()` | 需要用户登录态 |
| 点赞/投币 | `like()`, `pay_coin()` | 交互操作 |
| 私信/动态 | 私信相关方法 | 需要身份验证 |

### 3. 频率限制

B站 API 有频率限制，建议：
- 单次脚本间隔 ≥ 1 秒
- 大量数据使用异步并发
- 设置合理的 `User-Agent`

### 4. 代理设置

```python
from bilibili_api import request_settings

# 设置代理
request_settings.set_proxy("http://127.0.0.1:7890")
```

---

## 决策：封装方式

| 方案 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| 直接使用库 | 无开发成本 | 需要写 Python | ⭐⭐⭐ |
| 封装为 CLI | 命令行易用 | 需开发 | ⭐⭐ |
| 封装为 Skill | AI 可调用 | 需配置环境 | ⭐⭐⭐ |

**建议**：
1. 优先直接使用库，Python 脚本调用
2. 后续可封装为 `bilibili-analyzer` skill

---

## 快速参考

```bash
# 安装
pip install bilibili-api

# Python 调用
python -c "
import asyncio
from bilibili_api import user

async def main():
    u = user.User(uid=208259)
    info = await u.get_user_info()
    rel = await u.get_relation_info()
    print(f'{info[\"name\"]}: {rel[\"follower\"]} 粉丝')

asyncio.run(main())
"
```

---

## 参考资源

- [bilibili-api GitHub](https://github.com/Nemo2011/bilibili-api)
- [bilibili-api 文档](https://nemo2011.github.io/bilibili-api/)
- [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect)（已关闭但文档可参考）

---

*更新时间：2026-04-19*
