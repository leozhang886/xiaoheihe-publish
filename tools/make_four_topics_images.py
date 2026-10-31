# 生成「延迟 / 加载 / 退款 / 录屏」四篇的配图
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

def cover(name, tagtxt, l1, l2, rows, foot, c1, c2, tagcol, tcol1, tcol2):
    W, H = 1200, 675
    img, d = grad(W, H, c1, c2)
    tag = F(REG, 25)
    d.rounded_rectangle([58, 44, 58 + d.textlength(tagtxt, font=tag) + 42, 92], 24,
                        fill=tagcol[0], outline=tagcol[1], width=2)
    d.text((80, 55), tagtxt, font=tag, fill=tagcol[2])
    d.text((58, 122), l1, font=F(BOLD, 56), fill=tcol1)
    d.text((58, 196), l2, font=F(BOLD, 56), fill=tcol2)
    y = 300
    for nm, note, col in rows:
        d.rounded_rectangle([58, y, W-58, y+70], 11, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
        d.rounded_rectangle([58, y, 65, y+70], 4, fill=col)
        d.text((88, y+16), nm, font=F(BOLD, 27), fill=col)
        d.text((360, y+21), note, font=F(REG, 23), fill=(150, 156, 172))
        y += 80
    d.text((58, H-42), foot, font=F(REG, 25), fill=(140, 146, 162))
    img.save(os.path.join(ROOT, name))
    print(name)

# ---- A 网络延迟 ----
cover("cover-latency.png", "网络 · 三个数决定手感",
      "游戏卡不是网速慢", "是这三个数",
      [("延迟 ping", "操作到服务器再回来", (120, 190, 240)),
       ("抖动 jitter", "延迟稳不稳", (240, 196, 92)),
       ("丢包 loss", "哪怕 1% 也会瞬移", (220, 100, 96))],
      "测速网站只测带宽，不测这三个", (12, 14, 24), (18, 30, 46),
      ((24, 34, 54), (60, 92, 130), (150, 184, 228)), (238, 242, 248), (240, 186, 96))

# ---- B 加载 ----
cover("cover-loading.png", "加载 · 硬盘只是其中一段",
      "换了 SSD 还是慢", "问题不在硬盘",
      [("启动慢", "DRM 验证 + 解密 + 引擎初始化", (240, 176, 96)),
       ("切场景慢", "这才是硬盘的事", (120, 190, 240)),
       ("全都慢", "先看后台在干什么", (200, 150, 40))],
      "加载是 CPU、硬盘、网络叠在一起的结果", (14, 12, 22), (26, 22, 34),
      ((44, 32, 30), (104, 78, 62), (226, 186, 150)), (238, 242, 248), (240, 150, 110))

# ---- C 退款 ----
cover("cover-refund.png", "Steam · 无需理由",
      "退款不用不好意思", "规则比你想的宽松",
      [("两周之内", "从购买日算起", (120, 190, 240)),
       ("2 小时以内", "累计游玩时长", (240, 196, 92)),
       ("超了也能提", "Valve 酌情处理", (130, 220, 160))],
      "官方原文：「无需理由」", (12, 16, 24), (20, 30, 40),
      ((24, 36, 34), (58, 96, 80), (146, 214, 172)), (238, 242, 248), (140, 220, 170))

# ---- D 录屏 ----
cover("cover-recording.png", "录屏 · 自带 vs OBS",
      "系统自带的录屏", "其实够用了",
      [("录几十秒", "Win+Alt+R，够", (130, 220, 160)),
       ("后台回溯", "事后按一下就存下", (120, 190, 240)),
       ("录桌面 / 长时间", "这时候才需要 OBS", (240, 176, 96))],
      "别为录三十秒装一个要配半小时的软件", (12, 14, 22), (22, 24, 36),
      ((26, 34, 44), (62, 86, 108), (160, 196, 226)), (238, 242, 248), (150, 200, 240))

# ---- 正文图 1：网络三个数 ----
W2, H2 = 1150, 560
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 26), "三个数，分别管什么", font=F(BOLD, 38), fill=(22, 26, 36))
rows = [
    ("延迟 ping", "操作到服务器再回来的毫秒数", "50ms 以内舒服，100ms 以上明显", (72, 146, 224)),
    ("抖动 jitter", "延迟稳不稳，会不会突然跳", "比延迟更伤人", (200, 150, 40)),
    ("丢包 loss", "数据包在路上丢没丢", "1% 就能让你瞬移", (200, 80, 76)),
]
y = 100
for nm, what, why, col in rows:
    dr.rounded_rectangle([38, y, W2-38, y+104], 12, fill=(255, 255, 255), outline=(224, 226, 234), width=2)
    dr.rounded_rectangle([38, y, 46, y+104], 4, fill=col)
    dr.text((70, y+16), nm, font=F(BOLD, 26), fill=col)
    dr.text((70, y+56), what, font=F(REG, 21), fill=(110, 116, 132))
    dr.text((660, y+38), why, font=F(BOLD, 22), fill=(40, 46, 58))
    y += 114
dr.line([(38, y+6), (W2-38, y+6)], fill=(220, 222, 230), width=2)
dr.text((38, y+26), "测速网站只测带宽 —— 这三个数它都不报", font=F(BOLD, 23), fill=(26, 32, 44))
im.save(os.path.join(ROOT, "latency-three.jpg"), quality=92, optimize=True)
print("latency-three.jpg")

# ---- 正文图 2：退款条件速查 ----
W3 = 1150
items = [
    ("普通游戏", "14 天内 + 游玩不超过 2 小时", (72, 146, 224)),
    ("DLC", "14 天内 + 本体运行不超过 2 小时", (120, 176, 120)),
    ("预购（发行前不可玩）", "发行前随时可退", (200, 150, 40)),
    ("抢先体验", "时长全部计入 2 小时", (200, 80, 76)),
    ("游戏内购", "Valve 自家 48 小时内", (150, 110, 210)),
    ("钱包充值", "14 天内且未使用", (110, 150, 190)),
]
H3 = 120 + len(items)*64 + 76
im = Image.new("RGB", (W3, H3), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 26), "各种情况下的退款条件", font=F(BOLD, 38), fill=(22, 26, 36))
dr.text((38, 74), "整理自 Steam 官方退款页面", font=F(REG, 21), fill=(126, 132, 148))
y = 116
for k, v, col in items:
    dr.rounded_rectangle([38, y, W3-38, y+54], 9, fill=(255, 255, 255), outline=(228, 230, 238), width=2)
    dr.rounded_rectangle([38, y, 45, y+54], 4, fill=col)
    dr.text((68, y+14), k, font=F(BOLD, 22), fill=(32, 38, 50))
    dr.text((420, y+16), v, font=F(REG, 21), fill=(90, 96, 112))
    y += 64
dr.text((38, y+12), "超出条件也能提交，Valve 会酌情处理", font=F(BOLD, 23), fill=(26, 32, 44))
im.save(os.path.join(ROOT, "refund-conditions.jpg"), quality=92, optimize=True)
print("refund-conditions.jpg")
