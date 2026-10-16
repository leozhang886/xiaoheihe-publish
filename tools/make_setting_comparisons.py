# 生成六个设置的「开 / 关」对比图
# 底图：真实游戏截图（天国拯救2 库滕堡集市）
# 效果：按各选项的光学/渲染原理在底图上模拟，用于直观对比
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = r"C:\Users\86153\OneDrive\桌面\自媒体\小黑盒\assets\kcd2\ss8.jpg"
OUT = r"C:\Users\86153\OneDrive\桌面\自媒体\小黑盒\assets\settings"
os.makedirs(OUT, exist_ok=True)

BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG  = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

# 统一的取景：能同时看到近处摊位、中景人物、远处尖塔
PW, PH = 1200, 420
base = Image.open(SRC).convert("RGB").crop((0, 150, 1920, 820)).resize((PW, PH), Image.LANCZOS)

# ---------- 各种效果 ----------
def motion_blur(im, dist=14, samples=11):
    """水平方向运动模糊：把多张横向偏移的图叠起来平均"""
    a = np.asarray(im).astype(np.float32)
    acc = np.zeros_like(a)
    for i in range(samples):
        off = int((i / (samples - 1) - 0.5) * dist * 2)
        acc += np.roll(a, off, axis=1)
    return Image.fromarray((acc / samples).astype(np.uint8))

def film_grain(im, strength=26):
    a = np.asarray(im).astype(np.float32)
    rng = np.random.default_rng(7)
    n = rng.normal(0, strength, a.shape[:2])[..., None]
    # 颗粒在暗部更明显
    lum = a.mean(axis=2, keepdims=True) / 255.0
    n = n * (1.25 - 0.7 * lum)
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))

def chromatic_aberration(im, amount=0.0075):
    """径向色差：红通道放大一点、蓝通道缩小一点，越靠边缘越明显"""
    w, h = im.size
    r, g, b = im.split()
    def scale(ch, k):
        s = int(w * (1 + k)), int(h * (1 + k))
        z = ch.resize(s, Image.LANCZOS)
        left = (z.width - w) // 2
        top = (z.height - h) // 2
        return z.crop((left, top, left + w, top + h))
    return Image.merge("RGB", (scale(r, amount), g, scale(b, -amount)))

def vignette(im, strength=0.78):
    w, h = im.size
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = (w - 1) / 2, (h - 1) / 2
    d = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / np.sqrt(2)
    mask = 1 - strength * np.clip(d, 0, 1) ** 2
    a = np.asarray(im).astype(np.float32) * mask[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def depth_of_field(im, focus_top=0.52, focus_bot=0.78, radius=9):
    """只保留一条水平焦平面清晰，上下虚化"""
    h = im.size[1]
    blurred = im.filter(ImageFilter.GaussianBlur(radius))
    grad = np.zeros((h, 1), dtype=np.float32)
    t0, t1 = int(h * focus_top), int(h * focus_bot)
    for y in range(h):
        if t0 <= y <= t1:
            grad[y] = 0.0
        else:
            d = (t0 - y) if y < t0 else (y - t1)
            grad[y] = min(1.0, d / max(1, int(h * 0.20)))
    m = np.repeat(grad, im.size[0], axis=1)[..., None]
    a = np.asarray(im).astype(np.float32)
    b = np.asarray(blurred).astype(np.float32)
    return Image.fromarray(np.clip(a * (1 - m) + b * m, 0, 255).astype(np.uint8))

def narrow_fov(im, zoom=1.5):
    w, h = im.size
    cw, ch = int(w / zoom), int(h / zoom)
    left, top = (w - cw) // 2, (h - ch) // 2
    return im.crop((left, top, left + cw, top + ch)).resize((w, h), Image.LANCZOS)

# ---------- 拼图 ----------
def pair(name, on_img, off_img, on_label="默认（开）", off_label="关掉之后", note=""):
    pad, gap = 22, 74
    W = PW + pad * 2
    H = pad + 40 + PH + 30 + PH + 40 + (34 if note else 0) + pad
    canvas = Image.new("RGB", (W, H), (16, 18, 24))
    d = ImageDraw.Draw(canvas)
    fl, fs = F(BOLD, 27), F(REG, 22)

    y = pad
    d.text((pad, y), on_label, font=fl, fill=(232, 96, 90))
    y += 40
    canvas.paste(on_img, (pad, y))
    y += PH + 30
    d.text((pad, y), off_label, font=fl, fill=(92, 214, 148))
    y += 40
    canvas.paste(off_img, (pad, y))
    y += PH + 18
    if note:
        d.text((pad, y), note, font=fs, fill=(126, 132, 148))
    # 存 JPEG，体积比 PNG 小得多（小黑盒要上传）
    out = os.path.join(OUT, name.replace(".png", ".jpg"))
    canvas.save(out, quality=90, optimize=True)
    print(f"  {os.path.basename(out)}  {canvas.size}  {os.path.getsize(out)//1024}KB")

NOTE = "同一张游戏截图上的效果示意，用于对比差异"

print("生成中：")
pair("01-motion-blur.png",   motion_blur(base),  base, "动态模糊 开", "动态模糊 关", NOTE)
pair("02-film-grain.png",    film_grain(base),   base, "胶片颗粒 开", "胶片颗粒 关", NOTE)
pair("03-chromatic.png",     chromatic_aberration(base), base, "色差 开", "色差 关", NOTE)
pair("04-vignette.png",      vignette(base),     base, "暗角 开", "暗角 关", NOTE)
pair("05-dof.png",           base.filter(ImageFilter.GaussianBlur(0)) if False else depth_of_field(base),
                             base, "景深 开（只有焦平面清晰）", "景深 关（全画面清晰）", NOTE)
pair("06-fov.png",           narrow_fov(base),   base, "视野窄（部分主机默认值）", "视野宽（PC 上常见调法）", NOTE)
