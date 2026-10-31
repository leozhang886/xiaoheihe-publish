"""给所有封面右下角加一个吉祥物贴纸。

用法:
    python tools/add_mascot.py --test          # 只处理一张，出试样
    python tools/add_mascot.py                 # 处理全部 cover-*.png

做法: 素材是白底贴纸，直接抠白会把裙子上的白也抠掉，所以保留白底，
裁到内容边缘 + 圆角 + 细边框，做成「贴纸卡片」贴在右下角。
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
MASCOT = os.path.join(ROOT, "_mascot.jpg")

# 贴纸在封面上的宽度（占封面宽度的比例）和外边距
STICKER_W_RATIO = 0.20
MARGIN = 22
CORNER = 18


def trim_white(im, thresh=247):
    """裁掉四周接近纯白的外边，但保留贴纸本身的白色描边。"""
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    # 从四边往里找第一列/行有非白像素的位置
    left = 0
    while left < w and all(px[left, y] >= thresh for y in range(0, h, 3)):
        left += 1
    right = w - 1
    while right > left and all(px[right, y] >= thresh for y in range(0, h, 3)):
        right -= 1
    top = 0
    while top < h and all(px[x, top] >= thresh for x in range(0, w, 3)):
        top += 1
    bottom = h - 1
    while bottom > top and all(px[x, bottom] >= thresh for x in range(0, w, 3)):
        bottom -= 1
    # 留一点内边距，让白色描边完整
    pad = 8
    return im.crop((max(0, left - pad), max(0, top - pad),
                    min(w, right + pad + 1), min(h, bottom + pad + 1)))


def make_sticker(target_w):
    im = Image.open(MASCOT).convert("RGB")
    im = trim_white(im)
    # 缩放到目标宽度
    ratio = target_w / im.width
    im = im.resize((target_w, int(im.height * ratio)), Image.LANCZOS)

    # 圆角遮罩
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, im.width - 1, im.height - 1), radius=CORNER, fill=255)

    sticker = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sticker.paste(im, (0, 0), mask)

    # 细边框
    border = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle(
        (0, 0, im.width - 1, im.height - 1), radius=CORNER,
        outline=(255, 255, 255, 210), width=2)
    sticker = Image.alpha_composite(sticker, border)
    return sticker


def add_to(cover_path, sticker, shadow=True):
    base = Image.open(cover_path).convert("RGBA")
    sw, sh = sticker.size

    # 放右上角：标题都在左侧，右上角在现有封面上都是空的，不会压内容
    x = base.width - sw - MARGIN
    y = MARGIN

    if shadow:
        sh_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        mask = Image.new("L", (sw, sh), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, sw - 1, sh - 1), radius=CORNER, fill=140)
        sh_layer.paste(Image.new("RGBA", (sw, sh), (0, 0, 0, 255)),
                       (x + 4, y + 5), mask)
        sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(6))
        base = Image.alpha_composite(base, sh_layer)

    base.paste(sticker, (x, y), sticker)
    return base.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true", help="只处理一张，出试样")
    ap.add_argument("--only", default=None,
                    help="只处理指定的这一张（文件名），避免重复盖章")
    args = ap.parse_args()

    if args.only:
        covers = [args.only]
    elif args.test:
        covers = ["cover-bioware.png"]
    else:
        covers = sorted(f for f in os.listdir(ROOT)
                        if f.startswith("cover-") and f.endswith(".png"))

    for name in covers:
        path = os.path.join(ROOT, name)
        img = Image.open(path)
        target_w = int(img.width * STICKER_W_RATIO)
        sticker = make_sticker(target_w)
        out = add_to(path, sticker)
        if args.test:
            outf = os.path.join(ROOT, "_test_mascot.png")
        else:
            outf = path
        out.save(outf, quality=95)
        print(f"{name}  {img.size}  sticker={sticker.size}")

    print(f"\n共处理 {len(covers)} 张")


if __name__ == "__main__":
    main()
