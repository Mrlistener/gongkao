# -*- coding: utf-8 -*-
"""
本地练习服务器：把答题记录直接写进仓库，方便复盘与分析。

启动后浏览器打开 http://127.0.0.1:8765/
- 静态页面照常浏览（仓库根目录）
- 练习页交卷时 POST /api/log，追加一行 JSON 到 04_错题与笔记/答题记录.jsonl
- GET /api/log 返回全部记录（JSON 数组）
"""
import json
import os
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT, "04_错题与笔记")
LOG_FILE = os.path.join(LOG_DIR, "答题记录.jsonl")
SHENLUN_FILE = os.path.join(LOG_DIR, "申论作答.jsonl")
PORT = int(os.environ.get("QUIZ_PORT", "8765"))

# 短地址：避免输入又长又难记的编码路径
SHORTCUTS = {
    "/mem": "/01_行测/04_资料分析/记忆卡.html",
    "/flash": "/01_行测/04_资料分析/公式闪卡.html",
    "/drill1": "/01_行测/04_资料分析/演练/第1套.html",
    "/drill2": "/01_行测/04_资料分析/演练/公式选择2.html",
    "/choose1": "/01_行测/04_资料分析/演练/公式选择1.html",
    "/wrong": "/01_行测/04_资料分析/错题集.html",
    "/concept": "/01_行测/04_资料分析/概念地图.md",
    "/quiz": "/01_行测/04_资料分析/演练/概念小测.html",
    "/sl1": "/02_申论/要点训练·第1套.html",
    "/sl2025": "/02_申论/真题·2025国考执法卷.html",
    "/zl2025": "/01_行测/04_资料分析/真题/2025国考行测·资料分析.html",
    "/fraction": "/01_行测/04_资料分析/分数表.html",
}

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def append_shenlun(obj):
    os.makedirs(LOG_DIR, exist_ok=True)
    if "at" not in obj:
        obj["at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SHENLUN_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def read_log():
    if not os.path.exists(LOG_FILE):
        return []
    out = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def append_log(obj):
    os.makedirs(LOG_DIR, exist_ok=True)
    if "at" not in obj:
        obj["at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def _json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for k, v in CORS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        for k, v in CORS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path in SHORTCUTS:
            from urllib.parse import quote
            self.send_response(302)
            self.send_header("Location", quote(SHORTCUTS[path]))
            self.end_headers()
            return
        if self.path.split("?")[0] == "/api/log":
            self._json(200, read_log())
            return
        super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] != "/api/log":
            self._json(404, {"error": "not found"})
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n).decode("utf-8")
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                raise ValueError("body must be object")
        except Exception as e:
            self._json(400, {"error": str(e)})
            return
        if obj.get("kind") == "shenlun_answer":
            append_shenlun(obj)
            self._json(200, {"ok": True, "saved": "申论作答"})
            return
        append_log(obj)
        self._json(200, {"ok": True, "count": len(read_log())})

    def end_headers(self):
        if self.path.split("?")[0].endswith((".html", ".json")) or self.path == "/":
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


def main():
    os.chdir(ROOT)
    url = "http://127.0.0.1:%d/" % PORT
    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError as e:
        print("端口 %d 被占用或无法监听：%s" % (PORT, e))
        print("可设置环境变量 QUIZ_PORT 换一个端口，例如：set QUIZ_PORT=8766")
        input("按回车退出...")
        return
    print("练习服务器已启动：", url)
    print("答题记录写入：", LOG_FILE)
    print("关闭此窗口即停止服务。")
    if os.environ.get("QUIZ_NO_BROWSER") != "1":
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()