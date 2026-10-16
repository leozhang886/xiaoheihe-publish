# 生成「进游戏先关这六个」的封面
from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"C:\Users\86153\OneDrive\桌面\自媒体\小黑盒\assets"
os.makedirs(OUT, exist_ok=True)
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

W, H = 1200, 675
img = Image.new("RGB", (W, H), (12, 15, 22))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(22 - 10 * k), int(28 - 14 * k), int(42 - 22 * k)))

# 顶部标签
tag = F(REG, 25)
t = "游戏设置 · 两分钟看完"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(24, 40, 58), outline=(56, 92, 134), width=2)
d.text((80, 55), t, font=tag, fill=(138, 184, 238))

# 主标题
d.text((58, 118), "进游戏先别玩", font=F(BOLD, 62), fill=(238, 242, 248))
d.text((58, 194), "去设置里关这六个", font=F(BOLD, 62), fill=(238, 242, 248))

# 六个效果，两列
items = ["动态模糊", "胶片颗粒", "色差", "暗角", "景深", "镜头抖动"]
f = F(BOLD, 36)
y0, dy = 306, 62
for i, it in enumerate(items):
    col, row = divmod(i, 3)
    x = 58 + col * 560
    y = y0 + row * dy
    # 小方框
    d.rounded_rectangle([x, y + 8, x + 26, y + 34], 6,
                        fill=(30, 44, 62), outline=(72, 108, 150), width=2)
    d.text((x + 44, y), it, font=f, fill=(224, 230, 240))

# 底部
d.line([(58, 528), (W - 58, 528)], fill=(52, 58, 74), width=2)
d.text((58, 552), "它们默认全开，作用只是让画面更像电影", font=F(REG, 30), fill=(158, 164, 180))
d.text((58, H - 42), "代价是你玩游戏时的清晰度", font=F(REG, 26), fill=(116, 122, 138))

img.save(os.path.join(OUT, "cover-settings.png"))
print("cover-settings.png ok", img.size)
