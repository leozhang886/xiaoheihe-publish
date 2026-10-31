# 对比三个版本的写作指标
import re, os

BASE = r"C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒\articles"
files = {
    "A 直复营销": "ori-A-direct-response.md",
    "B 现有规范": "ori-B-current-spec.md",
    "C STE简化":  "ori-C-ste.md",
}

def metrics(path):
    t = open(path, encoding="utf-8").read()
    # 去掉 frontmatter 和声明段
    t = re.sub(r"^---[\s\S]*?---\n", "", t)
    t = re.sub(r"写在前面：.*?\n", "", t, count=1)
    # 去掉标题行、图片
    t = re.sub(r"(?m)^#+ .*$", "", t)
    t = re.sub(r"!\[\]\([^)]*\)", "", t)

    # 按中文句末标点断句
    sents = [s.strip() for s in re.split(r"[。！？\n]+", t) if s.strip()]
    # 只统计"实义句"（长度 > 4），避免把列表项碎片算进来
    sents = [s for s in sents if len(s) > 4]

    lens = [len(s) for s in sents]
    chars = len(re.sub(r"\s", "", t))
    return {
        "总字数": chars,
        "句数": len(sents),
        "平均句长": round(sum(lens) / len(lens), 1) if lens else 0,
        "最长句": max(lens) if lens else 0,
        "超40字的句": sum(1 for l in lens if l > 40),
        "破折号": len(re.findall(r"——|—", t)),
        "加粗": len(re.findall(r"\*\*[^*]+\*\*", t)),
        "我": len(re.findall(r"我", t)),
    }

rows = {k: metrics(os.path.join(BASE, v)) for k, v in files.items()}
keys = list(next(iter(rows.values())).keys())

w = 14
print("指标".ljust(w), "".join(k.ljust(w) for k in rows))
print("-" * (w + w * len(rows)))
for key in keys:
    print(key.ljust(w), "".join(str(rows[k][key]).ljust(w) for k in rows))
