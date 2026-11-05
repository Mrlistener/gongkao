#!/bin/bash
# ============================================================
#  macOS 双击启动：本地练习服务
#
#  首次使用若提示「无法打开」：右键 → 打开，或在本目录执行
#      chmod +x 启动练习.command
#  Linux 也可以：bash 启动练习.command
#  Windows 请双击 启动练习.bat
# ============================================================
cd "$(dirname "$0")" || exit 1

# 按优先级找一个能用的 Python 3：DSH 自带 → PATH 里的 python3 → python
find_python() {
  local bundled="$HOME/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3"
  if [ -x "$bundled" ]; then
    printf '%s\n' "$bundled"
    return 0
  fi

  local name path
  for name in python3 python; do
    path="$(command -v "$name" 2>/dev/null)"
    [ -n "$path" ] || continue
    if "$path" -c 'import sys; raise SystemExit(0 if sys.version_info[0] == 3 else 1)' 2>/dev/null; then
      printf '%s\n' "$path"
      return 0
    fi
  done
  return 1
}

pause_exit() {
  [ -t 0 ] && read -n 1 -s -r -p "按任意键关闭窗口..."
  echo
  exit "$1"
}

if [ ! -f "99_工具/serve.py" ]; then
  echo "找不到 99_工具/serve.py，请确认仓库目录完整。"
  pause_exit 1
fi

if ! PY="$(find_python)"; then
  echo "没有找到 Python 3。"
  echo
  echo "  方式一：xcode-select --install   （系统自带的 Python 3）"
  echo "  方式二：brew install python      （Homebrew）"
  echo "  方式三：https://www.python.org/downloads/"
  pause_exit 1
fi

"$PY" "99_工具/serve.py" "$@"
status=$?

if [ "$status" -ne 0 ]; then
  echo
  echo "服务异常退出（退出码 $status），上面是错误信息。"
  pause_exit "$status"
fi

# 正常停止（Ctrl+C）：窗口已打印「已停止。」
exit 0
