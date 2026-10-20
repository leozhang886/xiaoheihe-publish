"""为《盒友大实话 03》生成配图。沿用 01 期的视觉规范：
深色渐变底 + 圆角外框 + 左上标签胶囊 + 橙色副标题。"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)
FONT = Path("C:/Windows/Fonts/msyh.ttc")
BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")
W, H = 1200, 675


def font(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else FONT), size)


def base():
    im = Image.new("RGB", (W, H), "#101522")
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=(int(16 + t * 9), int(21 + t * 9), int(34 + t * 11)))
    d.rounded_rectangle((32, 32, W - 32, H - 32), radius=38, outline="#344055", width=2)
    return im, d


def label(d, text):
    d.rounded_rectangle((64, 58, 330, 106), radius=20, fill="#233048")
    d.text((84, 68), text, font=font(23, True), fill="#a9c6f7")


# ---------- 1. 封面 ----------
im, d = base()
label(d, "盒友大实话  03")
d.text((64, 152), "不是玩不动", font=font(76, True), fill="#f7f4ee")
d.text((64, 258), "是买太多", font=font(76, True), fill="#ffb85c")

d.rounded_rectangle((65, 392, 592, 556), radius=24, fill="#1d293c", outline="#4a5c78", width=2)
d.text((98, 418), "买游戏", font=font(40, True), fill="#aee0b9")
d.text((98, 484), "点一下，立刻爽", font=font(34), fill="#f7f4ee")

d.rounded_rectangle((608, 392, 1135, 556), radius=24, fill="#3a2b33", outline="#8c6068", width=2)
d.text((641, 418), "玩游戏", font=font(40, True), fill="#f4ad9f")
d.text((641, 484), "学系统，过教程，先笨拙两小时", font=font(28), fill="#f7f4ee")

d.text((65, 601), "买的不是游戏，是「以后会玩」这个念头", font=font(27), fill="#9db0cb")
im.save(OUT / "cover-box-truth-03.png")

# ---------- 2. 正文图：两种爽不一样 ----------
im, d = base()
label(d, "两种爽")
d.text((64, 148), "买的那一刻 vs 玩的那一刻", font=font(56, True), fill="#f7f4ee")

d.rounded_rectangle((64, 268, 566, 540), radius=26, fill="#1e3448", outline="#4f80ab", width=2)
d.text((104, 300), "买游戏", font=font(44, True), fill="#aee0b9")
for i, line in enumerate(["点一下，付款，结束", "多巴胺又快又便宜", "不需要任何投入"]):
    d.text((104, 380 + i * 48), line, font=font(30), fill="#dfe9f6")

d.rounded_rectangle((634, 268, 1136, 540), radius=26, fill="#43303a", outline="#a76f78", width=2)
d.text((674, 300), "玩游戏", font=font(44, True), fill="#f4ad9f")
for i, line in enumerate(["要学系统、过教程", "要接受前两小时的笨拙", "回报来得慢，但更耐放"]):
    d.text((674, 380 + i * 48), line, font=font(30), fill="#f6e6ea")

d.text((65, 592), "把这两件事分清，就没那么容易失手了", font=font(29), fill="#b8c7dc")
im.save(OUT / "box-truth-03-backlog.png")

for name in ("cover-box-truth-03.png", "box-truth-03-backlog.png"):
    print(name, Image.open(OUT / name).size)
