# 生成「BioWare / 2077 2.5 / 撕裂 / 字幕」四篇的封面
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
            int(c1[0]+(c2[0]-c1[0])*k), int(c1[1]+(c2[1]-c1[1])*k), int(c1[2]+(c2[2]-c1[2])*k)))
    return im, d

def cover(name, tagtxt, l1, l2, rows, foot, c1, c2, tagfill, tagline, tagcol, t1, t2):
    W, H = 1200, 675
    img, d = grad(W, H, c1, c2)
    tag = F(REG, 25)
    d.rounded_rectangle([58, 44, 58 + d.textlength(tagtxt, font=tag) + 42, 92], 24,
                        fill=tagfill, outline=tagline, width=2)
    d.text((80, 55), tagtxt, font=tag, fill=tagcol)
    d.text((58, 122), l1, font=F(BOLD, 56), fill=t1)
    d.text((58, 196), l2, font=F(BOLD, 56), fill=t2)
    y = 300
    for nm, note, col in rows:
        d.rounded_rectangle([58, y, W-58, y+70], 11, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
        d.rounded_rectangle([58, y, 65, y+70], 4, fill=col)
        d.text((88, y+16), nm, font=F(BOLD, 26), fill=col)
        d.text((360, y+21), note, font=F(REG, 23), fill=(150, 156, 172))
        y += 80
    d.text((58, H-42), foot, font=F(REG, 25), fill=(140, 146, 162))
    img.save(os.path.join(ROOT, name))
    print(name)

# A BioWare
cover("cover-bioware.png", "10 月 21 日 · 已多源确认",
      "BioWare 关了", "质量效应也没了",
      [("裁员约 400 人", "全公司，BioWare 约 50 人", (220, 110, 100)),
       ("新质量效应取消", "处于早期开发阶段", (240, 176, 96)),
       ("IP 仍归 EA", "招牌还在，人没了", (150, 160, 180))],
      "源：dotesports / VGC / Shacknews / VRT",
      (16, 12, 18), (34, 18, 22), (44, 28, 32), (110, 68, 72), (230, 160, 160),
      (240, 242, 248), (240, 140, 120))

# B 2077 2.5
cover("cover-cp2075.png", "2077 · 2.5 更新",
      "主机也能装 MOD 了", "这次真正的新闻",
      [("MOD 走 mod.io", "PC / Mac / PS5 / Xbox 都支持", (240, 200, 90)),
       ("Switch 2 延后", "10/22 先上其他平台", (150, 200, 240)),
       ("新增双持手枪", "新技能 Double Trouble", (240, 140, 180))],
      "内容更新是常规操作，MOD 跨平台才是变化",
      (14, 12, 14), (34, 22, 14), (52, 38, 20), (130, 96, 40), (248, 214, 130),
      (240, 242, 248), (250, 210, 90))

# C 撕裂
cover("cover-tearing.png", "显示 · 三个症状别混",
      "撕裂、卡顿、延迟", "根本不是一回事",
      [("撕裂", "画面被切成上下两半", (200, 90, 90)),
       ("卡顿", "帧时间忽快忽慢", (240, 176, 96)),
       ("延迟", "操作慢了半拍", (120, 190, 240))],
      "先认症状，再动手，别在设置里瞎试",
      (12, 14, 22), (20, 26, 40), (26, 34, 56), (62, 92, 132), (150, 184, 226),
      (240, 242, 248), (240, 150, 120))

# D 字幕
cover("cover-subtitle.png", "设置 · 两分钟的事",
      "游戏字幕", "多数人没调过",
      [("字幕大小", "默认是给显示器距离设计的", (120, 190, 240)),
       ("字幕背景", "加一层底，暗场景才看得清", (130, 220, 160)),
       ("音频 / 字幕分设", "可以听英文看中文", (240, 200, 120))],
      "不是给听不清的人用的，是给所有人用的",
      (12, 14, 20), (18, 24, 34), (24, 34, 46), (58, 86, 108), (160, 196, 226),
      (240, 242, 248), (130, 214, 180))
