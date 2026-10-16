# make_persona.py —— 通过 API 建人格，并把它挂到小黑盒插件上
import json
import os
import urllib.request

BASE = "http://127.0.0.1:6185"
USER = "astrbot"
PWD = os.environ.get("ASTRBOT_DASHBOARD_PASSWORD")
PLUG = r"C:\Users\86153\astrbot\data\config\astrbot_plugin_xhhrobot_config.json"
PERSONA_ID = "heybox_player"

SYSTEM_PROMPT = """你是一个普通的小黑盒玩家，平时爱玩游戏，也爱在评论区跟人唠嗑。

说话风格：
- 口语化，像朋友聊天，不用书面语
- 短句为主，别说教、别端着
- 可以用"哈哈""确实""我也""话说"这类口语词
- 适度用小黑盒表情，别堆太多
- 不吹不黑，有自己的判断，该说缺点就说缺点

禁区：
- 不要用 Markdown 格式（不要加粗、井号、列表符号）
- 不要说"作为AI""我来帮你"这类话
- 回复控制在 50 字以内，别长篇大论
- 不要每次都反问，会显得像客服"""


def req(method, path, payload=None, token=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(r, timeout=25) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]


if not PWD:
    raise SystemExit("请先设置 ASTRBOT_DASHBOARD_PASSWORD 环境变量")

# 1) 登录
_, login = req("POST", "/api/auth/login", {"username": USER, "password": PWD})
tok = login["data"]["token"]
print("[1] 面板登录成功")

# 2) 建人格
body = {
    "persona_id": PERSONA_ID,
    "system_prompt": SYSTEM_PROMPT,
    "begin_dialogs": [],
    "tools": None,
    "skills": None,
    "custom_error_message": None,
}
code, res = req("POST", "/api/persona/create", body, tok)
print("[2] 建人格 -> HTTP %s" % code)
if code not in (200, 201):
    print("    响应: %s" % res)

# 3) 确认
code, lst = req("GET", "/api/persona/list", None, tok)
print("[3] 当前人格列表:")
data = lst.get("data") if isinstance(lst, dict) else None
if isinstance(data, dict):
    data = data.get("personas") or []
for p in (data or []):
    if isinstance(p, dict):
        print("    - %s" % p.get("persona_id"))
    else:
        print("    - %s" % p)

# 4) 挂到小黑盒插件
with open(PLUG, encoding="utf-8-sig") as f:
    pc = json.load(f)
old = pc["ai"].get("persona_id")
pc["ai"]["persona_id"] = PERSONA_ID
with open(PLUG, "w", encoding="utf-8-sig") as f:
    json.dump(pc, f, ensure_ascii=False, indent=2)
print("[4] 插件人格: %r -> %r" % (old, PERSONA_ID))
print("\n完成。人格已建好并挂上。")
