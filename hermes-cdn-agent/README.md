# Hermes CDN Agent

基于 Hermes Agent 的 CDN 调度智能助手

---

## 项目结构

```
hermes-cdn-agent/
├── tools/                    # 工具层
│   ├── schema_infer.py       # 自动 Schema 推断（复用）
│   ├── browser_helper.py     # 浏览器语义提取（复用）
│   └── cdn_tools.py          # CDN 领域工具（自研）
├── hooks/                    # Hermes 钩子
│   └── param_fallback.py     # 参数回退钩子
├── skills/                   # 技能目录
├── config/                   # 配置文件
│   └── settings.yaml
├── tests/
├── scripts/
├── main.py                   # 入口
└── pyproject.toml
```

---

## 快速开始

```bash
# 安装依赖
pip install -e .

# 运行
python main.py
```

---

## 核心能力

1. **数据获取展示** — 多源监控数据整合
2. **问题归因分析** — 根因追溯
3. **技能进化** — 交互学习能力
4. **Git PR 工程化** — 配置变更管理
