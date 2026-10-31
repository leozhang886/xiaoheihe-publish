"""生成「显示器验货」封面。行距按行数自动算，不会压到页脚。"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

W, H = 1200, 675
FOOTER_H = 70          # 页脚占用的高度
TOP = 292              # 列表起点

img = Image.new("RGB", (W, H), (12, 14, 20))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(20 - 9 * k), int(26 - 12 * k), int(40 - 20 * k)))

tag = F(REG, 25)
t = "显示器 · 二十分钟"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(24, 34, 48), outline=(60, 90, 124), width=2)
d.text((80, 55), t, font=tag, fill=(150, 186, 230))

d.text((58, 118), "新显示器到手", font=F(BOLD, 54), fill=(240, 242, 248))
d.text((58, 188), "先验这几项", font=F(BOLD, 54), fill=(120, 200, 240))

rows = [
    ("坏点", "全屏纯色，红绿蓝各看一遍", (200, 96, 96)),
    ("漏光", "关灯全黑，看四角有没有亮斑", (240, 176, 96)),
    ("刷新率", "OSD 确认真的跑满了", (130, 210, 160)),
    ("分辨率和色深", "驱动面板里查，别只看参数", (120, 170, 230)),
]

avail = H - FOOTER_H - TOP          # 列表可用高度
gap = 8
row_h = min(80, (avail - gap * (len(rows) - 1)) // len(rows))

y = TOP
for nm, note, col in rows:
    d.rounded_rectangle([58, y, W - 58, y + row_h], 11, fill=(22, 26, 38),
                        outline=(42, 48, 64), width=2)
    d.rounded_rectangle([58, y, 65, y + row_h], 4, fill=col)
    d.text((88, y + 10), nm, font=F(BOLD, 25), fill=col)
    d.text((88, y + row_h - 30), note, font=F(REG, 19), fill=(148, 154, 170))
    y += row_h + gap

d.text((58, H - 42), "过了退换期，问题就都成你的了", font=F(REG, 24), fill=(140, 146, 162))

out = os.path.join(ROOT, "cover-monitor-check.png")
img.save(out)
print("cover-monitor-check.png", img.size, "row_h=", row_h, "内容底边 y=", y - gap)

subprocess.run([r"C:\Users\86153\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe",
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "tools", "add_mascot.py"),
                "--only", "cover-monitor-check.png"], capture_output=True, text=True)
print("吉祥物已贴")
