// tools/check-public.mjs —— 用全新的匿名上下文打开帖子，判断是否公开可见
// 用法: node tools/check-public.mjs <url>
import { chromium } from 'playwright';
import path from 'node:path';

const url = process.argv[2];
if (!url) { console.error('用法: node tools/check-public.mjs <url>'); process.exit(1); }

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
// 新建一个隔离上下文：没有登录 Cookie，等于陌生人访问
const ctx = await b.newContext({ viewport: { width: 1400, height: 900 } });
const page = await ctx.newPage();

await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch((e) => console.log('跳转警告:', e.message));
await page.waitForTimeout(8000);

const info = await page.evaluate(() => {
  const t = (document.body?.innerText || '');
  return {
    url: location.href,
    title: document.title,
    len: t.replace(/\s/g, '').length,
    captcha: /请依次点击|安全验证/.test(t),
    head: t.replace(/\n{2,}/g, '\n').trim().slice(0, 320),
  };
});

console.log(JSON.stringify(info, null, 2));
const out = path.resolve('shots', 'public-check.png');
await page.screenshot({ path: out });
console.log('截图:', out);

await ctx.close();
process.exit(0);
