# 生成「10 月 20 日新闻」的配图
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

# ---------- 封面 ----------
W, H = 1200, 675
img = Image.new("RGB", (W, H), (12, 15, 22))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(20 - 9 * k), int(26 - 13 * k), int(42 - 21 * k)))

tag = F(REG, 25)
t = "10 月 20 日 · 能动手的才写"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(24, 36, 30), outline=(58, 100, 78), width=2)
d.text((80, 55), t, font=tag, fill=(140, 214, 168))

d.text((58, 124), "今天能白嫖的", font=F(BOLD, 64), fill=(238, 242, 248))
d.text((58, 204), "一个 Demo，20 个卡包", font=F(BOLD, 56), fill=(240, 186, 96))

items = [
    ("Steam 免费 Demo", "上古世纪编年史 · 到 10/27", "不用申请", (120, 190, 240)),
    ("炉石 20 个卡包", "含 5 个帝国包", "登录就能做任务", (200, 160, 240)),
    ("魔兽万圣节", "到 11/2", "奎尔萨拉斯有新糖罐", (140, 220, 160)),
]
y = 306
for name, note, tail, col in items:
    d.rounded_rectangle([58, y, W - 58, y + 92], 12, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
    d.rounded_rectangle([58, y, 66, y + 92], 4, fill=col)
    d.text((90, y + 14), name, font=F(BOLD, 31), fill=(230, 236, 246))
    d.text((90, y + 58), note, font=F(REG, 22), fill=(150, 156, 172))
    d.text((760, y + 34), tail, font=F(REG, 22), fill=col)
    y += 102

d.text((58, H - 42), "新闻很多，跟你有关的没几条", font=F(REG, 26), fill=(140, 146, 162))
img.save(os.path.join(ROOT, "cover-daily-news.png"))
print("cover-daily-news.png ok")

# ---------- 正文图：今天的时间表 ----------
W2, H2 = 1150, 620
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 26), "今天到月底，能做的事", font=F(BOLD, 40), fill=(22, 26, 36))
dr.text((38, 76), "按截止时间从近到远排", font=F(REG, 21), fill=(126, 132, 148))

rows = [
    ("现在", "Steam 免费 Demo", "上古世纪编年史", "到 10/27 凌晨 1 点", (72, 146, 224)),
    ("现在", "炉石诸神宝库", "20 卡包 + 31 皮肤", "活动期内做完任务", (150, 110, 210)),
    ("今晚", "S16 瑞士轮", "TES vs HLE、IG vs GEN", "中韩对决两场", (200, 90, 90)),
    ("明天", "绝区零 3.3", "两个新 S 级代理人", "10/21 上线", (72, 186, 132)),
    ("到 11/2", "魔兽万圣节", "奎尔萨拉斯午夜糖罐", "每天每小时开 15 分钟", (200, 150, 40)),
]
y = 122
for when, what, detail, note, col in rows:
    dr.rounded_rectangle([38, y, W2 - 38, y + 82], 12, fill=(255, 255, 255), outline=(224, 226, 234), width=2)
    dr.rounded_rectangle([38, y, 46, y + 82], 4, fill=col)
    dr.text((68, y + 26), when, font=F(BOLD, 24), fill=col)
    dr.text((210, y + 14), what, font=F(BOLD, 25), fill=(30, 36, 48))
    dr.text((210, y + 50), detail, font=F(REG, 21), fill=(110, 116, 132))
    dr.text((700, y + 26), note, font=F(REG, 21), fill=(126, 132, 148))
    y += 92

dr.text((38, y + 10), "顺手能领的别拖，活动一过就归零", font=F(BOLD, 23), fill=(26, 32, 44))
im.save(os.path.join(ROOT, "daily-news-list.jpg"), quality=92, optimize=True)
print(f"  daily-news-list.jpg  {im.size}")
