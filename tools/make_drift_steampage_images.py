# 生成「手柄漂移」和「Steam 页面」两篇的配图
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
            int(c1[0] + (c2[0]-c1[0])*k), int(c1[1] + (c2[1]-c1[1])*k), int(c1[2] + (c2[2]-c1[2])*k)))
    return im, d

W, H = 1200, 675

# ==================== A. 手柄漂移 ====================
img, d = grad(W, H, (14, 12, 22), (30, 16, 26))
tag = F(REG, 25)
t = "手柄 · 修还是换"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(40, 26, 36), outline=(104, 66, 82), width=2)
d.text((80, 55), t, font=tag, fill=(226, 156, 168))

d.text((58, 122), "摇杆松手了", font=F(BOLD, 58), fill=(238, 242, 248))
d.text((58, 196), "人物还在走", font=F(BOLD, 58), fill=(240, 150, 120))

steps = [
    ("① 先测", "静止时轴读数偏不偏 0", (120, 190, 240)),
    ("② 轻则清洁", "异丙醇 + 棉签，成功率不高", (240, 196, 92)),
    ("③ 中则换模块", "看手柄值不值这个价", (240, 176, 96)),
    ("④ 重则换新", "优先霍尔摇杆型号", (130, 220, 160)),
]
y = 306
for name, note, col in steps:
    d.rounded_rectangle([58, y, W - 58, y + 76], 11, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
    d.rounded_rectangle([58, y, 66, y + 76], 4, fill=col)
    d.text((90, y + 12), name, font=F(BOLD, 27), fill=col)
    d.text((90, y + 48), note, font=F(REG, 21), fill=(150, 156, 172))
    y += 86

d.text((58, H - 42), "碳膜是磨坏，霍尔是老化，都不是永久", font=F(REG, 25), fill=(140, 136, 152))
img.save(os.path.join(ROOT, "cover-drift.png"))
print("cover-drift.png ok")

# 漂移诊断图
W2, H2 = 1150, 600
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 26), "静止时轴读数怎么看", font=F(BOLD, 40), fill=(22, 26, 36))
dr.text((38, 76), "手完全松开，看两个轴的值", font=F(REG, 21), fill=(126, 132, 148))

cases = [
    ("读数在 0 附近", "正常", "不用管", (72, 186, 132)),
    ("轻微跳动 ±0.02", "可能只是死区小", "先调游戏里的死区", (200, 150, 40)),
    ("稳定偏在非零值", "真漂移", "清洁 → 换模块 → 换新", (200, 80, 76)),
]
y = 128
for read, mean, todo, col in cases:
    dr.rounded_rectangle([38, y, W2 - 38, y + 92], 12, fill=(255, 255, 255), outline=(224, 226, 234), width=2)
    dr.rounded_rectangle([38, y, 46, y + 92], 4, fill=col)
    dr.text((70, y + 16), read, font=F(BOLD, 26), fill=col)
    dr.text((70, y + 56), mean, font=F(REG, 21), fill=(110, 116, 132))
    dr.text((640, y + 32), todo, font=F(BOLD, 23), fill=(40, 46, 58))
    y += 102

dr.line([(38, y + 8), (W2 - 38, y + 8)], fill=(220, 222, 230), width=2)
dr.text((38, y + 30), "测试工具：gamepad.js（★561，网页版，免安装）", font=F(BOLD, 23), fill=(26, 32, 44))
im.save(os.path.join(ROOT, "drift-diagnosis.jpg"), quality=92, optimize=True)
print("  drift-diagnosis.jpg")

# ==================== D. Steam 页面 ====================
img, d = grad(W, H, (12, 14, 22), (20, 26, 38))
t = "Steam · 买之前扫这几行"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(24, 34, 48), outline=(60, 88, 120), width=2)
d.text((80, 55), t, font=tag, fill=(150, 184, 226))

d.text((58, 122), "截图和视频可以跳过", font=F(BOLD, 54), fill=(238, 242, 248))
d.text((58, 190), "中间那些小字要看", font=F(BOLD, 54), fill=(240, 186, 96))

traps = [
    ("评价摘要", "默认是全部评价，不是最近", (200, 90, 90)),
    ("抢先体验", "看它待了几年", (200, 150, 40)),
    ("第三方账号", "锁不锁区", (240, 176, 96)),
    ("DLC 数量", "本体便宜可能只是诱饵", (120, 190, 240)),
]
y = 300
for name, note, col in traps:
    d.rounded_rectangle([58, y, W - 58, y + 70], 11, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
    d.rounded_rectangle([58, y, 65, y + 70], 4, fill=col)
    d.text((86, y + 16), name, font=F(BOLD, 27), fill=col)
    d.text((330, y + 21), note, font=F(REG, 23), fill=(150, 156, 172))
    y += 80

d.text((58, H - 42), "这两分钟，能省下不少冤枉钱", font=F(REG, 26), fill=(140, 146, 162))
img.save(os.path.join(ROOT, "cover-steam-page.png"))
print("cover-steam-page.png ok")

# 速查清单图
W3 = 1150
items = [
    ("评价摘要", "点进去看「最近评测」，别只看总数"),
    ("抢先体验", "点开开发者说明，看进了多久"),
    ("此游戏需要第三方账号", "先查那个平台锁不锁区"),
    ("标签", "看标签和最近评测对不对得上"),
    ("DLC 数量", "数一下，本体可能只是入口"),
    ("捆绑包", "看实付价格，别看折扣百分比"),
    ("系统需求", "看推荐配置，还要看它写于哪一年"),
    ("最近更新", "最后一条是两年前就别指望了"),
]
H3 = 130 + len(items) * 62 + 70
im = Image.new("RGB", (W3, H3), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 26), "两分钟速查清单", font=F(BOLD, 40), fill=(22, 26, 36))
dr.text((38, 76), "从上到下扫一遍，两分钟够了", font=F(REG, 21), fill=(126, 132, 148))
y = 122
for i, (k, v) in enumerate(items, 1):
    dr.rounded_rectangle([38, y, W3 - 38, y + 52], 9, fill=(255, 255, 255), outline=(228, 230, 238), width=2)
    dr.ellipse([52, y + 14, 76, y + 38], fill=(72, 146, 224))
    dr.text((58, y + 16), str(i), font=F(BOLD, 18), fill=(255, 255, 255))
    dr.text((92, y + 13), k, font=F(BOLD, 22), fill=(32, 38, 50))
    dr.text((420, y + 15), v, font=F(REG, 21), fill=(90, 96, 112))
    y += 62
dr.text((38, y + 10), "没有第三方工具能替你扫，只能养成习惯", font=F(BOLD, 23), fill=(26, 32, 44))
im.save(os.path.join(ROOT, "steam-page-checklist.jpg"), quality=92, optimize=True)
print("  steam-page-checklist.jpg")
