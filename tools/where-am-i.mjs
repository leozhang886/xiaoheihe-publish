// tools/where-am-i.mjs —— 看看浏览器现在开着哪些页面、编辑器里有没有内容
import { chromium } from 'playwright';

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = b.contexts()[0];
console.log('上下文数:', b.contexts().length, ' 页面数:', ctx.pages().length);

for (const [i, p] of ctx.pages().entries()) {
  let title = '', editors = '', bodyLen = '';
  try {
    title = await p.title();
    const info = await p.evaluate(() => {
      const eds = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
      return {
        n: eds.length,
        t: (eds[0]?.innerText || '').trim().slice(0, 40),
        b: (eds[eds.length - 1]?.innerText || '').trim().length,
      };
    }).catch(() => ({ n: 0, t: '', b: '' }));
    editors = info.n;
    title = (info.t || title).slice(0, 40);
    bodyLen = info.b;
  } catch (e) {
    title = '(读取失败)';
  }
  console.log(`  [${i}] ${p.url()}`);
  console.log(`      标题/首行: ${title || '(空)'}`);
  console.log(`      编辑器: ${editors} 个${editors ? `，正文 ${bodyLen} 字` : ''}`);
}

process.exit(0);
