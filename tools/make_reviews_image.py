# 生成「Steam 三个评分」的封面
from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
os.makedirs(OUT, exist_ok=True)
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

W, H = 1200, 675
img = Image.new("RGB", (W, H), (13, 17, 26))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(24 - 12 * k), int(32 - 16 * k), int(50 - 26 * k)))

# 标签
tag = F(REG, 26)
t = "同一款游戏 · 同一天"
d.rounded_rectangle([60, 48, 60 + d.textlength(t, font=tag) + 44, 98], 25,
                    fill=(26, 42, 62), outline=(58, 96, 140), width=2)
d.text((82, 60), t, font=tag, fill=(140, 186, 240))

# 三栏数字
pct = F(BOLD, 96)
lab = F(REG, 27)
num = F(REG, 23)

cols = [
    (62,  "87%", "全部评测", "98.5 万条",        (128, 134, 150)),
    (452, "80%", "简体中文", "20.2 万条",        (150, 138, 190)),
    (842, "94%", "最近 30 天", "6910 条",        (90, 220, 150)),
]
for x, p, l, n, c in cols:
    d.text((x, 158), p, font=pct, fill=c)
    d.text((x, 276), l, font=lab, fill=(226, 232, 242))
    d.text((x, 318), n, font=num, fill=(118, 124, 140))

# 分隔线
for x in (416, 806):
    d.line([(x, 160), (x, 340)], fill=(48, 54, 70), width=2)

# 结论
d.line([(60, 396), (W - 60, 396)], fill=(54, 60, 76), width=2)
d.text((60, 428), "差 14 个点，多数人只看左边那个", font=F(BOLD, 44), fill=(244, 246, 250))
d.text((60, 502), "赛博朋克 2077 · Steam 商店页实测", font=F(REG, 30), fill=(150, 156, 172))
d.text((60, H - 56), "最近评测才代表你现在买到的东西", font=F(REG, 27), fill=(112, 118, 134))

img.save(os.path.join(OUT, "cover-reviews.png"))
print("cover-reviews.png ok", img.size)
