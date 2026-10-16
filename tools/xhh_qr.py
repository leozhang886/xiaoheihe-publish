# xhh_qr.py —— 调用插件 API 启动扫码登录，把二维码渲染成 PNG
import json
import os
import time
import urllib.request

from PIL import Image, ImageDraw

BASE = "http://127.0.0.1:6185"
USER = "astrbot"
PWD = os.environ.get("ASTRBOT_DASHBOARD_PASSWORD")
OUT = r"C:\Users\86153\xhh\shots\xhh-login-qr.png"


def post(path, payload=None, token=None):
    data = json.dumps(payload or {}).encode()
    req = urllib.request.Request(BASE + path, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def get(path, token=None):
    req = urllib.request.Request(BASE + path, method="GET")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


if not PWD:
    raise SystemExit("请先设置 ASTRBOT_DASHBOARD_PASSWORD 环境变量")

# 1) 登录面板
tok = post("/api/auth/login", {"username": USER, "password": PWD})["data"]["token"]
print("[1] dashboard token ok")

# 2) 启动扫码登录
st = post("/api/plug/astrbot_plugin_xhhrobot/login/start", {}, tok)
print("[2] login/start -> state=%s  %s" % (st.get("state"), st.get("message")))

# 3) 轮询拿二维码
matrix = None
for i in range(20):
    p = get("/api/plug/astrbot_plugin_xhhrobot/login/poll?include_qr=1", tok)
    state = p.get("state")
    if p.get("qr_matrix"):
        matrix = p["qr_matrix"]
        print("[3] got qr_matrix  size=%s  expires_at=%s" % (matrix["size"], p.get("expires_at")))
        break
    print("    poll %d -> state=%s" % (i + 1, state))
    if state in ("authenticated", "failed", "cancelled"):
        print("    终止：%s  %s" % (state, p.get("message")))
        break
    time.sleep(1.5)

if not matrix:
    raise SystemExit("未能取到二维码")

# 4) 渲染成图片（矩阵已由 API 给出，不需要 qrcode 库）
size = matrix["size"]
scale = 10
border = 4
img_size = (size + border * 2) * scale

img = Image.new("RGB", (img_size, img_size), "white")
d = ImageDraw.Draw(img)
for y, row in enumerate(matrix["rows"]):
    for x, ch in enumerate(row):
        if ch == "1":
            px = (x + border) * scale
            py = (y + border) * scale
            d.rectangle([px, py, px + scale - 1, py + scale - 1], fill="black")
img.save(OUT)
print("[4] saved -> %s  (%dx%d)" % (OUT, img_size, img_size))
print("    二维码有效期约 120 秒，请尽快扫")
