#!/bin/bash
# link-skills.sh - 将 AI_apply 的自研 skills 软链接到 ~/.claude/skills/
#
# 使用方式：
#   ./link-skills.sh        # 创建软链接
#   ./link-skills.sh --unlink  # 删除软链接

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_SKILLS="$HOME/.claude/skills"

# 自研 skills 列表
SELF_SKILLS=(
    "info-tracker"
    "bilibili-analyzer"
    "log-analyzer"
    "test-case-generator"
)

echo "🔗 管理 AI_apply 自研 Skills 软链接..."
echo ""

# 确保 ~/.claude/skills 目录存在
mkdir -p "$CLAUDE_SKILLS"

if [ "$1" == "--unlink" ]; then
    echo "删除软链接..."
    for skill in "${SELF_SKILLS[@]}"; do
        target="$CLAUDE_SKILLS/$skill"
        if [ -L "$target" ]; then
            rm "$target"
            echo "  ✅ 已删除: $skill"
        elif [ -d "$target" ]; then
            echo "  ⚠️  跳过（是目录）: $skill"
        fi
    done
else
    echo "创建软链接..."
    for skill in "${SELF_SKILLS[@]}"; do
        source="$SCRIPT_DIR/skills/$skill"
        target="$CLAUDE_SKILLS/$skill"

        if [ -L "$target" ]; then
            echo "  ⏭️  已存在软链接: $skill"
        elif [ -d "$target" ]; then
            echo "  ⚠️  已存在目录，请手动处理: $skill"
            echo "     建议: rm -rf $target && ./link-skills.sh"
        else
            ln -s "$source" "$target"
            echo "  ✅ 已链接: $skill"
        fi
    done
fi

echo ""
echo "当前 ~/.claude/skills/ 中的自研 Skills:"
for skill in "${SELF_SKILLS[@]}"; do
    target="$CLAUDE_SKILLS/$skill"
    if [ -L "$target" ]; then
        echo "  🔗 $skill -> $SCRIPT_DIR/skills/$skill"
    elif [ -d "$target" ]; then
        echo "  📁 $skill (目录)"
    else
        echo "  ❌ $skill (不存在)"
    fi
done
