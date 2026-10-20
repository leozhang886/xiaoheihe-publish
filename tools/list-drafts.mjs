// tools/list-drafts.mjs —— 只读：列出小黑盒创作中心的草稿，不做任何修改
import { chromium } from 'playwright';

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = b.contexts()[0];
const page = ctx.pages().find((p) => !p.url().startsWith('devtools://')) ?? ctx.pages()[0];

// 可能的草稿管理页
const candidates = [
  'https://www.xiaoheihe.cn/creator/center',
  'https://www.xiaoheihe.cn/creator/editor',
  'https://www.xiaoheihe.cn/creator',
];

for (const url of candidates) {
  console.log(`\n=== 尝试 ${url} ===`);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 }).catch((e) => console.log('  跳转失败', e.message));
  await page.waitForTimeout(3500);

  const info = await page.evaluate(() => {
    const txt = (document.body?.innerText || '').replace(/\n{2,}/g, '\n').slice(0, 1200);
    const links = [...document.querySelectorAll('a[href]')]
      .map((a) => ({ href: a.getAttribute('href'), text: (a.textContent || '').trim().slice(0, 40) }))
      .filter((l) => l.text || (l.href || '').includes('draft'))
      .slice(0, 40);
    return { url: location.href, title: document.title, txt, links };
  });

  console.log('  最终 URL:', info.url);
  console.log('  标题:', info.title);
  console.log('  --- 页面文字（前 700 字）---');
  console.log(info.txt.slice(0, 700).split('\n').map((l) => '    ' + l).join('\n'));
  console.log('  --- 含 draft 或文字链接 ---');
  for (const l of info.links) if ((l.href || '').includes('draft')) console.log(`    ${l.href}  「${l.text}」`);
}

process.exit(0);
