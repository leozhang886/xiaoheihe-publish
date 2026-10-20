// tools/find-drafts-page.mjs —— 从编辑器点「草稿箱」，找出草稿列表页的真实地址
import { chromium } from 'playwright';

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = b.contexts()[0];
const page = ctx.pages().find((p) => !p.url().startsWith('devtools://')) ?? ctx.pages()[0];

// 用已知的草稿编辑页作为入口
const ENTRY = 'https://www.xiaoheihe.cn/creator/editor/edit/article/193949060';
console.log('打开已知草稿页…');
await page.goto(ENTRY, { waitUntil: 'domcontentloaded', timeout: 45000 }).catch((e) => console.log('  失败', e.message));
await page.waitForTimeout(5000);
console.log('  当前 URL:', page.url());

// 找「草稿箱」按钮
const clicked = await page.evaluate(() => {
  const els = [...document.querySelectorAll('button, a, div, span')];
  const hit = els.find((e) => (e.textContent || '').trim() === '草稿箱');
  if (!hit) return { found: false };
  const tag = hit.tagName.toLowerCase();
  hit.click();
  return { found: true, tag, cls: hit.className };
});
console.log('  找到「草稿箱」:', JSON.stringify(clicked));

await page.waitForTimeout(5000);
console.log('  点击后 URL:', page.url());

const info = await page.evaluate(() => {
  const txt = (document.body?.innerText || '').replace(/\n{2,}/g, '\n').slice(0, 1500);
  const draftLinks = [...document.querySelectorAll('a[href*="draft"]')]
    .map((a) => a.getAttribute('href')).slice(0, 30);
  return { url: location.href, txt, draftLinks };
});
console.log('  页面文字:');
console.log(info.txt.split('\n').map((l) => '    ' + l).join('\n'));
console.log('  含 draft 的链接:', JSON.stringify(info.draftLinks));

process.exit(0);
