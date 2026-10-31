// tools/shot-url.mjs —— 打开一个 URL 并截图，用来看页面真实渲染
// 用法: node tools/shot-url.mjs <url> <输出文件> [等待秒数]
import { chromium } from 'playwright';
import path from 'node:path';

const [url, out, waitSec] = process.argv.slice(2);
if (!url || !out) { console.error('用法: node tools/shot-url.mjs <url> <out.png> [秒]'); process.exit(1); }

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = b.contexts()[0];
const page = ctx.pages().find((p) => !p.url().startsWith('devtools://')) ?? ctx.pages()[0];

await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch((e) => console.log('跳转警告:', e.message));
await page.waitForTimeout(Number(waitSec || 6) * 1000);

const info = await page.evaluate(() => ({
  url: location.href,
  title: document.title,
  bodyLen: (document.body?.innerText || '').replace(/\s/g, '').length,
  hasLoginWall: /登录|扫码/.test((document.body?.innerText || '').slice(0, 300)),
}));
console.log(JSON.stringify(info, null, 2));
await page.screenshot({ path: path.resolve(out), fullPage: false });
console.log('截图:', path.resolve(out));
process.exit(0);
