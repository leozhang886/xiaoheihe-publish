"""10/28 三篇封面：预购数据（真实截图）、无畏契约（官方海报配色）、启动器（自制）。"""
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

def from_photo(src, out, tag, l1, l2, sub, accent, tf, tl, tc):
    base = Image.open(src).convert("RGB")
    sc = max(W/base.width, H/base.height)
    base = base.resize((int(base.width*sc)+1, int(base.height*sc)+1), Image.LANCZOS)
    l = (base.width-W)//2; t = (base.height-H)//2
    base = base.crop((l, t, l+W, t+H))
    veil = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(veil)
    for x in range(W):
        k = max(0.0, 1 - x/(W*0.68))
        vd.line([(x,0),(x,H)], fill=int(228*k**1.1))
    black = Image.new("RGB",(W,H),(8,10,14))
    base = Image.composite(black, base, veil.filter(ImageFilter.GaussianBlur(2)))
    g = Image.new("L",(W,H),0); gd = ImageDraw.Draw(g)
    for y in range(H):
        a = 0
        if y < 140: a = int(140*(1-y/140))
        if y > H-120: a = max(a, int(165*((y-(H-120))/120)))
        gd.line([(0,y),(W,y)], fill=a)
    base = Image.composite(black, base, g)
    d = ImageDraw.Draw(base)
    tf2 = F(REG, 24)
    d.rounded_rectangle([52,40,52+d.textlength(tag,font=tf2)+40,86], 22, fill=tf, outline=tl, width=2)
    d.text((72,50), tag, font=tf2, fill=tc)
    d.text((52,146), l1, font=F(BOLD,52), fill=(246,248,252))
    d.text((52,214), l2, font=F(BOLD,52), fill=accent)
    d.text((52,300), sub, font=F(REG,26), fill=(198,206,220))
    base.save(os.path.join(ROOT,out)); print(out); stamp(out)

def designed(out, tag, l1, l2, big, biglabel, foot, c1, c2):
    img = Image.new("RGB",(W,H),c1); d = ImageDraw.Draw(img)
    for y in range(H):
        k = y/H
        d.line([(0,y),(W,y)], fill=(int(c1[0]+(c2[0]-c1[0])*k), int(c1[1]+(c2[1]-c1[1])*k), int(c1[2]+(c2[2]-c1[2])*k)))
    tf = F(REG,25)
    d.rounded_rectangle([58,44,58+d.textlength(tag,font=tf)+42,92], 24, fill=(28,32,44), outline=(70,84,110), width=2)
    d.text((80,55), tag, font=tf, fill=(168,186,216))
    d.text((58,120), l1, font=F(BOLD,54), fill=(240,242,248))
    d.text((58,192), l2, font=F(BOLD,54), fill=(240,190,100))
    if big:
        d.text((58,300), big, font=F(BOLD,120), fill=(250,214,110))
        d.text((58+d.textlength(big,font=F(BOLD,120))+28,430), biglabel, font=F(REG,34), fill=(200,206,220))
    d.text((58,H-46), foot, font=F(REG,25), fill=(140,146,162))
    img.save(os.path.join(ROOT,out)); print(out); stamp(out)

# 1 预购数据：用官方截图
from_photo(os.path.join(ROOT,"news-pbz","shot2.jpg"), "cover-pbz-data.png",
  "10 月 29 日发售 · AlineaAnalytics",
  "85 万份预购", "六成来自大中华区",
  "Steam 上 76% 是中国玩家买的",
  (250,200,110), (44,32,18), (118,88,40), (240,210,140))

# 2 无畏契约
designed("cover-valorant.png", "腾讯 · 端游国服",
  "一亿人注册了", "这游戏凭什么",
  "1 亿", "端游，不是手游",
  "注册不等于活跃", (16,14,30), (40,22,58))

# 3 启动器
designed("cover-launcher.png", "PC · 平台套娃",
  "玩个游戏", "得装五个启动器",
  "5", "个平台，还互相嵌套",
  "Steam 版也要过别人的登录", (12,14,22), (26,30,44))
