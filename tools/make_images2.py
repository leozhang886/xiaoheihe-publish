# make_images2.py —— 教程文章的配图
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

OUT = r"C:\Users\86153\xhh\assets"
CN = r"C:\Windows\Fonts\msyh.ttc"
CNB = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    return ImageFont.truetype(CNB if bold else CN, size)


# ============================================================ 封面
# 底图：小黑盒编辑器里排好版的成品
base = Image.open(r"C:\Users\86153\xhh\shots\bg-top.png").convert("RGB")

W, H = 1920, 1080
# cover 方式缩放 + 居中裁剪
r = max(W / base.width, H / base.height)
base = base.resize((int(base.width * r), int(base.height * r)), Image.LANCZOS)
left = (base.width - W) // 2
top = (base.height - H) // 2
cover = base.crop((left, top, left + W, top + H))

# 顶部压暗，保证文字可读
overlay = Image.new("L", (W, H), 0)
od = ImageDraw.Draw(overlay)
for y in range(0, 460):
    od.line([(0, y), (W, y)], fill=int(215 * (1 - y / 460) ** 1.25))
dark = Image.new("RGB", (W, H), (10, 12, 18))
cover = Image.composite(dark, cover, overlay)

d = ImageDraw.Draw(cover)
d.text((80, 78), "用 AI 写小黑盒帖子", font=font(84, True), fill=(255, 255, 255))
d.text((84, 196), "提示词我调好了，直接抄 · 排版零手改", font=font(38), fill=(198, 214, 240))

# 左下角小标签
d.rounded_rectangle([80, H - 132, 470, H - 68], radius=32, fill=(66, 133, 244))
tb = d.textbbox((0, 0), "DeepSeek Harness", font=font(30, True))
d.text((80 + (390 - (tb[2] - tb[0])) / 2, H - 100 - (tb[3] - tb[1]) / 2 - tb[1]),
       "DeepSeek Harness", font=font(30, True), fill=(255, 255, 255))

cover.save(os.path.join(OUT, "cover-ai-write.png"), quality=95)
print("cover-ai-write.png", cover.size)


# ============================================================ 三步流程
FW, FH = 1600, 650
img = Image.new("RGB", (FW, FH), (247, 248, 250))
d = ImageDraw.Draw(img)

d.text((70, 48), "三步用上", font=font(46, True), fill=(26, 30, 38))
d.text((72, 114), "装好 DSH 之后，剩下的就是复制粘贴提示词", font=font(23), fill=(120, 128, 140))

cards = [
    ("1", "装好并启动", "npm i -g @deepseek-ai/dsh\ndsh web", (66, 133, 244)),
    ("2", "把小黑盒的规则喂给它", "复制我给的那段提示词，先发过去", (52, 168, 83)),
    ("3", "让它写，你只管改", "提意见、要标题、让它重排，都行", (251, 140, 0)),
]

cw = (FW - 140 - 2 * 44) // 3
ch = 400
x = 70
for num, title, desc, color in cards:
    d.rounded_rectangle([x, 190, x + cw, 190 + ch], radius=20, fill=(255, 255, 255),
                        outline=(228, 232, 238), width=2)
    d.rounded_rectangle([x, 190, x + cw, 202], radius=6, fill=color)
    d.ellipse([x + 34, 232, x + 96, 294], fill=color)
    nf = font(36, True)
    tb = d.textbbox((0, 0), num, font=nf)
    d.text((x + 65 - (tb[2] - tb[0]) / 2, 263 - (tb[3] - tb[1]) / 2 - tb[1]), num, font=nf, fill=(255, 255, 255))

    # 标题换行
    tf = font(31, True)
    y = 330
    line = ""
    for chx in title:
        if d.textlength(line + chx, font=tf) > cw - 68:
            d.text((x + 34, y), line, font=tf, fill=(26, 30, 38))
            y += 44
            line = chx
        else:
            line += chx
    if line:
        d.text((x + 34, y), line, font=tf, fill=(26, 30, 38))
    y += 56

    for ln in desc.split("\n"):
        d.text((x + 34, y), ln, font=font(21), fill=(118, 126, 138))
        y += 34
    x += cw + 44

img.save(os.path.join(OUT, "flow-ai-write.png"), quality=95)
print("flow-ai-write.png", img.size)

print("\n" + "=" * 40)
for f in sorted(os.listdir(OUT)):
    if f.startswith(("cover-ai", "flow-ai")):
        print(f"  {f}  {os.path.getsize(os.path.join(OUT, f))//1024}KB")
