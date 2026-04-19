#!/bin/bash
# link-skills.sh - 将 AI_apply 的自研 skills 和 hooks 软链接到 ~/.claude/
#
# 使用方式：
#   ./link-skills.sh        # 创建软链接
#   ./link-skills.sh --unlink  # 删除软链接

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

# 自研 skills 列表
SELF_SKILLS=(
    "intel"
    "bilibili-analyzer"
    "log-analyzer"
    "test-case-generator"
    "deep-review"
)

# 自研 hooks 列表
SELF_HOOKS=(
    "review-trigger.py"
    "README.md"
)

echo "🔗 管理 AI_apply 自研 Skills 和 Hooks 软链接..."
echo ""

# 确保 ~/.claude 目录存在
mkdir -p "$CLAUDE_DIR/skills"
mkdir -p "$CLAUDE_DIR/hooks"

if [ "$1" == "--unlink" ]; then
    echo "删除软链接..."

    # Skills
    for skill in "${SELF_SKILLS[@]}"; do
        target="$CLAUDE_DIR/skills/$skill"
        if [ -L "$target" ]; then
            rm "$target"
            echo "  ✅ 已删除: skills/$skill"
        fi
    done

    # Hooks
    for hook in "${SELF_HOOKS[@]}"; do
        target="$CLAUDE_DIR/hooks/$hook"
        if [ -L "$target" ]; then
            rm "$target"
            echo "  ✅ 已删除: hooks/$hook"
        fi
    done
else
    echo "创建软链接..."

    # Skills
    for skill in "${SELF_SKILLS[@]}"; do
        source="$SCRIPT_DIR/skills/$skill"
        target="$CLAUDE_DIR/skills/$skill"

        if [ -L "$target" ]; then
            echo "  ⏭️  已存在: skills/$skill"
        elif [ -d "$target" ]; then
            echo "  ⚠️  已存在目录: skills/$skill"
        else
            ln -s "$source" "$target"
            echo "  ✅ 已链接: skills/$skill"
        fi
    done

    # Hooks
    for hook in "${SELF_HOOKS[@]}"; do
        source="$SCRIPT_DIR/hooks/$hook"
        target="$CLAUDE_DIR/hooks/$hook"

        if [ -L "$target" ]; then
            echo "  ⏭️  已存在: hooks/$hook"
        elif [ -f "$target" ]; then
            echo "  ⚠️  已存在文件: hooks/$hook"
        else
            ln -s "$source" "$target"
            echo "  ✅ 已链接: hooks/$hook"
        fi
    done
fi

echo ""
echo "当前链接状态："
echo ""
echo "Skills:"
for skill in "${SELF_SKILLS[@]}"; do
    target="$CLAUDE_DIR/skills/$skill"
    if [ -L "$target" ]; then
        echo "  🔗 $skill"
    elif [ -d "$target" ]; then
        echo "  📁 $skill (目录)"
    else
        echo "  ❌ $skill (不存在)"
    fi
done

echo ""
echo "Hooks:"
for hook in "${SELF_HOOKS[@]}"; do
    target="$CLAUDE_DIR/hooks/$hook"
    if [ -L "$target" ]; then
        echo "  🔗 $hook"
    elif [ -f "$target" ]; then
        echo "  📄 $hook (文件)"
    else
        echo "  ❌ $hook (不存在)"
    fi
done
