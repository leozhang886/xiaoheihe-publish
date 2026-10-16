# api_probe2.py —— 确认风控影响范围（只用无效参数试探，不会真的发评论）
import json
import sqlite3
import sys
import urllib.parse
import urllib.request

PLUGIN_DIR = r"C:\Users\86153\astrbot\data\plugins\astrbot_plugin_xhhrobot"
sys.path.insert(0, PLUGIN_DIR)
from signing import get_heybox_request_keys  # noqa: E402

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


def call(method, base, path, params, data=None, label=""):
    hkey, nonce, ts = get_heybox_request_keys(path)
    q = dict(params); q.update({"hkey": hkey, "_time": str(ts), "nonce": nonce})
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
            st = ""
            try:
                st = json.loads(txt).get("status", "")
            except Exception:
                pass
            print(f"  {label:<34} HTTP {r.status}  status={st!r}  {txt[:150]}")
    except urllib.error.HTTPError as e:
        print(f"  {label:<34} HTTP {e.code}  {e.read().decode('utf-8','replace')[:150]}")
    except Exception as e:
        print(f"  {label:<34} ERR {e}")


print("=== 各类接口的风控状态 ===")
call("GET", "https://api.xiaoheihe.cn", "/bbs/app/profile/user/profile",
     {**COMMON, "userid": AUTH.get("heybox_id", "")}, label="用户资料(之前可用)")
call("GET", "https://api.xiaoheihe.cn", "/bbs/app/link/tree",
     {**COMMON, "link_id": "191479338", "page": "1", "limit": "20"}, label="帖子详情(插件失败点)")
call("GET", "https://api.xiaoheihe.cn", "/bbs/app/comment/sub/comments",
     {**COMMON, "root_comment_id": "963616474", "lastval": "0"}, label="子评论")
call("GET", "https://api.xiaoheihe.cn", "/bbs/app/feeds",
     {**COMMON, "offset": "0", "pull": "0"}, label="推荐流")
print()
call("POST", "https://workshopapi.xiaoheihe.cn", "/bbs/app/comment/create",
     COMMON, data={"is_cy": "", "link_id": "1", "reply_id": "1", "root_id": "1", "text": ""},
     label="发评论(空文本,不会真发)")
