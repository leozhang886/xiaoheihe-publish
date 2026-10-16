# 生成「单机游戏凭什么要我联网」的封面
from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"C:\Users\86153\OneDrive\桌面\自媒体\小黑盒\assets"
os.makedirs(OUT, exist_ok=True)
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

W, H = 1200, 675
img = Image.new("RGB", (W, H), (14, 16, 24))
d = ImageDraw.Draw(img)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(26 - 14 * k), int(30 - 16 * k), int(44 - 24 * k)))

# 顶部标签
tag = F(REG, 26)
t = "Denuvo 新机制 · 单机模式"
d.rounded_rectangle([60, 52, 60 + d.textlength(t, font=tag) + 44, 102], 25,
                    fill=(48, 30, 30), outline=(130, 70, 62), width=2)
d.text((82, 64), t, font=tag, fill=(240, 150, 138))

# 主视觉：14 天
big = F(BOLD, 190)
d.text((58, 150), "14", font=big, fill=(240, 82, 72))
w14 = d.textlength("14", font=big)
unit = F(BOLD, 84)
d.text((58 + w14 + 18, 240), "天", font=unit, fill=(240, 82, 72))

# 右侧说明
side = F(BOLD, 50)
d.text((58 + w14 + 150, 196), "断网超过这个数", font=side, fill=(232, 236, 244))
d.text((58 + w14 + 150, 262), "单机游戏也打不开", font=side, fill=(232, 236, 244))

# 分隔
d.line([(60, 424), (W - 60, 424)], fill=(58, 62, 76), width=2)

# 底部说明
sub = F(REG, 32)
d.text((60, 460), "而且买的时候，Steam 页面上没写", font=sub, fill=(178, 184, 198))
d.text((60, 512), "NBA 2K25 / 2K26 / 漫威暗夜之子 已被加上这条限制", font=F(REG, 26), fill=(132, 138, 154))

# 右下角小字
d.text((60, H - 58), "单机游戏的启动权，正在被交给服务器", font=F(REG, 27), fill=(108, 114, 130))

img.save(os.path.join(OUT, "cover-online.png"))
print("cover-online.png ok", img.size)
