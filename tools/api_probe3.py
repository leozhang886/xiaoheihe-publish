# api_probe3.py —— 系统性试参数，定位 comment/create 的「缺失参数」
# 安全性：link_id/reply_id/root_id 全用 1，text 用空字符串，不可能真的发出评论
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
BASE_COMMON = {
    "os_type": "web", "app": "heybox", "client_type": "web",
    "version": "999.0.4", "web_version": "2.5",
    "x_client_type": "web", "x_app": "heybox_website",
    "x_os_type": "Windows", "device_info": "Chrome",
    "device_id": DEVICE, "heybox_id": AUTH.get("heybox_id", ""),
}
BASE_DATA = {"is_cy": "", "link_id": "1", "reply_id": "1", "root_id": "1", "text": ""}


def call(query_extra, data_extra, label):
    hkey, nonce, ts = get_heybox_request_keys("/bbs/app/comment/create")
    q = {**BASE_COMMON, **query_extra}
    q.update({"hkey": hkey, "_time": str(ts), "nonce": nonce})
    d = {**BASE_DATA, **data_extra}
    url = "https://workshopapi.xiaoheihe.cn/bbs/app/comment/create?" + urllib.parse.urlencode(q)
    body = urllib.parse.urlencode(d).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("User-Agent", UA)
    req.add_header("Referer", "https://www.xiaoheihe.cn/")
    req.add_header("Origin", "https://www.xiaoheihe.cn")
    req.add_header("Cookie", AUTH.get("cookie", ""))
    req.add_header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            txt = r.read().decode("utf-8", "replace")
            try:
                o = json.loads(txt); st, msg = o.get("status"), o.get("msg")
            except Exception:
                st, msg = "?", txt[:60]
            flag = "★" if st not in ("failed",) or (msg and msg != "缺失参数") else " "
            print(f" {flag} {label:<40} status={st!r} msg={msg!r}")
    except Exception as e:
        print(f"   {label:<40} ERR {e}")


print("基线:", "is_cy='' + app=heybox  → 期望复现「缺失参数」")
print()
call({}, {}, "基线（插件当前）")
call({}, {"is_cy": "0"}, "is_cy=0")
call({}, {"is_cy": "1"}, "is_cy=1")
call({}, {"text": "x"}, "text=x（非空）")
call({"_notip": "true"}, {}, "+ _notip=true")
call({"app": "web"}, {}, "app=web")
call({"app": "web"}, {"is_cy": "0"}, "app=web + is_cy=0")
call({"x_app": "heybox"}, {}, "x_app=heybox")
call({}, {"user_id": AUTH.get("heybox_id", "")}, "+ data.user_id")
call({}, {"is_cy": "", "extra": ""}, "+ data.extra=''")
call({"_notip": "true", "app": "web"}, {"is_cy": "0"}, "全加：_notip + app=web + is_cy=0")
