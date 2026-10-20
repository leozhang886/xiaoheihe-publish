// tools/number-headings.mjs —— 给文章的小标题自动加中文序号
// 用法: node tools/number-headings.mjs articles/xxx.md [更多文件...]
// 已有序号的会先剥掉再重排，可以重复跑。

import fs from 'node:fs';

const CN = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
            '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十'];

const strip = (s) =>
  s.replace(/^([一二三四五六七八九十]+、|\d+[、.)]\s*|\d+\s+)/, '').trim();

let changed = 0;
for (const file of process.argv.slice(2)) {
  if (!fs.existsSync(file)) { console.log(`${file}  不存在`); continue; }
  const md = fs.readFileSync(file, 'utf8');
  // 拆出 frontmatter 原样保留
  const fm = md.match(/^(---\r?\n[\s\S]*?\r?\n---\r?\n?)/);
  const head = fm ? fm[1] : '';
  const body = fm ? md.slice(head.length) : md;

  let n = 0;
  const out = body.split('\n').map((line) => {
    const m = line.match(/^(#{1,6})\s+(.*)$/);
    if (!m) return line;
    const title = strip(m[2]);
    const num = CN[n] || String(n + 1);
    n++;
    return `${m[1]} ${num}、${title}`;
  }).join('\n');

  const next = head + out;
  if (next !== md) {
    fs.writeFileSync(file, next, 'utf8');
    console.log(`${file}  已编号，共 ${n} 节`);
    changed++;
  } else {
    console.log(`${file}  无变化`);
  }
}
console.log(changed ? `\n完成 ${changed} 个文件` : '\n没有需要改的');
