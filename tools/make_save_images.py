# 生成「存档备份」那篇的配图
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

# ---------- 封面 ----------
W, H = 1200, 675
img = Image.new("RGB", (W, H), (12, 14, 22))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(22 - 10 * k), int(26 - 14 * k), int(44 - 24 * k)))

tag = F(REG, 25)
t = "存档 · 丢了就是几百小时"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(46, 30, 32), outline=(116, 74, 74), width=2)
d.text((80, 55), t, font=tag, fill=(236, 160, 152))

d.text((58, 128), "云存档不是备份", font=F(BOLD, 66), fill=(240, 110, 100))
d.text((58, 214), "它同步，不归档", font=F(BOLD, 66), fill=(238, 242, 248))

d.line([(58, 330), (W - 58, 330)], fill=(52, 58, 74), width=2)

# 两条对比
f1, f2 = F(BOLD, 27), F(REG, 22)
d.rounded_rectangle([58, 366, 592, 520], radius=12, fill=(24, 28, 40), outline=(48, 54, 70), width=2)
d.text((80, 384), "同步（云存档）", font=f1, fill=(150, 156, 172))
d.text((80, 424), "你删本地，云上也跟着删", font=f2, fill=(178, 184, 198))
d.text((80, 462), "认的是「最新状态」", font=f2, fill=(178, 184, 198))

d.rounded_rectangle([608, 366, 1142, 520], radius=12, fill=(22, 32, 28), outline=(56, 104, 80), width=2)
d.text((630, 384), "备份（归档）", font=f1, fill=(120, 220, 160))
d.text((630, 424), "你删本地，备份还在", font=f2, fill=(178, 198, 186))
d.text((630, 462), "认的是「保留历史」", font=f2, fill=(178, 198, 186))

d.text((58, 552), "备份花十分钟，不备份可能重玩两百小时", font=F(REG, 28), fill=(158, 164, 180))
d.text((58, H - 44), "Ludusavi 支持 19,000+ 款游戏（★6,420）", font=F(REG, 25), fill=(122, 128, 144))
img.save(os.path.join(ROOT, "cover-save.png"))
print("cover-save.png ok")

# ---------- 正文图：存档在哪 + 该用什么 ----------
W2, H2 = 1150, 640
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 28), "存档可能在哪儿", font=F(BOLD, 40), fill=(22, 26, 36))
dr.text((38, 78), "没有统一规律，每款游戏不一样", font=F(REG, 22), fill=(126, 132, 148))

spots = [
    ("我的文档 / Documents", "最常见", (72, 146, 224)),
    ("AppData（隐藏目录）", "很多人找不到", (200, 150, 40)),
    ("游戏安装目录", "少数游戏这么做", (120, 176, 120)),
    ("Windows 注册表", "最难搞，多数工具管不了", (200, 96, 96)),
]
y = 122
for name, note, col in spots:
    dr.rounded_rectangle([38, y, W2 - 38, y + 74], 12, fill=(255, 255, 255), outline=(224, 226, 234), width=2)
    dr.rounded_rectangle([38, y, 46, y + 74], 4, fill=col)
    dr.text((70, y + 22), name, font=F(BOLD, 26), fill=(28, 32, 42))
    dr.text((620, y + 25), note, font=F(REG, 23), fill=(120, 126, 142))
    y += 86

dr.line([(38, y + 6), (W2 - 38, y + 6)], fill=(220, 222, 230), width=2)
dr.text((38, y + 26), "靠人肉记不现实 —— 用 Ludusavi（★6,420），连注册表里的都能处理",
        font=F(BOLD, 24), fill=(26, 32, 44))
im.save(os.path.join(ROOT, "save-locations.jpg"), quality=92, optimize=True)
print(f"  save-locations.jpg  {im.size}  {os.path.getsize(os.path.join(ROOT,'save-locations.jpg'))//1024}KB")
