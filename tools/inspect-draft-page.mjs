// tools/inspect-draft-page.mjs —— 只读：看草稿箱有没有分类标签 / 文章草稿
import { chromium } from 'playwright';

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = b.contexts()[0];
const page = ctx.pages().find((p) => !p.url().startsWith('devtools://')) ?? ctx.pages()[0];

await page.goto('https://www.xiaoheihe.cn/creator/draft', { waitUntil: 'domcontentloaded', timeout: 45000 });
await page.waitForTimeout(4000);

const info = await page.evaluate(() => {
  // 找可能的分类标签
  const tabs = [...document.querySelectorAll('[class*="tab"], [class*="Tab"], [role="tab"]')]
    .map((e) => ({ cls: e.className, text: (e.textContent || '').trim().slice(0, 20) }))
    .filter((t) => t.text);

  // 每个草稿条目
  const items = [...document.querySelectorAll('[class*="draft"], [class*="Draft"]')]
    .map((e) => {
      const t = (e.textContent || '').replace(/\s+/g, ' ').trim();
      return t.length > 3 && t.length < 160 ? { cls: String(e.className).slice(0, 60), t } : null;
    })
    .filter(Boolean).slice(0, 25);

  // 页面里有没有「文章」字样
  const bodyTxt = document.body?.innerText || '';
  return {
    url: location.href,
    hasArticleWord: bodyTxt.includes('文章'),
    hasPostWord: bodyTxt.includes('帖子'),
    tabs: tabs.slice(0, 12),
    items,
  };
});

console.log('URL:', info.url);
console.log('页面含「文章」:', info.hasArticleWord, ' 含「帖子」:', info.hasPostWord);
console.log('\n--- 分类标签候选 ---');
for (const t of info.tabs) console.log(`  [${t.cls}] 「${t.text}」`);
console.log('\n--- 草稿条目候选 ---');
for (const i of info.items) console.log(`  [${i.cls}]  ${i.t}`);

process.exit(0);
