# 生成去 AI 味那篇的两张配图
from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"C:\Users\86153\OneDrive\桌面\自媒体\小黑盒\assets"
os.makedirs(OUT, exist_ok=True)

# 中文粗体 / 常规
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
MONO = r"C:\Windows\Fonts\consola.ttf"

def F(path, size):
    return ImageFont.truetype(path, size)

def wrap_cjk(text, font, max_w, draw):
    """按字符宽度折行（中文没有空格，按字累加）"""
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        t = cur + ch
        if draw.textlength(t, font=font) > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines

# ---------- 1. 封面 ----------
W, H = 1200, 675
img = Image.new("RGB", (W, H), (16, 20, 32))
d = ImageDraw.Draw(img)

# 竖向渐变
top, bot = (20, 26, 44), (10, 12, 20)
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(
        int(top[0] + (bot[0] - top[0]) * k),
        int(top[1] + (bot[1] - top[1]) * k),
        int(top[2] + (bot[2] - top[2]) * k)))

# 左上角标签
tag_f = F(REG, 26)
tag = "GitHub 6 个项目  ·  实测对照"
d.rounded_rectangle([60, 56, 60 + d.textlength(tag, font=tag_f) + 44, 106], 25,
                    fill=(30, 40, 62), outline=(60, 80, 120), width=2)
d.text((82, 68), tag, font=tag_f, fill=(130, 170, 230))

# 主标题：AI 味（带红色删除线）
big = F(BOLD, 150)
t1 = "AI 味"
x1, y1 = 60, 170
d.text((x1, y1), t1, font=big, fill=(230, 235, 245))
w1 = d.textlength(t1, font=big)
d.line([(x1 - 8, y1 + 92), (x1 + w1 + 8, y1 + 92)], fill=(235, 70, 70), width=12)

# 右侧：不是玄学
sub = F(BOLD, 62)
d.text((x1 + w1 + 40, y1 + 46), "不是玄学", font=sub, fill=(120, 130, 150))

# 副标题
s2 = F(REG, 40)
lines = ["12 条特征，逐条给对照",
         "每条都有「差」和「好」两个版本"]
yy = 400
for ln in lines:
    d.text((60, yy), ln, font=s2, fill=(180, 190, 205))
    yy += 62

# 底部小字
s3 = F(REG, 26)
d.text((60, H - 62), "拿去对着自己的稿子改就行", font=s3, fill=(110, 120, 140))

img.save(os.path.join(OUT, "cover-deai.png"))
print("cover-deai.png ok", img.size)

# ---------- 2. 前后对照 ----------
W2, H2 = 1100, 800
img2 = Image.new("RGB", (W2, H2), (250, 250, 252))
d2 = ImageDraw.Draw(img2)

ttl = F(BOLD, 44)
d2.text((60, 48), "同一段话，改前改后", font=ttl, fill=(25, 28, 38))

body = F(REG, 30)
bodyb = F(BOLD, 30)

def panel(y, title, title_color, bg, border, rows):
    """rows: [(文字, 颜色, 是否加粗)]"""
    pad = 34
    h = 40 + len(rows) * 12
    # 预计算高度
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    all_lines = []
    for txt, col, bold in rows:
        f = bodyb if bold else body
        ls = wrap_cjk(txt, f, W2 - 120 - pad * 2, tmp)
        all_lines.append((ls, col, f))
    need = 96 + sum(len(ls) * 46 + 10 for ls, _, _ in all_lines)
    d2.rounded_rectangle([60, y, W2 - 60, y + need], 18, fill=bg, outline=border, width=3)
    # 标题
    d2.text((60 + pad, y + 26), title, font=F(BOLD, 32), fill=title_color)
    cy = y + 92
    for ls, col, f in all_lines:
        for ln in ls:
            d2.text((60 + pad + 4, cy), ln, font=f, fill=col)
            cy += 46
        cy += 10
    return y + need + 34

y = 130
y = panel(
    y, "改前", (190, 60, 60), (255, 246, 246), (240, 200, 200),
    [("先说重点：本体现在 ¥89.40，原价 ¥298，打 3 折。", (60, 60, 70), False),
     ("因为终极版在单品折扣之上又叠了一层捆绑折扣", (190, 60, 60), False),
     ("——单看本体是打 3 折，但终极版是打 4 折。", (190, 60, 60), False)])

y = panel(
    y, "改后", (30, 130, 90), (244, 252, 247), (190, 225, 205),
    [("本体 89 块 4，原价 298，打 3 折。", (40, 45, 55), False),
     ("终极版其实是折上折。本体单看是打 3 折，", (40, 45, 55), False),
     ("但进捆绑包按 4 折算，再叠一层。", (40, 45, 55), False)])

# 底部数据
stat = F(BOLD, 32)
d2.text((60, H2 - 96), "破折号 8 处 → 0    加粗 15 处 → 1", font=stat, fill=(25, 28, 38))

img2.save(os.path.join(OUT, "flow-deai.png"))
print("flow-deai.png ok", img2.size)
