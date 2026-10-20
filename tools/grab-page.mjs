// tools/grab-page.mjs —— 用已登录的浏览器渲染页面并把正文吐出来
// 用法: node tools/grab-page.mjs <url> [最多字符数]
import { chromium } from 'playwright';

const url = process.argv[2];
const MAX = parseInt(process.argv[3] || '6000', 10);
if (!url) { console.error('用法: node tools/grab-page.mjs <url> [最多字符数]'); process.exit(1); }

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = b.contexts()[0];
const page = ctx.pages().find((p) => !p.url().startsWith('devtools://')) ?? ctx.pages()[0];

console.log('打开:', url);
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch((e) => console.log('  跳转警告:', e.message));
await page.waitForTimeout(5000);

const txt = await page.evaluate(() => {
  const pick = document.querySelector('.faq_content, #faq_content, .help_page_content, article, main');
  const el = pick || document.body;
  return (el.innerText || '').replace(/\n{3,}/g, '\n\n').trim();
});

console.log('=== 正文（' + txt.length + ' 字）===');
console.log(txt.slice(0, MAX));
process.exit(0);
