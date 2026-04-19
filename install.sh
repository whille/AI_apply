#!/bin/bash
# install.sh - 安装 AI_apply 的 Skills 和 Hooks 到 ~/.claude/

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "🚀 安装 AI_apply Skills 和 Hooks..."
echo ""

# 创建目标目录
mkdir -p "$CLAUDE_DIR/skills/info-tracker"
mkdir -p "$CLAUDE_DIR/skills/bilibili-analyzer"
mkdir -p "$CLAUDE_DIR/hooks"

# 安装 Skills
echo "📦 安装 Skills..."
cp "$SCRIPT_DIR/skills/info-tracker/SKILL.md" "$CLAUDE_DIR/skills/info-tracker/"
cp "$SCRIPT_DIR/skills/bilibili-analyzer/SKILL.md" "$CLAUDE_DIR/skills/bilibili-analyzer/"

# 安装 Hooks
echo "🪝 安装 Hooks..."
cp "$SCRIPT_DIR/hooks/review-trigger.py" "$CLAUDE_DIR/hooks/"
cp "$SCRIPT_DIR/hooks/README.md" "$CLAUDE_DIR/hooks/"

# 设置权限
chmod +x "$CLAUDE_DIR/hooks/review-trigger.py"

echo ""
echo "✅ 安装完成！"
echo ""
echo "已安装："
echo "  Skills:"
echo "    - info-tracker"
echo "    - bilibili-analyzer"
echo "  Hooks:"
echo "    - review-trigger.py"
echo ""
echo "使用方式："
echo "  /info-tracker daily"
echo "  /bilibili-analyzer Claude Agent"
echo "  python3 ~/.claude/hooks/review-trigger.py"
echo ""
