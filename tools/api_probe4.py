# api_probe4.py —— 对比两种签名算法
import json
import sqlite3
import sys
import urllib.parse
import urllib.request

PLUGIN_DIR = r"C:\Users\86153\astrbot\data\plugins\astrbot_plugin_xhhrobot"
sys.path.insert(0, PLUGIN_DIR)
from signing import get_heybox_request_keys, get_request_keys  # noqa: E402

DB = r"C:\Users\86153\astrbot\data\data_v4.db"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


def load():
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row; cur = con.cursor()
    a = json.loads(cur.execute("SELECT value FROM preferences WHERE scope='plugin' AND key='xhh_auth_v1'").fetchone()["value"])["val"]
    d = json.loads(cur.execute("SELECT value FROM preferences WHERE scope='plugin' AND key='xhh_device_id_v1'").fetchone()["value"])["val"]
    con.close(); return a, d


AUTH, DEVICE = load()
COMMON = {
    "os_type": "web", "app": "heybox", "client_type": "web",
    "version": "999.0.4", "web_version": "2.5",
    "x_client_type": "web", "x_app": "heybox_website",
    "x_os_type": "Windows", "device_info": "Chrome",
    "device_id": DEVICE, "heybox_id": AUTH.get("heybox_id", ""),
}


def shoot(method, base, path, params, data, signer, label):
    hkey, nonce, ts = signer(path)
    q = {**COMMON, **params}
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
            try:
                o = json.loads(txt); st, msg = o.get("status"), o.get("msg")
            except Exception:
                st, msg = "?", txt[:50]
            print(f"  {label:<46} status={st!r} msg={msg!r}")
    except Exception as e:
        print(f"  {label:<46} ERR {e}")


print("=== /bbs/app/comment/create  （空文本，不会真发）===")
DATA = {"is_cy": "", "link_id": "1", "reply_id": "1", "root_id": "1", "text": ""}
shoot("POST", "https://workshopapi.xiaoheihe.cn", "/bbs/app/comment/create",
      {}, DATA, get_heybox_request_keys, "签名A 归一化(插件现用)")
shoot("POST", "https://workshopapi.xiaoheihe.cn", "/bbs/app/comment/create",
      {}, DATA, get_request_keys, "签名B 非归一化(可用版)")

print("\n=== /bbs/app/link/tree ===")
P = {"h_src": "", "link_id": "191479338", "is_first": "1", "page": "1",
     "index": "1", "limit": "20", "owner_only": "0", "sort_filter": "hot"}
shoot("GET", "https://api.xiaoheihe.cn", "/bbs/app/link/tree",
      P, None, get_heybox_request_keys, "签名A 归一化(插件现用)")
shoot("GET", "https://api.xiaoheihe.cn", "/bbs/app/link/tree",
      P, None, get_request_keys, "签名B 非归一化(可用版)")

print("\n=== 对照：已知可用的接口，两种签名 ===")
shoot("GET", "https://api.xiaoheihe.cn", "/bbs/app/profile/user/profile",
      {"userid": AUTH.get("heybox_id", "")}, None, get_heybox_request_keys, "资料 签名A")
shoot("GET", "https://api.xiaoheihe.cn", "/bbs/app/profile/user/profile",
      {"userid": AUTH.get("heybox_id", "")}, None, get_request_keys, "资料 签名B")
