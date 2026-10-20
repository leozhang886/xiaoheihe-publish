# 生成「本周 GitHub 第 2 期」的配图
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\自媒体\小黑盒\assets"
OUT = os.path.join(ROOT, "gh-weekly")
os.makedirs(OUT, exist_ok=True)

BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

# ---------- 1. 封面 ----------
W, H = 1200, 706
img = Image.new("RGB", (W, H), (10, 13, 20))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(18 - 8 * k), int(24 - 12 * k), int(40 - 20 * k)))

tag = F(REG, 25)
t = "每周 GitHub · 第 2 期"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(26, 32, 52), outline=(66, 86, 130), width=2)
d.text((80, 55), t, font=tag, fill=(150, 178, 226))

d.text((58, 112), "等不到官方", font=F(BOLD, 58), fill=(238, 242, 248))
d.text((58, 180), "玩家就自己做", font=F(BOLD, 58), fill=(240, 176, 92))

items = [
    ("DevilutionX", "9,869", "暗黑1 搬回现代系统"),
    ("PS2Recomp", "3,519", "PS2 静态重编译器"),
    ("bevy", "49,045", "Rust 开源游戏引擎"),
    ("Beyond All Reason", "4,303", "免费开源大型 RTS"),
    ("koharu", "6,322", "AI 漫画翻译"),
]
y = 278
for name, star, note in items:
    d.rounded_rectangle([58, y, W - 58, y + 60], 10, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
    d.text((80, y + 16), name, font=F(BOLD, 27), fill=(226, 232, 242))
    d.text((392, y + 19), "★" + star, font=F(BOLD, 24), fill=(240, 196, 92))
    d.text((560, y + 21), note, font=F(REG, 23), fill=(146, 152, 168))
    y += 70

d.text((58, H - 42), "补的都是官方留下的空位", font=F(REG, 26), fill=(140, 146, 162))
img.save(os.path.join(ROOT, "cover-gh-week2.png"))
print("cover-gh-week2.png ok")

# ---------- 2. 本周观察：都是官方没做的 ----------
rows = [
    ("暗黑1 不移植现代系统", "DevilutionX 自己做移植", 9869),
    ("PS2 游戏不复刻", "PS2Recomp 自己写重编译器", 3519),
    ("商业 RTS 没人做了", "Beyond All Reason 做免费的", 4303),
    ("日文作品没官方中文", "koharu 自己做 AI 翻译", 6322),
    ("商业引擎贵且闭源", "bevy 自己做开源的", 49045),
]
W2, rowh = 1150, 84
H2 = 116 + len(rows) * rowh + 72
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 28), "本周的共同点", font=F(BOLD, 40), fill=(22, 26, 36))
dr.text((38, 76), "五个项目，补的都是同一个位置", font=F(REG, 22), fill=(126, 132, 148))

y = 116
for left, right, star in rows:
    dr.rectangle([30, y, W2 - 30, y + rowh - 8], fill=(243, 244, 248))
    dr.text((46, y + 14), left, font=F(REG, 24), fill=(120, 126, 142))
    dr.text((46, y + 46), "→  " + right, font=F(BOLD, 25), fill=(30, 36, 48))
    dr.text((1000, y + 26), "★" + f"{star:,}", font=F(BOLD, 23), fill=(200, 150, 40))
    y += rowh

dr.text((38, y + 12), "不是情怀，是需求没被满足", font=F(BOLD, 24), fill=(26, 32, 44))
im.save(os.path.join(OUT, "week2-board.jpg"), quality=92, optimize=True)
print(f"  week2-board.jpg  {im.size}  {os.path.getsize(os.path.join(OUT,'week2-board.jpg'))//1024}KB")
