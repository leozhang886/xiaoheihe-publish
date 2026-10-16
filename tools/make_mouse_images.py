# 生成「鼠标加速」那篇的配图
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\自媒体\小黑盒\assets"
OUT = os.path.join(ROOT, "mouse")
os.makedirs(OUT, exist_ok=True)

BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

# ---------- 1. 封面 ----------
W, H = 1200, 675
img = Image.new("RGB", (W, H), (12, 14, 22))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(22 - 10 * k), int(26 - 14 * k), int(44 - 24 * k)))

tag = F(REG, 25)
t = "鼠标设置 · 一个常见误会"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(44, 30, 44), outline=(104, 70, 108), width=2)
d.text((80, 55), t, font=tag, fill=(214, 154, 220))

d.text((58, 126), "你关的那个鼠标加速", font=F(BOLD, 62), fill=(238, 242, 248))
d.text((58, 208), "可能根本没生效", font=F(BOLD, 62), fill=(240, 110, 100))

# 两条路径小示意
d.line([(58, 336), (W - 58, 336)], fill=(50, 56, 72), width=2)

f1, f2 = F(BOLD, 28), F(REG, 24)
# 路径 A
d.rounded_rectangle([58, 372, 620, 452], 10, fill=(26, 22, 30), outline=(92, 62, 96), width=2)
d.text((80, 386), "走 Windows 指针流程", font=f1, fill=(206, 148, 212))
d.text((80, 420), "← 那个开关只影响这条路", font=f2, fill=(148, 122, 152))
# 路径 B
d.rounded_rectangle([640, 372, 1142, 452], 10, fill=(22, 30, 26), outline=(62, 108, 84), width=2)
d.text((662, 386), "走 raw input", font=f1, fill=(120, 220, 160))
d.text((662, 420), "← 绕开系统，开关管不着", font=f2, fill=(110, 150, 128))

d.text((58, 496), "现在主流 FPS 大多走下面那条", font=F(BOLD, 32), fill=(228, 234, 244))
d.text((58, 548), "所以关完手感一样，不是你的问题", font=F(REG, 29), fill=(154, 160, 176))
d.text((58, H - 44), "真想调加速，得用改 raw input 的工具", font=F(REG, 26), fill=(126, 132, 148))
img.save(os.path.join(ROOT, "cover-mouse.png"))
print("cover-mouse.png ok")

# ---------- 2. 两条路径流程图 ----------
W2, H2 = 1150, 640
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 30), "鼠标输入的两条路", font=F(BOLD, 40), fill=(22, 26, 36))

def box(x, y, w, h, text, sub, fill, outline, tcol, scol):
    dr.rounded_rectangle([x, y, x + w, y + h], 10, fill=fill, outline=outline, width=2)
    dr.text((x + 18, y + 14), text, font=F(BOLD, 25), fill=tcol)
    if sub:
        dr.text((x + 18, y + 48), sub, font=F(REG, 21), fill=scol)

def arrow(x1, y1, x2, y2, col):
    dr.line([(x1, y1), (x2, y2)], fill=col, width=3)
    # 箭头
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 12
    for s in (-1, 1):
        dr.line([(x2, y2), (x2 - L * math.cos(ang - s * 0.45), y2 - L * math.sin(ang - s * 0.45))],
                fill=col, width=3)

# 起点
box(38, 210, 170, 90, "鼠标", "物理移动", (238, 240, 246), (206, 210, 222), (30, 34, 44), (110, 116, 132))

# 上路径：Windows 指针流程
GREY = (150, 154, 168)
box(300, 118, 300, 104, "Windows 指针流程", "含「提高指针精确度」", (250, 244, 250), (208, 178, 212), (150, 92, 158), (150, 108, 156))
box(690, 118, 250, 104, "游戏", "手感受它影响", (238, 240, 246), (206, 210, 222), (30, 34, 44), (110, 116, 132))

# 下路径：raw input
box(300, 300, 300, 104, "raw input", "游戏直接读鼠标数据", (240, 250, 244), (170, 214, 188), (26, 118, 74), (86, 140, 108))
box(690, 300, 250, 104, "游戏", "开关管不着这条路", (238, 240, 246), (206, 210, 222), (30, 34, 44), (110, 116, 132))

arrow(208, 255, 296, 180, GREY)
arrow(208, 255, 296, 344, GREY)
arrow(600, 170, 686, 170, GREY)
arrow(600, 352, 686, 352, GREY)

dr.line([(38, 452), (W2 - 38, 452)], fill=(224, 226, 234), width=2)
dr.text((38, 476), "左边那条路：系统在中间改了数据，所以「手快指针走得远」。", font=F(REG, 24), fill=(70, 76, 92))
dr.text((38, 512), "右边那条路：游戏绕过系统，Windows 那个开关对它没有任何作用。", font=F(REG, 24), fill=(70, 76, 92))
dr.text((38, 560), "想控制加速，就要在右边那条路上动手 —— 比如 Raw Accel（★2,556）。",
        font=F(BOLD, 24), fill=(26, 32, 44))

im.save(os.path.join(OUT, "paths.jpg"), quality=92, optimize=True)
print(f"  paths.jpg  {im.size}  {os.path.getsize(os.path.join(OUT,'paths.jpg'))//1024}KB")
