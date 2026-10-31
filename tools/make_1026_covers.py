"""10/26 四篇的封面：Arkane 和 LPL 用真实图，DDU 和死区自制。"""
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

def news_cover(src, out, tag, l1, l2, sub, accent, tagfill, tagline, tagcol):
    base = Image.open(src).convert("RGB")
    sc = max(W / base.width, H / base.height)
    base = base.resize((int(base.width*sc)+1, int(base.height*sc)+1), Image.LANCZOS)
    l = (base.width - W)//2; t = (base.height - H)//2
    base = base.crop((l, t, l+W, t+H))
    veil = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(veil)
    for x in range(W):
        k = max(0.0, 1 - x/(W*0.68))
        vd.line([(x,0),(x,H)], fill=int(226*k**1.1))
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
    d.rounded_rectangle([52,40,52+d.textlength(tag,font=tf)+40,86], 22, fill=tagfill, outline=tagline, width=2)
    d.text((72,50), tag, font=tf, fill=tagcol)
    d.text((52,146), l1, font=F(BOLD,52), fill=(246,248,252))
    d.text((52,214), l2, font=F(BOLD,52), fill=accent)
    d.text((52,300), sub, font=F(REG,27), fill=(198,206,220))
    base.save(os.path.join(ROOT,out)); print(out); stamp(out)

def plain_cover(out, tag, l1, l2, rows, foot, c1, c2, tagname=None):
    img = Image.new("RGB", (W, H), c1); d = ImageDraw.Draw(img)
    for y in range(H):
        k = y/H
        d.line([(0,y),(W,y)], fill=(int(c1[0]+(c2[0]-c1[0])*k), int(c1[1]+(c2[1]-c1[1])*k), int(c1[2]+(c2[2]-c1[2])*k)))
    tf = F(REG,25)
    d.rounded_rectangle([58,44,58+d.textlength(tag,font=tf)+42,92], 24, fill=(24,32,50), outline=(62,88,128), width=2)
    d.text((80,55), tag, font=tf, fill=(152,184,228))
    d.text((58,118), l1, font=F(BOLD,54), fill=(240,242,248))
    d.text((58,188), l2, font=F(BOLD,54), fill=(240,186,96))
    avail = H - 70 - 292
    gap = 8
    rh = min(80, (avail - gap*(len(rows)-1))//len(rows))
    y = 292
    for nm, note, col in rows:
        d.rounded_rectangle([58,y,W-58,y+rh], 11, fill=(22,26,38), outline=(42,48,64), width=2)
        d.rectangle([58,y,65,y+rh], fill=col)
        d.text((90,y+10), nm, font=F(BOLD,25), fill=col)
        d.text((90,y+rh-30), note, font=F(REG,19), fill=(148,154,170))
        y += rh + gap
    d.text((58,H-42), foot, font=F(REG,24), fill=(140,146,162))
    img.save(os.path.join(ROOT,out)); print(out); stamp(out)

# A Arkane —— 真实截图
news_cover(os.path.join(ROOT,"news-arkane","deathloop1.jpg"), "cover-arkane.png",
  "10 月 23 日 · 期限 11 月 13 日", "继 BioWare 之后",
  "Arkane Lyon 也悬了", "217 人，微软在找买家",
  (240,150,120), (40,26,24), (108,66,58), (226,160,150))

# B LPL —— 真实现场图
news_cover(os.path.join(ROOT,"news-lpl","ig-hle.jpg"), "cover-lpl-d3.png",
  "S16 瑞士轮 · 第三轮", "iG 赢了 HLE",
  "LPL 终于开张", "本届首次击败 LCK",
  (120,196,240), (24,34,54), (60,92,132), (150,190,232))

# C DDU —— 自制
plain_cover("cover-ddu.png", "显卡 · 别乱用手术刀",
  "驱动怎么装才干净", "大部分时候不用 DDU",
  [("换品牌才需要", "N 卡换 A 卡这种", (240,150,120)),
   ("先在安全模式", "正常模式下清不干净", (240,196,92)),
   ("先下好驱动再断网", "顺序错了会白折腾一晚", (130,210,160))],
  "DDU 是手术刀，不是日常用品", (12,14,20), (22,18,26))

# D 死区 —— 自制
plain_cover("cover-deadzone.png", "手柄 · 先测再调",
  "死区调大还是调小", "默认值不是最优",
  [("默认偏大", "按最差的那只手柄设计", (120,190,240)),
   ("调小更准", "但漂移会显现出来", (240,196,92)),
   ("先测零点", "手松开看读数稳不稳", (130,210,160))],
  "死区不是越小越好", (12,16,22), (18,26,36))
