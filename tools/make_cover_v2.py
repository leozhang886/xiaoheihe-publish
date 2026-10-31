"""小黑盒封面 v2 新风格：右侧超大字（截断出画）+ 左侧标题 + 三张要点卡。

依据 refs/封面规则.md：
- 背景尽量简单（纯渐变，不堆装饰）
- 视觉重心偏右
- 用「大而截断的文字」

用法（作为模块调用，或直接改底部 demo 区）：
    python tools/make_cover_v2.py
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\assets"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
REG = r"C:\Windows\Fonts\msyh.ttc"
PY = r"C:\Users\86153\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"

W, H = 1200, 675


def F(p, s):
    return ImageFont.truetype(p, s)


def cover(out, tag, line1, line2, sub, big, cards, base=(10, 12, 20), grad=(26, 34, 52), bigcol=(38, 44, 68)):
    img = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(img)
    # 纯渐变底，不加任何装饰
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(base[i] + (grad[i] - base[i]) * k) for i in range(3)))

    # 右侧超大字，故意截断出画（下移，给右上角贴纸留位）
    if big:
        d.text((858, 128), big, font=F(BOLD, 400), fill=bigcol)

    # 左上小标
    tf = F(REG, 22)
    d.rounded_rectangle([64, 46, 64 + d.textlength(tag, font=tf) + 34, 88], 20,
                        fill=(26, 32, 48), outline=(66, 78, 108), width=2)
    d.text((81, 56), tag, font=tf, fill=(164, 184, 222))

    # 标题
    d.text((64, 152), line1, font=F(BOLD, 56), fill=(244, 246, 250))
    d.text((64, 226), line2, font=F(BOLD, 56), fill=(244, 190, 96))
    d.text((64, 326), sub, font=F(REG, 26), fill=(188, 198, 216))

    # 三张卡横排
    cw = 336
    gap = 14
    x = 64
    for nm, note, col in cards:
        d.rounded_rectangle([x, 414, x + cw, 506], 12, fill=(24, 28, 44), outline=(54, 62, 86), width=2)
        d.rectangle([x, 414, x + 6, 506], fill=col)
        d.text((x + 28, 426), nm, font=F(BOLD, 24), fill=col)
        d.text((x + 28, 464), note, font=F(REG, 20), fill=(158, 166, 184))
        x += cw + gap

    path = os.path.join(ROOT, out)
    img.save(path)
    print(out)
    subprocess.run([PY, r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\tools\add_mascot.py", "--only", out],
                   capture_output=True, text=True)


if __name__ == "__main__":
    # 键盘
    cover("cover-keyboard.png", "键盘 · 别看颜色",
          "买键盘只看颜色", "等于没选",
          "真正决定手感的是三个参数", "3",
          [("触发力度", "35-65 克", (120, 190, 240)),
           ("触发行程", "1.2-2.0mm", (240, 190, 96)),
           ("段落感", "要不要卡点", (150, 214, 160))])

    # 显卡驱动
    cover("cover-ddu.png", "显卡 · 别乱用手术刀",
          "驱动怎么装才干净", "大部分时候不用 DDU",
          "只有三种情况需要动它", "3",
          [("换品牌", "N 卡换 A 卡这种", (240, 150, 120)),
           ("反复崩溃", "回滚也救不回来", (240, 190, 96)),
           ("安装报错", "驱动装不上去", (150, 214, 160))],
          base=(14, 12, 14), grad=(38, 28, 24), bigcol=(52, 40, 34))

    # 账号安全
    cover("cover-account.png", "账号安全 · 三条路",
          "账号被偷", "基本都是自己给的门",
          "骗子要的是确认，不是密码", "3",
          [("假登录页", "域名差一个字母", (238, 138, 126)),
           ("假交易", "让你去第三方平台", (240, 176, 96)),
           ("邮箱先失守", "邮箱丢了全白搭", (172, 160, 232))],
          base=(18, 12, 16), grad=(42, 24, 28), bigcol=(54, 34, 38))
