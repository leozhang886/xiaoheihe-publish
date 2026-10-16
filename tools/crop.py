# crop.py —— 放大截图底部区域，读清 AI 相关文字
from PIL import Image

src = r"C:\Users\86153\xhh\shots\review-top.png"
im = Image.open(src)
W, H = im.size
print("size:", W, H)

# 底部 25% 全宽，放大 2 倍
crop = im.crop((0, int(H * 0.72), W, H))
crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
crop.save(r"C:\Users\86153\xhh\shots\crop-bottom.png")
print("saved crop-bottom.png", crop.size)

# 右侧预览栏底部
crop2 = im.crop((int(W * 0.62), int(H * 0.70), W, int(H * 0.92)))
crop2 = crop2.resize((crop2.width * 3, crop2.height * 3), Image.LANCZOS)
crop2.save(r"C:\Users\86153\xhh\shots\crop-preview.png")
print("saved crop-preview.png", crop2.size)
