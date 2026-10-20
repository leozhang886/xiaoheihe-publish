# 生成「全屏 vs 无边框」那篇的配图
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

# ---------- 封面 ----------
W, H = 1200, 675
img = Image.new("RGB", (W, H), (11, 14, 21))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(20 - 9 * k), int(26 - 13 * k), int(42 - 22 * k)))

tag = F(REG, 25)
t = "显示模式 · 三种，不是三种排版"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(26, 36, 54), outline=(62, 92, 132), width=2)
d.text((80, 55), t, font=tag, fill=(146, 182, 232))

d.text((58, 122), "全屏 还是", font=F(BOLD, 60), fill=(238, 242, 248))
d.text((58, 196), "无边框窗口", font=F(BOLD, 60), fill=(240, 186, 96))

modes = [
    ("独占全屏", "延迟最低，VRR 最可靠", "Alt+Tab 会闪黑", (120, 220, 160)),
    ("无边框窗口", "切换无感，多屏友好", "多一道合成", (240, 196, 92)),
    ("窗口化", "除非有特殊理由", "不用考虑", (150, 156, 172)),
]
y = 296
for name, good, bad, col in modes:
    d.rounded_rectangle([58, y, W - 58, y + 76], 11, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
    d.rounded_rectangle([58, y, 65, y + 76], 4, fill=col)
    d.text((86, y + 12), name, font=F(BOLD, 30), fill=col)
    d.text((300, y + 18), good, font=F(REG, 22), fill=(170, 176, 192))
    d.text((700, y + 18), bad, font=F(REG, 22), fill=(126, 132, 148))
    y += 86

d.text((58, H - 44), "别信「一定差 xx 帧」——因游戏而异", font=F(REG, 26), fill=(138, 144, 160))
img.save(os.path.join(ROOT, "cover-displaymode.png"))
print("cover-displaymode.png ok")

# ---------- 正文图：两条渲染路径 ----------
W2, H2 = 1150, 560
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 28), "两条渲染路径", font=F(BOLD, 40), fill=(22, 26, 36))

def box(x, y, w, h, title, sub, fill, outline, tc, sc):
    dr.rounded_rectangle([x, y, x + w, y + h], 10, fill=fill, outline=outline, width=2)
    dr.text((x + 16, y + 12), title, font=F(BOLD, 24), fill=tc)
    if sub:
        dr.text((x + 16, y + 44), sub, font=F(REG, 20), fill=sc)

def arrow(x1, y1, x2, y2, col):
    import math
    dr.line([(x1, y1), (x2, y2)], fill=col, width=3)
    a = math.atan2(y2 - y1, x2 - x1)
    for s in (-1, 1):
        dr.line([(x2, y2), (x2 - 12 * math.cos(a - s * 0.45), y2 - 12 * math.sin(a - s * 0.45))], fill=col, width=3)

GREY = (150, 154, 168)
# 独占全屏
box(38, 108, 170, 80, "游戏", "渲染", (238, 240, 246), (206, 210, 222), (30, 34, 44), (110, 116, 132))
box(300, 108, 260, 80, "直接送显示器", "绕过桌面合成器", (240, 250, 244), (170, 214, 188), (26, 118, 74), (86, 140, 108))
box(650, 108, 460, 80, "路径最短", "延迟低 · VRR 可靠 · 切换成本高", (246, 248, 251), (206, 210, 222), (30, 34, 44), (110, 116, 132))
arrow(210, 148, 296, 148, GREY); arrow(562, 148, 646, 148, GREY)

# 无边框
box(38, 232, 170, 80, "游戏", "渲染到窗口", (238, 240, 246), (206, 210, 222), (30, 34, 44), (110, 116, 132))
box(300, 232, 260, 80, "过桌面合成器", "DWM 再送屏幕", (252, 246, 236), (214, 194, 160), (150, 106, 30), (150, 126, 80))
box(650, 232, 460, 80, "多一道环节", "切换无感 · 但表现因游戏而异", (246, 248, 251), (206, 210, 222), (30, 34, 44), (110, 116, 132))
arrow(210, 272, 296, 272, GREY); arrow(562, 272, 646, 272, GREY)

dr.line([(38, 356), (W2 - 38, 356)], fill=(222, 224, 232), width=2)
dr.text((38, 382), "补丁：新版 Windows 给无边框加了快速路径（独立翻转），有可能接近独占全屏的表现。",
        font=F(REG, 23), fill=(70, 76, 92))
dr.text((38, 418), "但能不能生效，取决于游戏、驱动、显卡设置、有没有叠加层 —— 同一台电脑上不同游戏结果可能不同。",
        font=F(REG, 23), fill=(70, 76, 92))
dr.text((38, 468), "所以：先默认独占全屏，遇到问题再切，切完核对三项（VRR / 帧数 / 延迟）。",
        font=F(BOLD, 24), fill=(26, 32, 44))

im.save(os.path.join(ROOT, "display-mode-paths.jpg"), quality=92, optimize=True)
print(f"  display-mode-paths.jpg  {im.size}  {os.path.getsize(os.path.join(ROOT,'display-mode-paths.jpg'))//1024}KB")
