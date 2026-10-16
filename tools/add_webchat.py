# add_webchat.py —— 给 AstrBot 加内置 WebChat 平台（用于测试插件命令）
import json
import shutil
import os

CFG = r"C:\Users\86153\astrbot\data\cmd_config.json"

shutil.copy(CFG, CFG + ".bak2")
with open(CFG, encoding="utf-8-sig") as f:
    cfg = json.load(f)

cfg["platform"] = [{
    "id": "webchat",
    "type": "webchat",
    "enable": True,
    "webchat_link_path": "",
    "webchat_present_type": "fullscreen",
}]

with open(CFG, "w", encoding="utf-8-sig") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)

with open(CFG, encoding="utf-8-sig") as f:
    json.load(f)

print("platform 已配置为 WebChat，JSON 校验通过")
print("platform 项数 =", len(cfg["platform"]))
