"""把真实截图做成封面：底部压暗 + 叠标题。新闻稿用这个，保证是真图。"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG = r"C:\Windows\Fonts\msyh.ttc"
def F(p, s): return ImageFont.truetype(p, s)

W, H = 1200, 675


def make(src, out, tag, line1, line2, accent=(240, 190, 90)):
    base = Image.open(src).convert("RGB")
    # 等比铺满再裁 16:9
    sc = max(W / base.width, H / base.height)
    base = base.resize((int(base.width * sc) + 1, int(base.height * sc) + 1), Image.LANCZOS)
    left = (base.width - W) // 2
    top = (base.height - H) // 2
    base = base.crop((left, top, left + W, top + H))

    # 左侧压暗，让文字立起来
    veil = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(veil)
    for x in range(W):
        k = max(0.0, 1 - x / (W * 0.78))
        vd.line([(x, 0), (x, H)], fill=int(232 * k ** 1.15))
    black = Image.new("RGB", (W, H), (6, 8, 12))
    base = Image.composite(black, base, veil.filter(ImageFilter.GaussianBlur(2)))

    # 顶部和底部再压一层，方便放标和落款
    g = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(g)
    for y in range(H):
        a = 0
        if y < 150:
            a = int(150 * (1 - y / 150))
        if y > H - 130:
            a = max(a, int(170 * ((y - (H - 130)) / 130)))
        gd.line([(0, y), (W, y)], fill=a)
    base = Image.composite(black, base, g)

    d = ImageDraw.Draw(base)

    # 标签胶囊
    tagf = F(REG, 24)
    tw = d.textlength(tag, font=tagf)
    d.rounded_rectangle([52, 40, 52 + tw + 40, 86], 22, fill=(20, 18, 16), outline=(120, 96, 48), width=2)
    d.text((72, 50), tag, font=tagf, fill=(246, 214, 140))

    # 标题
    d.text((52, 150), line1, font=F(BOLD, 54), fill=(246, 248, 252))
    d.text((52, 222), line2, font=F(BOLD, 54), fill=accent)

    out_path = os.path.join(ROOT, out)
    base.save(out_path)
    print(out, base.size)


# A. LPL 首轮全败：用真实比赛截图
make(os.path.join(ROOT, "news-lpl", "match-blg-mkoi.png"),
     "cover-lpl-d1.png",
     "S16 瑞士轮 · 10 月 24 日",
     "LPL 首轮全败",
     "四场比分全在这",
     accent=(240, 170, 120))

# B. 2077：用官方双持截图
make(os.path.join(ROOT, "news-cp2077", "dual-wield.jpg"),
     "cover-cp2077-anime.png",
     "2077 · 动画 + 2.5 更新",
     "一部动画",
     "把老游戏又拉起来了",
     accent=(250, 210, 90))
