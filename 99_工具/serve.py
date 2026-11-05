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
PORT = int(os.environ.get("QUIZ_PORT", "8765"))

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


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
        append_log(obj)
        self._json(200, {"ok": True, "count": len(read_log())})

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
