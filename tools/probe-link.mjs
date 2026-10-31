// tools/probe-link.mjs —— 查小黑盒帖子是否存在（走接口，绕开页面验证码）
// 用法: node tools/probe-link.mjs <link_id> [更多 id...]

const ids = process.argv.slice(2);
if (!ids.length) { console.error('用法: node tools/probe-link.mjs <link_id> [...]'); process.exit(1); }

const ENDPOINTS = [
  (id) => `https://www.xiaoheihe.cn/bbs/app/link/tree?link_id=${id}`,
  (id) => `https://api.xiaoheihe.cn/bbs/app/link/tree?link_id=${id}`,
  (id) => `https://www.xiaoheihe.cn/bbs/app/link/details?link_id=${id}`,
];
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/153.0.0.0 Safari/537.36';

let any = false;
for (const id of ids) {
  console.log(`\n=== link_id ${id} ===`);
  for (const ep of ENDPOINTS) {
    const u = ep(id);
    try {
      const r = await fetch(u, { headers: { 'User-Agent': UA, Referer: 'https://www.xiaoheihe.cn/' } });
      const txt = await r.text();
      const capped = /captcha|安全验证|请依次点击/i.test(txt);
      let tip = '';
      try {
        const j = JSON.parse(txt);
        const status = j.status ?? j.msg ?? j.result?.status ?? '';
        const title = j.result?.link?.title || j.result?.title || j.link?.title || '';
        tip = ` status=${JSON.stringify(status)} title=${JSON.stringify(title)}`;
        if (title) any = true;
      } catch { /* 非 JSON */ }
      console.log(`  ${r.status}  ${u.split('?')[0].replace('https://', '')}  长度=${txt.length} 验证码=${capped}${tip}`);
      if (!capped && txt.length > 150 && txt.length < 900) {
        console.log('    预览:', txt.slice(0, 200).replace(/\s+/g, ' '));
      }
    } catch (e) {
      console.log(`  ERR ${u.split('?')[0]} ${e.message}`);
    }
  }
}
console.log(any ? '\n✅ 拿到标题 —— 帖子存在' : '\n⚠️ 没拿到标题，接口可能都改了或需要签名');
process.exit(0);
