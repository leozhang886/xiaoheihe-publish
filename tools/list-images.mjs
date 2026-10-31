// tools/list-images.mjs —— 列出网页里的图片地址（找新闻图用）
// 用法: node tools/list-images.mjs <url> [最多条数]
const url = process.argv[2];
const MAX = parseInt(process.argv[3] || '15', 10);
if (!url) { console.error('用法: node tools/list-images.mjs <url> [条数]'); process.exit(1); }

const r = await fetch(url, {
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36',
    'Referer': new URL(url).origin + '/',
  },
});
console.log('HTTP', r.status);
const html = await r.text();
console.log('原始长度', html.length);

const urls = new Set();
const re = /<img[^>]+(?:src|data-src|data-original)\s*=\s*["']([^"']+)["']/gi;
let m;
while ((m = re.exec(html))) {
  let u = m[1];
  if (u.startsWith('//')) u = 'https:' + u;
  if (!/^https?:/.test(u)) continue;
  if (/\.(gif|svg)$/i.test(u)) continue;
  if (/logo|icon|avatar|qr|emoji/i.test(u)) continue;
  urls.add(u);
}

const list = [...urls].slice(0, MAX);
console.log(`\n=== 候选图片 ${urls.size} 张，列前 ${list.length} ===`);
list.forEach((u, i) => console.log(`${i + 1}. ${u}`));
process.exit(0);
