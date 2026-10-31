# 生成「模拟器入门」的配图
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
OUT = os.path.join(ROOT, "emu")
os.makedirs(OUT, exist_ok=True)

BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

# ---------- 1. 封面 ----------
W, H = 1200, 706
img = Image.new("RGB", (W, H), (11, 14, 20))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(20 - 9 * k), int(26 - 13 * k), int(42 - 22 * k)))

tag = F(REG, 25)
t = "模拟器 · 四档速查"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(24, 40, 58), outline=(56, 92, 134), width=2)
d.text((80, 55), t, font=tag, fill=(138, 184, 238))

d.text((58, 110), "哪几台机器", font=F(BOLD, 58), fill=(238, 242, 248))
d.text((58, 178), "现在能玩了", font=F(BOLD, 58), fill=(238, 242, 248))

tiers = [
    ("随便玩", "PS1 · PS2 · PSP · NDS · GC/Wii · Wii U", (92, 214, 148)),
    ("大部分能玩", "PS3 · 3DS · PS Vita", (232, 206, 92)),
    ("看具体游戏", "PS4 · Xbox 360 · Xbox", (238, 152, 88)),
    ("别碰", "Switch（项目已被清空）", (232, 90, 84)),
]
y = 278
for name, list_, col in tiers:
    d.rounded_rectangle([58, y, W - 58, y + 76], 10, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
    d.rounded_rectangle([58, y, 66, y + 76], 4, fill=col)
    d.text((92, y + 14), name, font=F(BOLD, 30), fill=col)
    d.text((92, y + 48), list_, font=F(REG, 21), fill=(146, 152, 168))
    y += 88

d.text((58, H - 42), "数据来自各项目 GitHub 仓库，抓取于 2026-10-13", font=F(REG, 23), fill=(132, 138, 154))
img.save(os.path.join(ROOT, "cover-emu.png"))
print("cover-emu.png ok")

# ---------- 2. 分档速查表 ----------
rows = [
    ("1", "随便玩", "PS1", "DuckStation", "10,831", (92, 214, 148)),
    ("", "", "PS2", "PCSX2", "15,785", (92, 214, 148)),
    ("", "", "PSP", "PPSSPP", "14,646", (92, 214, 148)),
    ("", "", "NDS", "melonDS", "5,105", (92, 214, 148)),
    ("", "", "GC / Wii", "Dolphin", "15,648", (92, 214, 148)),
    ("", "", "Wii U", "Cemu", "9,979", (92, 214, 148)),
    ("2", "大部分能玩", "PS3", "RPCS3", "20,042", (232, 206, 92)),
    ("", "", "3DS", "Azahar", "8,327", (232, 206, 92)),
    ("", "", "PS Vita", "Vita3K", "5,823", (232, 206, 92)),
    ("3", "看具体游戏", "PS4", "shadPS4", "33,479", (238, 152, 88)),
    ("", "", "Xbox 360", "xenia（稳定分支）", "9,714", (238, 152, 88)),
    ("", "", "Xbox", "xemu", "4,177", (238, 152, 88)),
    ("4", "别碰", "Switch", "yuzu / Ryujinx / suyu 均已关闭", "—", (232, 90, 84)),
]

W2 = 1150
rowh = 62
H2 = 112 + len(rows) * rowh + 66
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 28), "模拟器成熟度速查", font=F(BOLD, 40), fill=(22, 26, 36))
dr.text((38, 76), "星数为各项目 GitHub 仓库数据，抓取于 2026-10-13", font=F(REG, 21), fill=(126, 132, 148))

y = 112
for num, tier, plat, emu, star, col in rows:
    if num:
        dr.rectangle([30, y, W2 - 30, y + rowh - 6], fill=(240, 241, 246))
    dr.rounded_rectangle([40, y + 12, 48, y + rowh - 18], 4, fill=col)
    if num:
        dr.text((60, y + 14), f"{num}. {tier}", font=F(BOLD, 25), fill=col)
    dr.text((280, y + 16), plat, font=F(BOLD, 24), fill=(28, 32, 42))
    dr.text((450, y + 18), emu, font=F(REG, 23), fill=(72, 78, 94))
    dr.text((880, y + 16), ("★" + star) if star != "—" else star,
            font=F(BOLD, 23), fill=(150, 154, 164) if star == "—" else (200, 150, 40))
    dr.line([(30, y), (W2 - 30, y)], fill=(228, 230, 238), width=1)
    y += rowh
dr.line([(30, y), (W2 - 30, y)], fill=(214, 216, 226), width=3)
dr.text((38, y + 14), "xenia 主仓库为稳定分支，日常开发在 xenia-canary（★2,630）",
        font=F(REG, 21), fill=(126, 132, 148))

im.save(os.path.join(OUT, "tiers.jpg"), quality=92, optimize=True)
print(f"  tiers.jpg  {im.size}  {os.path.getsize(os.path.join(OUT,'tiers.jpg'))//1024}KB")
