# 生成「显示器四个地方」的配图
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
OUT = os.path.join(ROOT, "display")
os.makedirs(OUT, exist_ok=True)

BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

# ---------- 1. 封面 ----------
W, H = 1200, 675
img = Image.new("RGB", (W, H), (12, 15, 22))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(22 - 10 * k), int(28 - 14 * k), int(44 - 24 * k)))

tag = F(REG, 25)
t = "显示器买回来 · 五分钟自检"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(24, 40, 58), outline=(56, 92, 134), width=2)
d.text((80, 55), t, font=tag, fill=(138, 184, 238))

d.text((58, 116), "买了高刷显示器", font=F(BOLD, 60), fill=(238, 242, 248))
d.text((58, 190), "先查这四个地方", font=F(BOLD, 60), fill=(238, 242, 248))

items = [
    ("1", "刷新率", "是不是还在跑 60Hz"),
    ("2", "色深", "10bit 屏默认只给 8bit"),
    ("3", "可变刷新率", "三个开关，漏一个就不生效"),
    ("4", "缩放", "降分辨率时会不会变形"),
]
y = 296
for n, name, note in items:
    d.rounded_rectangle([58, y + 4, 96, y + 42], 9, fill=(28, 44, 66), outline=(66, 106, 152), width=2)
    d.text((68, y + 10), n, font=F(BOLD, 26), fill=(140, 186, 240))
    d.text((116, y), name, font=F(BOLD, 33), fill=(232, 238, 246))
    d.text((300, y + 6), note, font=F(REG, 27), fill=(140, 146, 162))
    y += 62

d.line([(58, 556), (W - 58, 556)], fill=(52, 58, 74), width=2)
d.text((58, 580), "默认值不等于最佳值，而且不看不知道", font=F(REG, 30), fill=(158, 164, 180))
d.text((58, H - 42), "四项加起来花不了五分钟", font=F(REG, 26), fill=(116, 122, 138))
img.save(os.path.join(ROOT, "cover-display.png"))
print("cover-display.png ok")

# ---------- 2. 色深：8bit 分层的夸张示意 ----------
PW, PH = 1200, 330
canvas = Image.new("RGB", (1244, 330 + 40 + 330 + 150), (16, 18, 24))
dr = ImageDraw.Draw(canvas)

def gradient(steps=256, lo=38, hi=96):
    """纵向渐变；steps 越小，分层越明显"""
    col = np.zeros((PH, PW, 3), dtype=np.float32)
    ramp = np.linspace(lo, hi, PH)
    if steps:
        lv = 256 // steps if steps < 256 else 1
        ramp = np.round(ramp / max(lv, 1)) * max(lv, 1)
    for c in range(3):
        col[:, :, c] = ramp[:, None]
    # 稍微偏蓝，像天空
    col[:, :, 2] *= 1.18
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))

dr.text((22, 14), "8bit（色阶不够，渐变断成一条一条）", font=F(BOLD, 27), fill=(232, 96, 90))
canvas.paste(gradient(steps=8), (22, 50))
dr.text((22, 50 + PH + 24), "色阶更多时（示意，实际差别比这个小得多）", font=F(BOLD, 27), fill=(92, 214, 148))
canvas.paste(gradient(steps=64), (22, 50 + PH + 60))
dr.text((22, 50 + PH * 2 + 86), "说明：这是把差别放大了的示意。8bit 的屏幕上也显示不出真正的 10bit 效果，",
        font=F(REG, 22), fill=(126, 132, 148))
dr.text((22, 50 + PH * 2 + 114), "这张图只用来让你知道「色彩分层」长什么样。", font=F(REG, 22), fill=(126, 132, 148))
canvas.save(os.path.join(OUT, "color-depth.jpg"), quality=90, optimize=True)
print("color-depth.jpg ok")

# ---------- 3. 缩放：拉伸 vs 保持比例 ----------
src = Image.open(os.path.join(ROOT, "kcd2", "ss8.jpg")).convert("RGB")
# 取一个 4:3 的画面（模拟老游戏 / 非宽屏分辨率）
crop = src.crop((300, 150, 1620, 1140))   # 1320x990 ≈ 4:3
PW2, PH2 = 580, 435
FRAME_W = 1030

# 全屏拉伸：直接把 4:3 硬拉到 16:9 铺满整框（画面变形）
stretched = crop.resize((FRAME_W, PH2), Image.LANCZOS)
# 保持比例：按 4:3 放大，两侧留黑边
kept = crop.resize((PW2, PH2), Image.LANCZOS)

c2 = Image.new("RGB", (1244, 40 + PH2 + 40 + PH2 + 60), (16, 18, 24))
d2 = ImageDraw.Draw(c2)
d2.text((22, 14), "全屏拉伸（铺满屏幕，但画面被拉宽）", font=F(BOLD, 27), fill=(232, 96, 90))
c2.paste(stretched, (107, 52))
y2 = 52 + PH2 + 40
d2.text((22, y2 - 38), "保持比例（两边留黑边，画面不变形）", font=F(BOLD, 27), fill=(92, 214, 148))
band = Image.new("RGB", (FRAME_W, PH2), (6, 6, 8))
band.paste(kept, ((FRAME_W - kept.width) // 2, 0))
c2.paste(band, (107, y2))
d2.text((22, y2 + PH2 + 16), "同一个 4:3 画面，两种缩放方式的结果", font=F(REG, 22), fill=(126, 132, 148))
c2.save(os.path.join(OUT, "scaling.jpg"), quality=90, optimize=True)
print("scaling.jpg ok")
