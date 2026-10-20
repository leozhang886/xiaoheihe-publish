// tools/probe-edit-page.mjs —— 只读探测：已发布的文章能不能进编辑器改
import { chromium } from 'playwright';

const POST_ID = process.argv[2];
if (!POST_ID) { console.error('用法: node tools/probe-edit-page.mjs <post_id>'); process.exit(1); }

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = b.contexts()[0];
const page = ctx.pages().find((p) => !p.url().startsWith('devtools://')) ?? ctx.pages()[0];

const url = `https://www.xiaoheihe.cn/creator/editor/edit/article/${POST_ID}`;
console.log('尝试打开:', url);
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 }).catch((e) => console.log('  跳转失败', e.message));
await page.waitForTimeout(6000);

const info = await page.evaluate(() => {
  const eds = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
  const titleText = eds[0]?.textContent?.trim() || '';
  const bodyText = eds.length > 1 ? eds[eds.length - 1].textContent.trim() : '';
  const buttons = [...document.querySelectorAll('button')]
    .map((b) => (b.textContent || '').trim())
    .filter((t) => t && t.length < 12)
    .slice(0, 30);
  return {
    url: location.href,
    editorCount: eds.length,
    titleText: titleText.slice(0, 60),
    bodyLen: bodyText.length,
    bodyHead: bodyText.slice(0, 120),
    buttons,
  };
});

console.log('  最终 URL:', info.url);
console.log('  编辑器数量:', info.editorCount);
console.log('  标题框内容:', info.titleText || '（空）');
console.log('  正文长度:', info.bodyLen);
console.log('  正文开头:', info.bodyHead || '（空）');
console.log('  页面按钮:', JSON.stringify(info.buttons));

process.exit(0);
