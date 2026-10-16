// review.mjs —— 截取填充结果（顶部 + 正文中段 + 预览区）
import { chromium } from 'playwright';

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const page = b.contexts()[0].pages()[0];

// 回到顶部
await page.evaluate(() => window.scrollTo(0, 0));
await page.waitForTimeout(1200);
await page.screenshot({ path: 'C:\\Users\\86153\\xhh\\shots\\review-top.png' });

// 正文中段
await page.evaluate(() => window.scrollTo(0, 900));
await page.waitForTimeout(1000);
await page.screenshot({ path: 'C:\\Users\\86153\\xhh\\shots\\review-mid.png' });

// 正文后段
await page.evaluate(() => window.scrollTo(0, 1900));
await page.waitForTimeout(1000);
await page.screenshot({ path: 'C:\\Users\\86153\\xhh\\shots\\review-bottom.png' });

// 输出正文结构，确认标签层级
const struct = await page.evaluate(() => {
  const e = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
  const ed = e[e.length - 1];
  const out = [];
  [...ed.children].forEach((el) => {
    const t = el.tagName.toLowerCase();
    const txt = (el.innerText || '').replace(/\s+/g, ' ').slice(0, 46);
    out.push(`${t.padEnd(6)} | ${txt}`);
  });
  return { title: (e[0].innerText || '').trim(), blocks: out };
});
console.log('TITLE: ' + struct.title);
console.log('--- 正文块结构 ---');
struct.blocks.forEach((l) => console.log(l));

process.exit(0);
