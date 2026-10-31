# 生成「DLSS/FSR/帧生成」那篇的配图
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
OUT = os.path.join(ROOT, "upscale")
os.makedirs(OUT, exist_ok=True)

BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

# ---------- 1. 封面：三层结构 ----------
W, H = 1200, 675
img = Image.new("RGB", (W, H), (11, 14, 21))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(20 - 9 * k), int(26 - 13 * k), int(42 - 22 * k)))

tag = F(REG, 25)
t = "画质设置 · 别再搞混"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(24, 40, 58), outline=(56, 92, 134), width=2)
d.text((80, 55), t, font=tag, fill=(138, 184, 238))

d.text((58, 112), "DLSS、FSR、帧生成", font=F(BOLD, 54), fill=(238, 242, 248))
d.text((58, 178), "不是一个选择题", font=F(BOLD, 54), fill=(238, 242, 248))

# 三层
layers = [
    ("第一层", "超分辨率", "低分辨率渲染，AI 放大", (92, 214, 148)),
    ("第二层", "帧生成", "两帧之间插一张生成的帧", (238, 196, 92)),
    ("第三层", "光追重建 / 神经渲染", "AI 重算光照和材质", (140, 172, 238)),
]
y = 272
for tagtxt, name, note, col in layers:
    d.rounded_rectangle([58, y, W - 58, y + 76], 12, fill=(24, 28, 40), outline=(44, 50, 66), width=2)
    d.text((80, y + 24), tagtxt, font=F(REG, 24), fill=(120, 126, 142))
    d.text((176, y + 18), name, font=F(BOLD, 32), fill=col)
    d.text((176, y + 52), note, font=F(REG, 21), fill=(146, 152, 168))
    y += 88

d.text((58, H - 46), "按顺序开，不是三选一", font=F(REG, 28), fill=(150, 156, 172))
img.save(os.path.join(ROOT, "cover-upscale.png"))
print("cover-upscale.png ok")

# ---------- 2. 超分辨率档位表 ----------
def table(path, title, headers, rows, colw, note=None, rowh=92, w=1100):
    pad = 34
    H0 = 108 + len(rows) * rowh + (56 if note else 0) + pad
    im = Image.new("RGB", (w, H0), (250, 250, 252))
    dr = ImageDraw.Draw(im)
    dr.text((40, 34), title, font=F(BOLD, 42), fill=(22, 26, 36))

    # 表头
    hy = 104
    dr.rectangle([34, hy, w - 34, hy + 56], fill=(236, 238, 244))
    x = 34 + 18
    for i, h in enumerate(headers):
        dr.text((x, hy + 14), h, font=F(BOLD, 26), fill=(60, 66, 80))
        x += colw[i]

    y = hy + 56
    for r_i, row in enumerate(rows):
        if r_i % 2 == 1:
            dr.rectangle([34, y, w - 34, y + rowh], fill=(244, 245, 249))
        x = 34 + 18
        for i, cell in enumerate(row):
            fnt = F(BOLD, 27) if i == 0 else F(REG, 26)
            col = (24, 28, 38) if i == 0 else (66, 72, 88)
            dr.text((x, y + rowh // 2 - 18), cell, font=fnt, fill=col)
            x += colw[i]
        dr.line([(34, y), (w - 34, y)], fill=(228, 230, 238), width=1)
        y += rowh
    dr.line([(34, y), (w - 34, y)], fill=(214, 216, 226), width=3)

    if note:
        dr.text((40, y + 16), note, font=F(REG, 22), fill=(120, 126, 142))
    im.save(path, quality=92, optimize=True)
    print(f"  {os.path.basename(path)}  {im.size}  {os.path.getsize(path)//1024}KB")

table(
    os.path.join(OUT, "tiers.jpg"),
    "超分辨率档位对照",
    ["档位", "内部渲染比例", "4K 屏实际渲染"],
    [
        ["质量", "每边约 66%", "约 1440p"],
        ["平衡", "每边约 58%", "约 2228×1253"],
        ["性能", "每边 50%", "约 1080p"],
        ["超级性能", "每边约 33%", "约 720p"],
    ],
    colw=[220, 340, 400],
    note="各家叫法可能略有不同，比例关系基本一致",
)

table(
    os.path.join(OUT, "summary.jpg"),
    "三层速查",
    ["技术层", "作用", "硬件门槛"],
    [
        ["超分辨率", "低分辨率渲染后 AI 放大", "DLSS：RTX 20 起\nFSR / XeSS：不挑卡"],
        ["帧生成", "两帧之间插入生成的帧", "DLSS：RTX 40 起\n多帧生成：RTX 50 起"],
        ["光追重建", "清掉光追的噪点和闪烁", "看游戏是否支持"],
        ["神经渲染", "AI 重算光照和材质", "官方未公布"],
    ],
    colw=[190, 340, 430],
    note="DLSS 5（神经渲染）的支持显卡名单，NVIDIA 至今没有公布",
    rowh=88,
)
