# 生成「2077 XPA」封面，并把吉祥物贴上（只处理这一张）
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

W, H = 1200, 675
img = Image.new("RGB", (W, H), (14, 12, 14))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(34 - 16 * k), int(22 - 8 * k), int(16 + 2 * k)))

tag = F(REG, 25)
t = "2077 · 10 月 22 日"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(52, 38, 18), outline=(132, 98, 40), width=2)
d.text((80, 55), t, font=tag, fill=(248, 214, 130))

d.text((58, 122), "悄悄支持了", font=F(BOLD, 58), fill=(240, 242, 248))
d.text((58, 196), "买一份送一份", font=F(BOLD, 58), fill=(250, 210, 90))

rows = [
    ("Xbox Play Anywhere", "主机 + PC 都能玩，存档成就通用", (250, 210, 90)),
    ("2.5 免费更新", "新任务 · 双持 · 跨平台 MOD", (240, 140, 180)),
    ("六年还在更", "2020 发售，2026 还有新内容", (150, 200, 240)),
]
y = 300
for nm, note, col in rows:
    d.rounded_rectangle([58, y, W - 58, y + 88], 11, fill=(26, 22, 22), outline=(52, 44, 44), width=2)
    d.rounded_rectangle([58, y, 65, y + 88], 4, fill=col)
    d.text((90, y + 12), nm, font=F(BOLD, 27), fill=col)
    d.text((90, y + 52), note, font=F(REG, 21), fill=(150, 146, 142))
    y += 96

d.text((58, H - 42), "源：Xbox 官方新闻 10/22、CDPR 更新说明", font=F(REG, 23), fill=(140, 136, 132))
out = os.path.join(ROOT, "cover-cp2077-xpa.png")
img.save(out)
print("cover-cp2077-xpa.png", img.size)

# 只给这一张盖吉祥物
r = subprocess.run(
    [r"C:\Users\86153\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe",
     os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "add_mascot.py"),
     "--only", "cover-cp2077-xpa.png"],
    capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
