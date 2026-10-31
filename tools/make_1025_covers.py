"""生成 Factorio 封面（真实截图）和游戏库封面（自制），都贴吉祥物。"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG = r"C:\Windows\Fonts\msyh.ttc"
PY = r"C:\Users\86153\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
def F(p, s): return ImageFont.truetype(p, s)

W, H = 1200, 675
TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")


def stamp(name):
    subprocess.run([PY, os.path.join(TOOLS, "add_mascot.py"), "--only", name],
                   capture_output=True, text=True)


def news_cover(src, out, tag, l1, l2, sub, accent):
    base = Image.open(src).convert("RGB")
    sc = max(W / base.width, H / base.height)
    base = base.resize((int(base.width * sc) + 1, int(base.height * sc) + 1), Image.LANCZOS)
    l = (base.width - W) // 2
    t = (base.height - H) // 2
    base = base.crop((l, t, l + W, t + H))

    veil = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(veil)
    for x in range(W):
        k = max(0.0, 1 - x / (W * 0.70))
        vd.line([(x, 0), (x, H)], fill=int(228 * k ** 1.1))
    black = Image.new("RGB", (W, H), (8, 10, 14))
    base = Image.composite(black, base, veil.filter(ImageFilter.GaussianBlur(2)))

    g = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(g)
    for y in range(H):
        a = 0
        if y < 140:
            a = int(140 * (1 - y / 140))
        if y > H - 120:
            a = max(a, int(165 * ((y - (H - 120)) / 120)))
        gd.line([(0, y), (W, y)], fill=a)
    base = Image.composite(black, base, g)

    d = ImageDraw.Draw(base)
    tf = F(REG, 24)
    d.rounded_rectangle([52, 40, 52 + d.textlength(tag, font=tf) + 40, 86], 22,
                        fill=(18, 22, 16), outline=(96, 120, 56), width=2)
    d.text((72, 50), tag, font=tf, fill=(206, 226, 140))
    d.text((52, 146), l1, font=F(BOLD, 52), fill=(246, 248, 252))
    d.text((52, 214), l2, font=F(BOLD, 52), fill=accent)
    d.text((52, 300), sub, font=F(REG, 27), fill=(198, 206, 220))

    base.save(os.path.join(ROOT, out))
    print(out)
    stamp(out)


# A. Factorio：官方工厂截图
news_cover(os.path.join(ROOT, "news-factorio", "shot2.jpg"),
           "cover-factorio.png",
           "10 月 23 日 · 最后一次大更新",
           "做了十四年",
           "Factorio 宣布做完了",
           "23.4 万好评，主动收工",
           (232, 200, 96))

# D. 游戏库：自制
img = Image.new("RGB", (W, H), (12, 14, 20))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(20 - 9*k), int(26 - 12*k), int(44 - 22*k)))

tf = F(REG, 25)
t = "Steam · 库管理"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tf) + 42, 92], 24,
                    fill=(24, 32, 50), outline=(62, 88, 128), width=2)
d.text((80, 55), t, font=tf, fill=(152, 184, 228))

d.text((58, 120), "游戏库太乱", font=F(BOLD, 56), fill=(240, 242, 248))
d.text((58, 192), "两个能用的办法", font=F(BOLD, 56), fill=(240, 186, 96))

rows = [
    ("Steam 自带收藏夹", "四个分类就够，别建十几个", (120, 190, 240)),
    ("Playnite", "★14,346，跨平台统一库", (130, 210, 160)),
    ("Depressurizer", "已归档，别再用了", (220, 100, 96)),
]
y = 300
for nm, note, col in rows:
    d.rounded_rectangle([58, y, W - 58, y + 84], 11, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
    d.rectangle([58, y, 65, y + 84], fill=col)
    d.text((90, y + 14), nm, font=F(BOLD, 26), fill=col)
    d.text((90, y + 50), note, font=F(REG, 21), fill=(148, 154, 170))
    y += 94

d.text((58, H - 42), "星数高不等于还活着", font=F(REG, 25), fill=(140, 146, 162))
img.save(os.path.join(ROOT, "cover-library.png"))
print("cover-library.png")
stamp("cover-library.png")
