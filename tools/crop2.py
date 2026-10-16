# crop2.py —— 放大验证码区域
from PIL import Image

src = r"C:\Users\86153\xhh\shots\review-top.png"
im = Image.open(src)
W, H = im.size

# 验证码大致区域
crop = im.crop((int(W * 0.28), int(H * 0.35), int(W * 0.78), int(H * 0.82)))
crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
crop.save(r"C:\Users\86153\xhh\shots\crop-captcha.png")
print("saved", crop.size)

# 另外：直接在当前页面里全文搜 "生成"
