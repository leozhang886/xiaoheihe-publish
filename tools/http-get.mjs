// tools/http-get.mjs —— 用 Node 直接抓 HTML 并抽正文文字（不需要浏览器）
// 用法: node tools/http-get.mjs <url> [最多字符数]
// 说明：本机 hosts 把 steam/github 等指到 302 代理，证书是 MITM 的，
//       所以调用前需要 $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"

const url = process.argv[2];
const MAX = parseInt(process.argv[3] || '4000', 10);
if (!url) { console.error('用法: node tools/http-get.mjs <url> [最多字符数]'); process.exit(1); }

const r = await fetch(url, {
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  },
});
console.log('HTTP', r.status, r.headers.get('content-type'));
let html = await r.text();
console.log('原始长度', html.length);

let body = html
  .replace(/<script[\s\S]*?<\/script>/gi, '')
  .replace(/<style[\s\S]*?<\/style>/gi, '')
  .replace(/<li[^>]*>/gi, '\n- ')
  .replace(/<\/(p|div|h[1-6]|li|tr|td)>/gi, '\n')
  .replace(/<br\s*\/?>/gi, '\n')
  .replace(/<[^>]+>/g, '')
  .replace(/&nbsp;/g, ' ')
  .replace(/&amp;/g, '&')
  .replace(/&quot;/g, '"')
  .replace(/&#39;/g, "'")
  .replace(/&gt;/g, '>')
  .replace(/&lt;/g, '<')
  .replace(/[ \t]+/g, ' ')
  .replace(/\n{3,}/g, '\n\n')
  .trim();

console.log('=== 正文（' + body.length + ' 字）===');
console.log(body.slice(0, MAX));
process.exit(0);
