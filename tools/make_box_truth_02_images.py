"""生成《盒友大实话 02》的两张原创观点配图。"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)
REGULAR = "C:/Windows/Fonts/msyh.ttc"
BOLD = "C:/Windows/Fonts/msyhbd.ttc"
W, H = 1200, 675


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


def canvas():
    im = Image.new("RGB", (W, H), "#101522")
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=(int(16 + t * 9), int(21 + t * 9), int(34 + t * 11)))
    d.rounded_rectangle((32, 32, W - 32, H - 32), radius=38, outline="#344055", width=2)
    d.rounded_rectangle((64, 58, 320, 106), radius=20, fill="#233048")
    d.text((84, 68), "盒友大实话  02", font=font(23, True), fill="#a9c6f7")
    return im, d


im, d = canvas()
d.text((64, 151), "难度选简单", font=font(80, True), fill="#f7f4ee")
d.text((64, 260), "丢人吗？", font=font(76, True), fill="#ffbe6d")
choices = [(67, "简单", True), (331, "普通", False), (595, "困难", False), (859, "最高难度", False)]
for x, text, active in choices:
    d.rounded_rectangle((x, 421, x + 247, 537), radius=23,
                        fill="#2e614f" if active else "#273142",
                        outline="#8ee0a6" if active else "#526074", width=3)
    tw = d.textlength(text, font=font(37, True))
    d.text((x + (247 - tw) / 2, 451), text, font=font(37, True),
           fill="#c9f4d4" if active else "#aebbd0")
d.text((66, 590), "自己掏钱买的游戏，难度还要别人批准？", font=font(28), fill="#aebbd0")
im.save(OUT / "cover-box-truth-02.png")

im, d = canvas()
d.text((64, 153), "两种玩法，都能玩得认真", font=font(58, True), fill="#f7f4ee")
d.rounded_rectangle((64, 281, 565, 525), radius=26, fill="#463337", outline="#ad786f", width=2)
d.rounded_rectangle((635, 281, 1136, 525), radius=26, fill="#29483f", outline="#75a891", width=2)
d.text((101, 315), "高难度", font=font(41, True), fill="#ffbaa0")
d.text((101, 391), "练招、复盘、打赢", font=font(37), fill="#f7f4ee")
d.text((672, 315), "简单难度", font=font(41, True), fill="#b4e9ce")
d.text((672, 391), "探索、支线、剧情", font=font(37), fill="#f7f4ee")
d.text((65, 586), "难度菜单不是玩家资格证", font=font(32, True), fill="#aebbd0")
im.save(OUT / "box-truth-02-two-ways.png")

for name in ("cover-box-truth-02.png", "box-truth-02-two-ways.png"):
    print(name, Image.open(OUT / name).size)
