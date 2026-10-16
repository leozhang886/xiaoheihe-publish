# api_probe.py —— 直接调小黑盒接口，对比不同参数组合（不回显 cookie）
import json
import sqlite3
import sys
import urllib.parse
import urllib.request

PLUGIN_DIR = r"C:\Users\86153\astrbot\data\plugins\astrbot_plugin_xhhrobot"
sys.path.insert(0, PLUGIN_DIR)
from signing import get_heybox_request_keys  # noqa: E402

DB = r"C:\Users\86153\astrbot\data\data_v4.db"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def load_auth():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    row = cur.execute(
        "SELECT value FROM preferences WHERE scope='plugin' AND key='xhh_auth_v1'"
    ).fetchone()
    dev = cur.execute(
        "SELECT value FROM preferences WHERE scope='plugin' AND key='xhh_device_id_v1'"
    ).fetchone()
    con.close()
    auth = json.loads(row["value"])["val"]
    device = json.loads(dev["value"])["val"] if dev else ""
    return auth, device


AUTH, DEVICE = load_auth()
print("cookie 字段:", sorted(json.loads("{}").keys()) or "ok")
print("heybox_id:", AUTH.get("heybox_id"), " device_id:", DEVICE[:8] + "...")


def call(method, base, path, params, data=None, label=""):
    hkey, nonce, ts = get_heybox_request_keys(path)
    q = dict(params)
    q.update({"hkey": hkey, "_time": str(ts), "nonce": nonce})
    url = base + path + "?" + urllib.parse.urlencode(q)
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("User-Agent", UA)
    req.add_header("Referer", "https://www.xiaoheihe.cn/")
    req.add_header("Origin", "https://www.xiaoheihe.cn")
    req.add_header("Cookie", AUTH.get("cookie", ""))
    if body:
        req.add_header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            txt = r.read().decode("utf-8", "replace")
            print(f"\n[{label}] HTTP {r.status}")
            print("  ", txt[:500])
            return txt
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        print(f"\n[{label}] HTTP {e.code}")
        print("  ", txt[:500])
        return txt
    except Exception as e:
        print(f"\n[{label}] ERR {e}")
        return ""


BASE_API = "https://api.xiaoheihe.cn"
BASE_REPLY = "https://workshopapi.xiaoheihe.cn"

COMMON_PLUGIN = {
    "os_type": "web",
    "app": "heybox",
    "client_type": "web",
    "version": "999.0.4",
    "web_version": "2.5",
    "x_client_type": "web",
    "x_app": "heybox_website",
    "x_os_type": "Windows",
    "device_info": "Chrome",
    "device_id": DEVICE,
    "heybox_id": AUTH.get("heybox_id", ""),
}

COMMON_WORKING = dict(COMMON_PLUGIN)
COMMON_WORKING["app"] = "web"

LINK_ID = "191479338"

print("\n" + "=" * 70)
print("A) /bbs/app/link/tree  —— 复刻插件当前参数")
print("=" * 70)
call("GET", BASE_API, "/bbs/app/link/tree",
     {**COMMON_PLUGIN, "h_src": "", "link_id": LINK_ID, "is_first": "1",
      "page": "1", "index": "1", "limit": "20", "owner_only": "0",
      "sort_filter": "hot"},
     label="A 插件参数")

print("\n" + "=" * 70)
print("B) 同上，但 app 改成 web（对照可用版）")
print("=" * 70)
call("GET", BASE_API, "/bbs/app/link/tree",
     {**COMMON_WORKING, "h_src": "", "link_id": LINK_ID, "is_first": "1",
      "page": "1", "index": "1", "limit": "20", "owner_only": "0",
      "sort_filter": "hot"},
     label="B app=web")

print("\n" + "=" * 70)
print("C) 最简参数（只带必需项）")
print("=" * 70)
call("GET", BASE_API, "/bbs/app/link/tree",
     {**COMMON_WORKING, "link_id": LINK_ID, "page": "1", "limit": "20"},
     label="C 最简")
