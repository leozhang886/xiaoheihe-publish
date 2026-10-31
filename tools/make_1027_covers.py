"""10/27 两篇新闻封面：影之刃零、AL 出局。都用真实截图/照片。"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG = r"C:\Windows\Fonts\msyh.ttc"
PY = r"C:\Users\86153\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
W, H = 1200, 675
TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")

def F(p, s): return ImageFont.truetype(p, s)
def stamp(n):
    subprocess.run([PY, os.path.join(TOOLS, "add_mascot.py"), "--only", n], capture_output=True, text=True)

def cover(src, out, tag, l1, l2, sub, accent, tf_fill, tf_line, tf_col):
    base = Image.open(src).convert("RGB")
    sc = max(W / base.width, H / base.height)
    base = base.resize((int(base.width*sc)+1, int(base.height*sc)+1), Image.LANCZOS)
    l = (base.width - W)//2; t = (base.height - H)//2
    base = base.crop((l, t, l+W, t+H))
    veil = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(veil)
    for x in range(W):
        k = max(0.0, 1 - x/(W*0.68))
        vd.line([(x,0),(x,H)], fill=int(228*k**1.1))
    black = Image.new("RGB", (W, H), (8,10,14))
    base = Image.composite(black, base, veil.filter(ImageFilter.GaussianBlur(2)))
    g = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(g)
    for y in range(H):
        a = 0
        if y < 140: a = int(140*(1-y/140))
        if y > H-120: a = max(a, int(165*((y-(H-120))/120)))
        gd.line([(0,y),(W,y)], fill=a)
    base = Image.composite(black, base, g)
    d = ImageDraw.Draw(base)
    tf = F(REG, 24)
    d.rounded_rectangle([52,40,52+d.textlength(tag,font=tf)+40,86], 22, fill=tf_fill, outline=tf_line, width=2)
    d.text((72,50), tag, font=tf, fill=tf_col)
    d.text((52,146), l1, font=F(BOLD,52), fill=(246,248,252))
    d.text((52,214), l2, font=F(BOLD,52), fill=accent)
    d.text((52,300), sub, font=F(REG,26), fill=(198,206,220))
    base.save(os.path.join(ROOT,out)); print(out); stamp(out)

# A 影之刃零
cover(os.path.join(ROOT,"news-pbz","shot1.jpg"), "cover-pbz.png",
  "10 月 28 日 · ¥268", "影之刃零明天发售",
  "两条硬要求", "SSD 是硬性，最低只标 30 帧",
  (250,200,110), (44,32,18), (118,88,40), (240,210,140))

# B AL 出局
cover(os.path.join(ROOT,"news-lpl","al-out.jpg"), "cover-lpl-al.png",
  "S16 瑞士轮 · 10 月 27 日", "AL 0-3 出局",
  "一号种子的魔咒", "瑞士轮改制后首支 0-3 的 LPL 队",
  (232,140,130), (44,24,26), (110,60,62), (226,150,148))
