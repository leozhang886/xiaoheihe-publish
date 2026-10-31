# 生成「HDR」和「Steam 家庭组」两篇的配图
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

def grad(w, h, c1, c2):
    im = Image.new("RGB", (w, h), c1)
    d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=(
            int(c1[0] + (c2[0] - c1[0]) * k),
            int(c1[1] + (c2[1] - c1[1]) * k),
            int(c1[2] + (c2[2] - c1[2]) * k)))
    return im, d


# ==================== A. HDR ====================
W, H = 1200, 675
img, d = grad(W, H, (14, 12, 24), (26, 18, 40))
tag = F(REG, 25)
t = "显示 · 分档的，不是开关"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(38, 28, 58), outline=(96, 72, 130), width=2)
d.text((80, 55), t, font=tag, fill=(196, 168, 236))

d.text((58, 122), "你显示器上的 HDR", font=F(BOLD, 58), fill=(238, 242, 248))
d.text((58, 196), "可能一直开错了", font=F(BOLD, 58), fill=(240, 150, 110))

d.rounded_rectangle([58, 300, 588, 546], radius=16, fill=(26, 22, 34), outline=(80, 56, 88), width=2)
d.text((88, 322), "HDR400", font=F(BOLD, 40), fill=(200, 140, 140))
d.text((88, 384), "对比度只要求 1,300 : 1", font=F(REG, 25), fill=(180, 172, 186))
d.text((88, 424), "普通 IPS 就够", font=F(REG, 25), fill=(180, 172, 186))
d.text((88, 470), "不要求分区背光", font=F(BOLD, 26), fill=(232, 120, 110))

d.rounded_rectangle([612, 300, 1142, 546], radius=16, fill=(18, 30, 26), outline=(52, 96, 76), width=2)
d.text((642, 322), "HDR600 以上", font=F(BOLD, 40), fill=(130, 220, 160))
d.text((642, 384), "对比度 8,000 : 1 起", font=F(REG, 25), fill=(176, 198, 184))
d.text((642, 424), "强制 1D 分区背光", font=F(REG, 25), fill=(176, 198, 184))
d.text((642, 470), "暗部真能黑下去", font=F(BOLD, 26), fill=(120, 220, 150))

d.text((58, 592), "数据来源：VESA DisplayHDR CTS 1.2", font=F(REG, 24), fill=(132, 126, 146))
img.save(os.path.join(ROOT, "cover-hdr.png"))
print("cover-hdr.png ok")

# HDR 分档表
rows = [("400", "1,300 : 1", "不要求", True), ("500", "7,000 : 1", "1D 分区", False),
        ("600", "8,000 : 1", "1D 分区", False), ("1000", "30,000 : 1", "2D 分区", False),
        ("1400", "50,000 : 1", "2D 分区", False)]
W2, rowh = 1150, 72
H2 = 120 + len(rows) * rowh + 90
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 26), "DisplayHDR 分档对比", font=F(BOLD, 38), fill=(22, 26, 36))
dr.text((38, 74), "门槛在对比度，不在亮度数字", font=F(REG, 21), fill=(126, 132, 148))
y = 120
dr.text((60, y - 4), "档位", font=F(BOLD, 20), fill=(120, 126, 142))
dr.text((240, y - 4), "静态对比度要求", font=F(BOLD, 20), fill=(120, 126, 142))
dr.text((620, y - 4), "分区背光", font=F(BOLD, 20), fill=(120, 126, 142))
y += 30
for tier, cr, dim, warn in rows:
    bg = (253, 238, 236) if warn else (255, 255, 255)
    dr.rectangle([38, y, W2 - 38, y + rowh - 6], fill=bg, outline=(228, 230, 238))
    col = (200, 80, 76) if warn else (40, 46, 58)
    dr.text((60, y + 16), "HDR" + tier, font=F(BOLD, 26), fill=col)
    dr.text((240, y + 16), cr, font=F(BOLD, 26), fill=col)
    dr.text((620, y + 16), dim, font=F(REG, 24), fill=(90, 96, 112))
    if warn:
        dr.text((880, y + 18), "← 入门级，别期待", font=F(BOLD, 22), fill=(200, 80, 76))
    y += rowh
dr.text((38, y + 14), "数据来源：VESA DisplayHDR CTS 1.2 官方汇总表", font=F(REG, 21), fill=(126, 132, 148))
im.save(os.path.join(ROOT, "hdr-tiers.jpg"), quality=92, optimize=True)
print(f"  hdr-tiers.jpg  {im.size}")


# ==================== D. Steam 家庭组 ====================
img, d = grad(W, H, (12, 14, 22), (18, 26, 38))
t = "Steam · 家庭组的真实规则"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(24, 34, 48), outline=(60, 88, 120), width=2)
d.text((80, 55), t, font=tag, fill=(150, 184, 226))

d.text((58, 122), "六个人，一个库", font=F(BOLD, 58), fill=(238, 242, 248))
d.text((58, 196), "规则比你想的多", font=F(BOLD, 58), fill=(120, 190, 240))

facts = [
    ("最多 6 人", "不是随便拉的群", (120, 190, 240)),
    ("离开要等 1 年", "从加入那天起算", (240, 176, 96)),
    ("位置冷却 1 年", "有人退了，位子空一年", (240, 176, 96)),
    ("同一游戏要两份", "才能两人同时玩", (130, 220, 160)),
]
y = 300
for name, note, col in facts:
    d.rounded_rectangle([58, y, W - 58, y + 66], 11, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
    d.rounded_rectangle([58, y, 65, y + 66], 4, fill=col)
    d.text((88, y + 16), name, font=F(BOLD, 28), fill=col)
    d.text((400, y + 21), note, font=F(REG, 23), fill=(150, 156, 172))
    y += 76

d.text((58, H - 42), "依据：Steam 官方 Families 用户指南与 FAQ", font=F(REG, 23), fill=(132, 138, 154))
img.save(os.path.join(ROOT, "cover-steam-family.png"))
print("cover-steam-family.png ok")

# 家庭组：能共享 / 不能共享
no_share = [
    "需要第三方 key / 账号 / 订阅的",
    "免费游戏，以及它们的 DLC",
    "在某一方地区受限的",
    "不支持对方操作系统的",
    "发行商标记为不可共享的",
    "原主标记为私密的",
]
W3 = 1150
H3 = 150 + len(no_share) * 58 + 150
im = Image.new("RGB", (W3, H3), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 26), "哪些游戏共享不了", font=F(BOLD, 38), fill=(22, 26, 36))
dr.text((38, 76), "Steam 官方 FAQ 列出的六类", font=F(REG, 21), fill=(126, 132, 148))
y = 122
for item in no_share:
    dr.rounded_rectangle([38, y, W3 - 38, y + 48], 9, fill=(255, 255, 255), outline=(228, 230, 238), width=2)
    dr.ellipse([58, y + 18, 70, y + 30], fill=(208, 84, 80))
    dr.text((86, y + 10), item, font=F(REG, 24), fill=(44, 50, 62))
    y += 58
y += 14
dr.line([(38, y), (W3 - 38, y)], fill=(220, 222, 230), width=2)
y += 20
dr.text((38, y), "同时玩的规则：同一个游戏有几份，就能几个人同时玩", font=F(BOLD, 25), fill=(26, 32, 44))
y += 42
dr.text((38, y), "一个人玩 A 游戏、另一个人玩 B 游戏 —— 只要份数够，没问题。", font=F(REG, 22), fill=(90, 96, 112))
im.save(os.path.join(ROOT, "steam-family-rules.jpg"), quality=92, optimize=True)
print(f"  steam-family-rules.jpg  {im.size}")
