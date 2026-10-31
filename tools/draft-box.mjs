// tools/draft-box.mjs —— 列出小黑盒服务器草稿箱里的条目
import { chromium } from 'playwright';

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = b.contexts()[0];
const page = ctx.pages().find((p) => !p.url().startsWith('devtools://')) ?? ctx.pages()[0];

await page.goto('https://www.xiaoheihe.cn/creator/draft', { waitUntil: 'domcontentloaded', timeout: 45000 });
await page.waitForTimeout(5000);

const info = await page.evaluate(() => ({
  url: location.href,
  captcha: /请依次点击|安全验证/.test(document.body.innerText || ''),
  titles: [...document.querySelectorAll('.creator-draft__content')].map((e) => (e.textContent || '').trim()),
  metas: [...document.querySelectorAll('.creator-draft__meta')].map((e) => (e.textContent || '').trim()),
}));

console.log('URL:', info.url);
console.log('验证码:', info.captcha);
console.log(`草稿数: ${info.titles.length}`);
info.titles.forEach((t, i) => console.log(`  ${i + 1}. ${t || '(无标题)'}   ${info.metas[i] || ''}`));
process.exit(0);
