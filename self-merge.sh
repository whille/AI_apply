#!/bin/bash
# Worker 完成后自合并脚本
# 用法: ./self-merge.sh [success|fail]

set -e
cd "$(dirname "$0")"

[ ! -f ".worker-context" ] && { echo "No .worker-context found"; exit 1; }
source .worker-context

RESULT="${1:-success}"

if [ "$RESULT" = "success" ]; then
  echo "[$(date)] Self-merging $TASK_ID..."

  # 1. 提交当前改动（如果有）
  if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "feat: $TASK_ID completed" || true
  fi

  # 2. 切到主仓库并合并
  cd "$PROJECT_DIR"
  git merge "$BRANCH_NAME" --no-edit -m "feat: $TASK_ID completed" 2>/dev/null || {
    echo "[$(date)] MERGE_FAILED: conflicts detected"
    echo "  Resolve conflicts manually in $PROJECT_DIR"
    exit 1
  }

  # 3. 更新主 prd.json
  if [ -f "prd.json" ]; then
    jq --arg id "$TASK_ID" '
      .userStories = [.userStories[] | if .id == $id then .passes = true else . end]
    ' prd.json > prd.json.tmp
    mv prd.json.tmp prd.json
    echo "[$(date)] Updated prd.json: $TASK_ID marked as passed"
  fi

  # 4. 清理 worktree 和分支
  git worktree remove "$WORKTREE_PATH" --force 2>/dev/null || {
    rm -rf "$WORKTREE_PATH"
  }
  git branch -D "$BRANCH_NAME" 2>/dev/null || true

  echo "[$(date)] $TASK_ID completed and merged successfully"
else
  echo "[$(date)] $TASK_ID marked as failed, keeping worktree for debugging"
fi
