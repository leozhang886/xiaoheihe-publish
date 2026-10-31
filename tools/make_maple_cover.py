"""用冒险岛官方登录界面截图做封面。"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

W, H = 1200, 675
src = os.path.join(ROOT, "news-maple", "shot1.jpg")

base = Image.open(src).convert("RGB")
sc = max(W / base.width, H / base.height)
base = base.resize((int(base.width * sc) + 1, int(base.height * sc) + 1), Image.LANCZOS)
left = (base.width - W) // 2
top = (base.height - H) // 2
base = base.crop((left, top, left + W, top + H))

# 左侧压暗
veil = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(veil)
for x in range(W):
    k = max(0.0, 1 - x / (W * 0.72))
    vd.line([(x, 0), (x, H)], fill=int(225 * k ** 1.1))
black = Image.new("RGB", (W, H), (8, 10, 14))
base = Image.composite(black, base, veil.filter(ImageFilter.GaussianBlur(2)))

g = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(g)
for y in range(H):
    a = 0
    if y < 140:
        a = int(140 * (1 - y / 140))
    if y > H - 120:
        a = max(a, int(160 * ((y - (H - 120)) / 120)))
    gd.line([(0, y), (W, y)], fill=a)
base = Image.composite(black, base, g)

d = ImageDraw.Draw(base)
tag = F(REG, 24)
t = "10 月 21 日 · Steam 免费"
d.rounded_rectangle([52, 40, 52 + d.textlength(t, font=tag) + 40, 86], 22,
                    fill=(18, 20, 16), outline=(110, 118, 52), width=2)
d.text((72, 50), t, font=tag, fill=(226, 226, 130))

d.text((52, 148), "冒险岛怀旧服免费了", font=F(BOLD, 52), fill=(246, 248, 252))
d.text((52, 216), "可惜没中文", font=F(BOLD, 52), fill=(240, 140, 120))

d.text((52, 300), "国区还取不到", font=F(REG, 28), fill=(200, 206, 220))

out = os.path.join(ROOT, "cover-maple.png")
base.save(out)
print("cover-maple.png", base.size)

subprocess.run([r"C:\Users\86153\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe",
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "tools", "add_mascot.py"),
                "--only", "cover-maple.png"], capture_output=True, text=True)
print("吉祥物已贴")
