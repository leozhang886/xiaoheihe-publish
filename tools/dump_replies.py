# dump_replies.py —— 从插件归档库里读出实际生成的回复
import sqlite3
import json

DB = r"C:\Users\86153\astrbot\data\plugin_data\astrbot_plugin_xhhrobot\comment_archive.sqlite3"

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

print("=== 表 ===")
for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print("  ", r["name"])

for table in ("received_comments", "outbound_replies", "replies", "messages"):
    try:
        cols = [d[1] for d in cur.execute(f"PRAGMA table_info({table})")]
    except Exception:
        continue
    if not cols:
        continue
    print(f"\n=== {table} 列 ===")
    print("  ", cols)
    rows = list(cur.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT 5"))
    if not rows:
        print("   (空)")
    for r in rows:
        d = dict(r)
        print("  ---")
        for k, v in d.items():
            s = str(v)
            if len(s) > 300:
                s = s[:300] + "…"
            print(f"    {k}: {s}")

con.close()
