# 生成「这周游戏圈」的配图
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

# ---------- 封面 ----------
W, H = 1200, 675
img = Image.new("RGB", (W, H), (13, 15, 24))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(22 - 10 * k), int(26 - 14 * k), int(44 - 22 * k)))

tag = F(REG, 25)
t = "游戏周报 · 10 月 13 – 19 日"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(24, 34, 54), outline=(60, 92, 130), width=2)
d.text((80, 55), t, font=tag, fill=(150, 184, 228))

d.text((58, 120), "三个大作", font=F(BOLD, 62), fill=(238, 242, 248))
d.text((58, 196), "挤在月底", font=F(BOLD, 62), fill=(240, 186, 96))

rows = [
    ("10/22", "最终幻想：共鸣", "¥268", "Switch2 实体版是密钥卡", (120, 190, 240)),
    ("10/22", "现代战争 4", "¥298", "战役已开评，92.5% 好评", (140, 220, 160)),
    ("10/28", "影之刃零", "¥268", "愿望单破 300 万", (240, 176, 96)),
]
y = 306
for date, name, price, note, col in rows:
    d.rounded_rectangle([58, y, W - 58, y + 86], 12, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
    d.rounded_rectangle([58, y, 66, y + 86], 4, fill=col)
    d.text((88, y + 12), date, font=F(BOLD, 26), fill=col)
    d.text((200, y + 10), name, font=F(BOLD, 31), fill=(230, 236, 246))
    d.text((620, y + 16), price, font=F(BOLD, 27), fill=(240, 196, 92))
    d.text((88, y + 52), note, font=F(REG, 21), fill=(148, 154, 170))
    y += 96

d.text((58, H - 42), "还有一个坑：Switch2 那张卡带不含游戏数据", font=F(REG, 25), fill=(150, 156, 172))
img.save(os.path.join(ROOT, "cover-weekly-news.png"))
print("cover-weekly-news.png ok")

# ---------- 正文图：本月发售时间线 ----------
W2, H2 = 1150, 660
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 26), "月底这波怎么排", font=F(BOLD, 40), fill=(22, 26, 36))
dr.text((38, 76), "数据来自 Steam 商店页与评测接口，抓取于 2026-10-19", font=F(REG, 21), fill=(126, 132, 148))

# 时间轴
AX, AY = 80, 210
dr.line([(AX, AY), (W2 - 80, AY)], fill=(210, 214, 224), width=4)
events = [
    (0.10, "10/22", "FF 共鸣", "¥268", (72, 146, 224)),
    (0.42, "10/22", "现代战争 4", "¥298", (72, 186, 132)),
    (0.78, "10/28", "影之刃零", "¥268", (224, 150, 60)),
]
for pos, date, name, price, col in events:
    x = int(AX + (W2 - 160) * pos)
    dr.ellipse([x - 14, AY - 14, x + 14, AY + 14], fill=col, outline=(255, 255, 255), width=3)
    dr.text((x - 26, AY - 70), date, font=F(BOLD, 26), fill=col)
    dr.text((x - 40, AY + 34), name, font=F(BOLD, 25), fill=(32, 38, 50))
    dr.text((x - 26, AY + 74), price, font=F(BOLD, 23), fill=(150, 100, 30))

# 数据块
dr.line([(38, 348), (W2 - 38, 348)], fill=(222, 224, 232), width=2)
dr.text((38, 372), "已经能查到的数据", font=F(BOLD, 30), fill=(22, 26, 36))

facts = [
    ("影之刃零", "愿望单 300 万+", "Steam 热门即将推出前十", (224, 150, 60)),
    ("现代战争 4", "92.5% 好评 · 3,846 条", "还没发售，战役已开评", (72, 186, 132)),
    ("FF 共鸣", "Switch2 版 12.6 GB", "实体版是密钥卡，要下载", (72, 146, 224)),
]
y = 420
for name, big, note, col in facts:
    dr.rounded_rectangle([38, y, W2 - 38, y + 64], 10, fill=(255, 255, 255), outline=(224, 226, 234), width=2)
    dr.rounded_rectangle([38, y, 45, y + 64], 4, fill=col)
    dr.text((66, y + 18), name, font=F(BOLD, 24), fill=(32, 38, 50))
    dr.text((280, y + 16), big, font=F(BOLD, 24), fill=col)
    dr.text((640, y + 20), note, font=F(REG, 21), fill=(110, 116, 132))
    y += 74

im.save(os.path.join(ROOT, "weekly-news-timeline.jpg"), quality=92, optimize=True)
print(f"  weekly-news-timeline.jpg  {im.size}")
