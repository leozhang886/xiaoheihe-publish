# get_auth.py —— 从 AstrBot preferences 表取出插件登录凭据（不回显敏感值）
import sqlite3
import json

DB = r"C:\Users\86153\astrbot\data\data_v4.db"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

cols = [d[1] for d in cur.execute("PRAGMA table_info(preferences)")]
print("preferences 列:", cols)

rows = list(cur.execute("SELECT * FROM preferences LIMIT 40"))
print("总行数:", len(list(cur.execute("SELECT * FROM preferences"))))
for r in rows:
    d = dict(r)
    # 只显示非敏感字段
    brief = {}
    for k, v in d.items():
        s = str(v)
        if any(x in k.lower() for x in ("cookie", "token", "key", "secret")):
            brief[k] = f"<len={len(s)}>" if s else ""
        elif len(s) > 120:
            brief[k] = s[:120] + "…"
        else:
            brief[k] = s
    print("---")
    print("  ", json.dumps(brief, ensure_ascii=False))

con.close()
