# make_images.py —— 生成文章配图
from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"C:\Users\86153\xhh\assets"
os.makedirs(OUT, exist_ok=True)

CN = r"C:\Windows\Fonts\msyh.ttc"
CNB = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    return ImageFont.truetype(CNB if bold else CN, size)


# ---------------------------------------------------------------- 封面
# 左：小黑盒编辑器截图（脚本自动填好的文章）；右：终端日志
editor = Image.open(r"C:\Users\86153\xhh\shots\bg-top.png").convert("RGB")

W, H = 1920, 1080
cover = Image.new("RGB", (W, H), (16, 18, 22))
d = ImageDraw.Draw(cover)

# 左侧：编辑器截图，裁成左半 + 缩放
ew, eh = editor.size
left_part = editor.crop((0, 0, int(ew * 0.66), eh))
target_w = 1150
ratio = target_w / left_part.width
left_part = left_part.resize((target_w, int(left_part.height * ratio)), Image.LANCZOS)
cover.paste(left_part, (0, max(0, (H - left_part.height) // 2)))

# 右侧：终端
LOG = """PS C:\\Users\\86153\\xhh> node publish.mjs articles/uncharted.md

[xhh] 文章: 别买错！神秘海域在PC上只有一部
[xhh] 片段: 6 个（含 3 张图）
[xhh] 打开创作页...
[xhh] 编辑器 URL: https://www.xiaoheihe.cn/
      creator/editor/draft/article/local_...
[xhh] 填写标题...
[xhh]   标题 = 别买错！神秘海域在PC上只有一部
[xhh] 填充正文...
[xhh]   [1/6] 插图 1...
[xhh]   [3/6] 插图 2...
[xhh]   [5/6] 插图 3...
[xhh]   正文 1052 字，图片 3/3 张
[xhh] 选择社区...
[xhh]   社区已选 -> 神秘海域: 盗贼传奇合辑
[xhh] 关联计数: ["1/2","0/5"]
[xhh] === 未发布（默认安全模式）===
[xhh] 确认无误后执行: ... --publish"""

panel_x = 1180
d.rectangle([panel_x - 20, 60, W - 40, H - 60], fill=(24, 27, 33))
d.rectangle([panel_x - 20, 60, W - 40, 108], fill=(38, 42, 50))
for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
    d.ellipse([panel_x + 4 + i * 26, 76, panel_x + 18 + i * 26, 90], fill=c)
d.text((panel_x + 100, 72), "publish.mjs  —  运行日志", font=font(24), fill=(200, 205, 215))

y = 132
for line in LOG.split("\n"):
    col = (120, 230, 150) if line.startswith("[xhh]") else (200, 205, 215)
    if "标题 =" in line or "社区已选" in line or "正文" in line:
        col = (255, 210, 120)
    if "[xhh]" == line[:5]:
        col = (120, 230, 150)
    d.text((panel_x, y), line, font=font(19), fill=col)
    y += 30

cover.save(os.path.join(OUT, "cover-dsh.png"), quality=95)
print("cover-dsh.png", cover.size)


# ---------------------------------------------------------------- 流程图
FW, FH = 1600, 900
flow = Image.new("RGB", (FW, FH), (248, 249, 251))
d = ImageDraw.Draw(flow)

d.text((70, 50), "我用 DSH 发小黑盒的流程", font=font(44, True), fill=(28, 32, 40))
d.text((72, 112), "DSH = DeepSeek Harness，一个能操作浏览器的 AI 助手", font=font(22), fill=(120, 128, 140))

steps = [
    ("1", "写 Markdown 稿子", "标题 / 正文 / 配图链接，全在本地", (66, 133, 244)),
    ("2", "转换 + 注入编辑器", "# → h2、## → h3，粘贴事件直填", (52, 168, 83)),
    ("3", "自动插图", "本地文件或 URL，小黑盒自动转存 CDN", (251, 140, 0)),
    ("4", "搜索并选中关联社区", "发布必填，脚本自动搜", (156, 39, 176)),
    ("5", "你来点发布", "最后一步留给人", (217, 48, 37)),
]

bx, by = 70, 190
bw, bh = FW - 140, 108
for num, title, desc, color in steps:
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=(255, 255, 255),
                        outline=(226, 230, 236), width=2)
    d.rounded_rectangle([bx, by, bx + 12, by + bh], radius=6, fill=color)
    d.ellipse([bx + 40, by + 28, bx + 92, by + 80], fill=color)
    nf = font(30, True)
    tb = d.textbbox((0, 0), num, font=nf)
    d.text((bx + 66 - (tb[2] - tb[0]) / 2, by + 54 - (tb[3] - tb[1]) / 2 - tb[1]), num, font=nf, fill=(255, 255, 255))
    d.text((bx + 120, by + 26), title, font=font(30, True), fill=(28, 32, 40))
    d.text((bx + 120, by + 66), desc, font=font(21), fill=(120, 128, 140))
    # 箭头
    if num != "5":
        cy = by + bh
        d.line([bx + bw // 2, cy + 6, bx + bw // 2, cy + 22], fill=(200, 206, 214), width=3)
        d.polygon([(bx + bw // 2 - 7, cy + 20), (bx + bw // 2 + 7, cy + 20), (bx + bw // 2, cy + 30)],
                  fill=(200, 206, 214))
    by += bh + 36

flow.save(os.path.join(OUT, "flow-dsh.png"), quality=95)
print("flow-dsh.png", flow.size)

print("\n生成完毕:")
for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    print(f"  {f}  {os.path.getsize(p)//1024}KB")
