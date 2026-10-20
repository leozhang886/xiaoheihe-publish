# 生成「游戏体积」那篇的配图
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

# ---------- 封面 ----------
W, H = 1200, 675
img = Image.new("RGB", (W, H), (12, 14, 22))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(22 - 10 * k), int(26 - 14 * k), int(44 - 24 * k)))

tag = F(REG, 25)
t = "体积 · 拆开看才省得下"
d.rounded_rectangle([58, 44, 58 + d.textlength(t, font=tag) + 42, 92], 24,
                    fill=(24, 34, 50), outline=(58, 88, 126), width=2)
d.text((80, 55), t, font=tag, fill=(146, 182, 232))

d.text((58, 122), "100G 都算小了", font=F(BOLD, 64), fill=(238, 242, 248))
d.text((58, 200), "里面都是些什么", font=F(BOLD, 64), fill=(240, 186, 96))

# 体积构成条
d.line([(58, 310), (W - 58, 310)], fill=(50, 56, 72), width=2)
f1, f2 = F(BOLD, 26), F(REG, 22)
items = [
    ("未压缩音频", "多语言配音全在", (96, 168, 232)),
    ("4K 纹理", "开高画质的代价", (168, 146, 232)),
    ("预渲染过场", "一段视频几个 G", (232, 152, 120)),
    ("重复资源", "拿空间换加载速度", (120, 200, 152)),
    ("没做 PC 精简", "主机资源整套搬", (200, 200, 120)),
]
y = 340
for name, note, col in items:
    d.rounded_rectangle([58, y, W - 58, y + 54], 9, fill=(22, 26, 38), outline=(42, 48, 64), width=2)
    d.rounded_rectangle([58, y, 65, y + 54], 4, fill=col)
    d.text((84, y + 13), name, font=f1, fill=col)
    d.text((330, y + 17), note, font=f2, fill=(158, 164, 180))
    y += 62

d.text((58, H - 42), "省空间的正道：透明压缩，不是删文件", font=F(REG, 26), fill=(140, 146, 162))
img.save(os.path.join(ROOT, "cover-gamesize.png"))
print("cover-gamesize.png ok")

# ---------- 正文图：压缩前后 + 能不能压 ----------
W2, H2 = 1150, 690
im = Image.new("RGB", (W2, H2), (250, 250, 252))
dr = ImageDraw.Draw(im)
dr.text((38, 28), "压缩能省多少", font=F(BOLD, 40), fill=(22, 26, 36))
dr.text((38, 78), "数据来自 CompactGUI 官方 README（★9,039）", font=F(REG, 21), fill=(126, 132, 148))

# 前后对比条
BX, BY, BW, BH = 300, 130, 560, 58
dr.text((38, BY + 12), "压缩前", font=F(BOLD, 26), fill=(120, 126, 142))
dr.rounded_rectangle([BX, BY, BX + BW, BY + BH], 8, fill=(206, 210, 222))
dr.text((BX + 18, BY + 14), "169 GB", font=F(BOLD, 26), fill=(60, 66, 80))

dr.text((38, BY + 92), "压缩后", font=F(BOLD, 26), fill=(26, 118, 74))
nw = int(BW * 91.2 / 169)
dr.rounded_rectangle([BX, BY + 80, BX + nw, BY + 80 + BH], 8, fill=(72, 186, 132))
dr.text((BX + 18, BY + 94), "91.2 GB", font=F(BOLD, 26), fill=(12, 52, 32))
dr.text((BX + nw + 20, BY + 96), "省 46%", font=F(BOLD, 30), fill=(26, 118, 74))

dr.text((38, 286), "官方举例：《方舟：生存进化》。README 说法是游戏目录最多可缩到 60%",
        font=F(REG, 22), fill=(90, 96, 112))

dr.line([(38, 336), (W2 - 38, 336)], fill=(222, 224, 232), width=2)
dr.text((38, 360), "但这工具不能乱用", font=F(BOLD, 32), fill=(200, 80, 76))

rows = [
    ("能用", "普通游戏目录", (72, 186, 132)),
    ("别用", "用了 DirectStorage 的游戏（Win11）", (200, 80, 76)),
    ("别删", "游戏目录里手删文件", (200, 150, 40)),
]
y = 412
for tag_, text, col in rows:
    dr.rounded_rectangle([38, y, W2 - 38, y + 64], 10, fill=(255, 255, 255), outline=(224, 226, 234), width=2)
    tw = dr.textlength(tag_, font=F(BOLD, 23)) + 28
    dr.rounded_rectangle([54, y + 18, 54 + tw, y + 46], 6, fill=col)
    dr.text((68, y + 20), tag_, font=F(BOLD, 21), fill=(255, 255, 255))
    dr.text((70 + tw + 18, y + 20), text, font=F(REG, 24), fill=(40, 46, 58))
    y += 76

dr.text((38, y + 10), "DirectStorage 直接从 SSD 读资源，硬压过反而要先解压，把优势抵消掉",
        font=F(REG, 21), fill=(120, 126, 142))

im.save(os.path.join(ROOT, "gamesize-breakdown.jpg"), quality=92, optimize=True)
print(f"  gamesize-breakdown.jpg  {im.size}  {os.path.getsize(os.path.join(ROOT,'gamesize-breakdown.jpg'))//1024}KB")
