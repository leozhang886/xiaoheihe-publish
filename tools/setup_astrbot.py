# setup_astrbot.py —— 写入 DeepSeek provider + 调整插件配置
# 注意：AstrBot 的 json 带 UTF-8 BOM，必须用 utf-8-sig 读写
import json
import shutil
import os

ASTROBOT = r"C:\Users\86153\astrbot\data"
CFG = os.path.join(ASTROBOT, "cmd_config.json")
PLUG = os.path.join(ASTROBOT, "config", "astrbot_plugin_xhhrobot_config.json")

KEY = os.environ.get("DEEPSEEK_KEY", "").strip()
if not KEY:
    raise SystemExit("missing env DEEPSEEK_KEY")

SOURCE_ID = "deepseek_source"

# ---------- 1) AstrBot main config ----------
shutil.copy(CFG, CFG + ".bak")
with open(CFG, encoding="utf-8-sig") as f:
    cfg = json.load(f)

cfg["provider_sources"] = [{
    "id": SOURCE_ID,
    "provider": "deepseek",
    "type": "openai_chat_completion",
    "provider_type": "chat_completion",
    "enable": True,
    "key": [KEY],
    "api_base": "https://api.deepseek.com/v1",
    "timeout": 120,
    "proxy": "",
    "custom_headers": {},
}]

cfg["provider"] = [{
    "id": "deepseek",
    "provider_source_id": SOURCE_ID,
    "model": "deepseek-chat",
    "modalities": [],
    "custom_extra_body": {},
    "enable": True,
}]

with open(CFG, "w", encoding="utf-8-sig") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)

print("[1] cmd_config.json updated (backup .bak)")
print("    provider_sources=%d  provider=%d" % (len(cfg["provider_sources"]), len(cfg["provider"])))
print("    model=%s  api_base=%s" % (cfg["provider"][0]["model"], cfg["provider_sources"][0]["api_base"]))
print("    key written, length=%d (not echoed)" % len(KEY))

# ---------- 2) plugin config ----------
shutil.copy(PLUG, PLUG + ".bak")
with open(PLUG, encoding="utf-8-sig") as f:
    pc = json.load(f)

changed = []


def setp(section, key, value):
    cur = pc.get(section, {}).get(key, "<missing>")
    if cur != value:
        changed.append("%s.%s: %r -> %r" % (section, key, cur, value))
    pc.setdefault(section, {})[key] = value


setp("ai", "provider_id", "deepseek")
setp("filters", "reply_to_own_post_comments", True)
setp("filters", "max_replies_per_own_post", 4)
setp("filters", "allow_all_users", False)
setp("auto_browse", "enabled", False)
setp("direct_messages", "enabled", False)
setp("tools", "enable_write_tools", False)
setp("polling", "poll_interval_sec", 60)
setp("polling", "max_replies_per_cycle", 2)

with open(PLUG, "w", encoding="utf-8-sig") as f:
    json.dump(pc, f, ensure_ascii=False, indent=2)

print("\n[2] plugin config updated (backup .bak)")
if changed:
    for c in changed:
        print("    " + c)
else:
    print("    no change")

# ---------- 3) validate ----------
for p in (CFG, PLUG):
    with open(p, encoding="utf-8-sig") as f:
        json.load(f)
print("\n[3] both JSON validated OK")
