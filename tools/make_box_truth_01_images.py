"""为《盒友大实话 01》生成三张不借用游戏画面的观点配图。"""

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
    d.rounded_rectangle((64, 58, 310, 106), radius=20, fill="#233048")
    d.text((84, 68), text, font=font(23, True), fill="#a9c6f7")


im, d = base()
label(d, "盒友大实话  01")
d.text((64, 152), "3A 游戏卖三四百", font=font(70, True), fill="#f7f4ee")
d.text((64, 251), "首发到底买到了什么？", font=font(56, True), fill="#ffb85c")
d.rounded_rectangle((65, 388, 755, 555), radius=24, fill="#1d293c", outline="#4a5c78", width=2)
d.text((98, 414), "年度神作", font=font(43, True), fill="#aee0b9")
d.text((98, 483), "还是大型付费测试？", font=font(39, True), fill="#f49b95")
d.rounded_rectangle((863, 333, 1065, 527), radius=22, fill="#ebad55", outline="#ffe0a2", width=5)
d.line((964, 333, 964, 527), fill="#bd782d", width=5)
d.polygon(((863, 333), (965, 291), (1065, 333), (964, 375)), fill="#ffd17a")
d.text((934, 397), "?", font=font(94, True), fill="#3b2a1a")
d.text((65, 601), "聊价格，也聊首发体验", font=font(24), fill="#9db0cb")
im.save(OUT / "cover-box-truth-01.png")

im, d = base()
label(d, "宣传与首发")
d.text((64, 154), "预告片很炸，开机先排雷？", font=font(60, True), fill="#f7f4ee")
d.rounded_rectangle((64, 280, 566, 532), radius=26, fill="#263b56", outline="#547da8", width=2)
d.rounded_rectangle((634, 280, 1136, 532), radius=26, fill="#493039", outline="#b66c74", width=2)
d.text((102, 310), "发售前", font=font(34, True), fill="#a9c6f7")
d.text((102, 381), "预告片 / 实机演示", font=font(38, True), fill="#f7f4ee")
d.text((672, 310), "发售后", font=font(34, True), fill="#f4ad9f")
d.text((672, 380), "配置 / 优化 / BUG", font=font(38, True), fill="#f7f4ee")
d.line((580, 405, 620, 405), fill="#ffc36e", width=8)
d.polygon(((621, 405), (601, 393), (601, 417)), fill="#ffc36e")
d.text((65, 592), "贵可以，至少把游戏做完整", font=font(30), fill="#b8c7dc")
im.save(OUT / "box-truth-01-launch.png")

im, d = base()
label(d, "首发与等等")
d.text((64, 154), "同一款游戏，两种入手时机", font=font(57, True), fill="#f7f4ee")
d.rounded_rectangle((64, 280, 566, 530), radius=26, fill="#47343a", outline="#a06a75", width=2)
d.rounded_rectangle((634, 280, 1136, 530), radius=26, fill="#2b443f", outline="#699e8d", width=2)
d.text((105, 316), "首发玩家", font=font(42, True), fill="#ffc4a6")
d.text((105, 396), "花全价，先体验", font=font(34), fill="#f7f4ee")
d.text((675, 316), "等等党", font=font(42, True), fill="#b1ead3")
d.text((675, 396), "等折扣、补丁和口碑", font=font(34), fill="#f7f4ee")
d.text((65, 590), "当然，真喜欢的游戏首发也能值", font=font(30), fill="#b8c7dc")
im.save(OUT / "box-truth-01-wait.png")

for name in ("cover-box-truth-01.png", "box-truth-01-launch.png", "box-truth-01-wait.png"):
    print(name, Image.open(OUT / name).size)
