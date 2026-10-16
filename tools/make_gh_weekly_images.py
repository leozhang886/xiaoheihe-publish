# 生成「每周 GitHub 第 1 期」的配图
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
t = "每周 GitHub · 第 1 期"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(26, 32, 52), outline=(66, 86, 130), width=2)
d.text((80, 55), t, font=tag, fill=(150, 178, 226))

d.text((58, 110), "5 个玩家", font=F(BOLD, 58), fill=(238, 242, 248))
d.text((58, 178), "能直接用上的项目", font=F(BOLD, 58), fill=(238, 242, 248))

items = [
    ("Moonlight", "19,054", "把 PC 游戏串到手机/电视"),
    ("shadPS4", "33,430", "PS4 模拟器"),
    ("Vita3K", "5,817", "PS Vita 模拟器"),
    ("Pumpkin", "12,320", "Rust 写的 MC 服务端"),
    ("Steamodded", "985", "小丑牌 mod 框架"),
]
y = 278
for name, star, note in items:
    d.rounded_rectangle([58, y, W - 58, y + 60], 10, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
    d.text((80, y + 16), name, font=F(BOLD, 29), fill=(226, 232, 242))
    d.text((330, y + 19), "★" + star, font=F(BOLD, 25), fill=(240, 196, 92))
    d.text((510, y + 21), note, font=F(REG, 23), fill=(146, 152, 168))
    y += 70

d.text((58, H - 42), "标准：合法、活跃、玩家能直接用上", font=F(REG, 26), fill=(140, 146, 162))
img.save(os.path.join(ROOT, "cover-gh-week1.png"))
print("cover-gh-week1.png ok")

# ---------- 2. 本周观察：游戏机项目扎堆 ----------
rows = [
    ("AnyPS5", "PS5 程序移植到 PC", 25151, "未选"),
    ("raddebugger", "Epic 出的图形调试器", 794, ""),
    ("Pumpkin", "Rust 写的 MC 服务端", 407, "已选"),
    ("shadPS4", "PS4 模拟器", 370, "已选"),
    ("moonlight-qt", "串流客户端", 173, "已选"),
    ("Vita3K", "PS Vita 模拟器", 44, "已选"),
    ("Steamodded", "小丑牌 mod 框架", 4, "已选"),
]
W2 = 1150
rowh = 76
H2 = 118 + len(rows) * rowh + 86
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 30), "本周榜单上的游戏相关项目", font=F(BOLD, 40), fill=(22, 26, 36))
dr.text((38, 78), "柱长 = 本周新增 star 数", font=F(REG, 22), fill=(120, 126, 142))

y = 118
maxv = max(r[2] for r in rows)
BAR_X, BAR_MAX = 300, 400          # 柱子固定从 300 开始，最长 400
VAL_X, NOTE_X = BAR_X + BAR_MAX + 16, BAR_X + BAR_MAX + 150   # 数值和说明固定位置
for name, note, val, mark in rows:
    faded = (mark == "未选")
    dr.text((38, y + 10), name, font=F(BOLD, 27),
            fill=(150, 154, 164) if faded else (24, 28, 38))
    barw = max(int(BAR_MAX * (val / maxv) ** 0.42), 6)   # 开方压缩，否则小数值看不见
    dr.rounded_rectangle([BAR_X, y + 16, BAR_X + barw, y + 46], 8,
                         fill=(196, 202, 214) if faded else (72, 146, 224))
    dr.text((VAL_X, y + 17), f"{val:,}", font=F(BOLD, 24),
            fill=(150, 154, 164) if faded else (40, 46, 60))
    dr.text((NOTE_X, y + 22), note, font=F(REG, 22), fill=(128, 134, 150))
    y += rowh

dr.text((38, y + 14), "注：AnyPS5 涨星最猛，但把它这类「主机程序移植到 PC」的工具排除在推荐之外。",
        font=F(REG, 21), fill=(122, 128, 144))
im.save(os.path.join(OUT, "weekly-board.jpg"), quality=92, optimize=True)
print(f"  weekly-board.jpg  {im.size}  {os.path.getsize(os.path.join(OUT,'weekly-board.jpg'))//1024}KB")
