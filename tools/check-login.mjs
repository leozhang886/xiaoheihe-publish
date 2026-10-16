// tools/check-login.mjs —— 检查小黑盒登录态
import { chromium } from 'playwright';

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = b.contexts()[0];
const page = ctx.pages().find((p) => !p.url().startsWith('devtools://')) ?? ctx.pages()[0];

await page.goto('https://www.xiaoheihe.cn/', { waitUntil: 'domcontentloaded', timeout: 45000 }).catch(() => {});
await page.waitForTimeout(4000);

const st = await page.evaluate(() => {
  const txt = (document.body?.innerText || '').replace(/\s+/g, ' ').slice(0, 300);
  return {
    url: location.href,
    loggedIn: /发布内容/.test(txt),
    hasLoginBtn: /登录/.test(txt),
    snippet: txt.slice(0, 160),
  };
});
console.log(JSON.stringify(st, null, 2));

// 顺便看看 cookie 里还有没有登录凭据
const names = await page.evaluate(() => document.cookie.split(';').map((s) => s.split('=')[0].trim()).filter(Boolean));
console.log('cookie 名:', JSON.stringify(names));

process.exit(0);
