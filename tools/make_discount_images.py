# 生成「Steam 折扣」那篇的两张配图
from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
os.makedirs(OUT, exist_ok=True)
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"

def F(p, s): return ImageFont.truetype(p, s)

def wrap_cjk(text, font, max_w, draw):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        t = cur + ch
        if draw.textlength(t, font=font) > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur = t
    if cur: lines.append(cur)
    return lines

# ---------- 1. 封面 ----------
W, H = 1200, 675
img = Image.new("RGB", (W, H), (18, 14, 14))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(34 - 18 * k), int(22 - 12 * k), int(20 - 10 * k)))

tag = F(REG, 26)
t = "实测 · Steam 官方接口 + 4 个比价站"
d.rounded_rectangle([60, 52, 60 + d.textlength(t, font=tag) + 44, 102], 25,
                    fill=(58, 32, 30), outline=(120, 62, 58), width=2)
d.text((82, 64), t, font=tag, fill=(232, 150, 140))

# 两栏对比
big = F(BOLD, 62)
price = F(BOLD, 74)
lab = F(REG, 28)

def col(x, disc, prc, good):
    c = (90, 220, 150) if good else (235, 95, 85)
    d.text((x, 178), disc, font=big, fill=c)
    d.text((x, 258), prc, font=price, fill=(240, 242, 248))
    d.text((x, 352), "实付", font=lab, fill=(140, 145, 160))

col(70, "打 2 折", "¥93.60", False)
col(640, "打 2.5 折", "¥69.75", True)

# 中间分隔
d.line([(596, 170), (596, 400)], fill=(70, 74, 88), width=3)

# 底部结论
con = F(BOLD, 46)
d.text((70, 452), "折扣更狠的那个，反而贵 24 块", font=con, fill=(245, 246, 250))
sub = F(REG, 32)
d.text((70, 528), "荒野大镖客2 · 终极版 vs 标准版", font=sub, fill=(150, 155, 170))
d.text((70, H - 58), "只看百分比，就会买错", font=F(REG, 27), fill=(120, 125, 140))

img.save(os.path.join(OUT, "cover-discount.png"))
print("cover-discount.png ok", img.size)

# ---------- 2. 两个算例 ----------
W2, H2 = 1120, 750
img2 = Image.new("RGB", (W2, H2), (250, 250, 252))
d2 = ImageDraw.Draw(img2)
d2.text((60, 44), "两个真实算例", font=F(BOLD, 46), fill=(24, 26, 34))

def panel(y, title, rows, note):
    pad = 34
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    body = F(REG, 31); bodyb = F(BOLD, 31)
    allp = []
    for txt, col, bold in rows:
        f = bodyb if bold else body
        allp.append((wrap_cjk(txt, f, W2 - 120 - pad * 2, tmp), col, f))
    need = 104 + sum(len(ls) * 48 for ls, _, _ in allp) + 78
    d2.rounded_rectangle([60, y, W2 - 60, y + need], 18,
                         fill=(255, 255, 255), outline=(224, 226, 234), width=3)
    d2.text((60 + pad, y + 26), title, font=F(BOLD, 34), fill=(30, 34, 46))
    cy = y + 100
    for ls, col, f in allp:
        for ln in ls:
            d2.text((60 + pad + 2, cy), ln, font=f, fill=col)
            cy += 48
    d2.text((60 + pad + 2, y + need - 62), note, font=F(BOLD, 30), fill=(200, 70, 60))
    return y + need + 32

y = 128
y = panel(y, "① 荒野大镖客2", [
    ("终极版  原价 468  打 2 折  →  实付 93.60", (60, 64, 76), False),
    ("标准版  原价 279  打 2.5 折 →  实付 69.75", (60, 64, 76), False),
], "折扣更狠，但贵了 24 块")

y = panel(y, "② 赛博朋克 2077", [
    ("本体 89.40  +  往日之影 89.40  =  分开买 178.80", (60, 64, 76), False),
    ("终极版  原价 411.24  打 4 折  →  实付 164.50", (60, 64, 76), False),
], "折扣更小，但省了 14 块 3")

img2.save(os.path.join(OUT, "flow-discount.png"))
print("flow-discount.png ok", img2.size)
