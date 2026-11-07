// tools/debug-topic.mjs —— 查清「添加话题」这一步为什么加不上
// 用法: node tools/debug-topic.mjs <draftId> <关键词>
import { chromium } from 'playwright';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const PROFILE = path.join(ROOT, 'profile');
const SHOTS = path.join(ROOT, 'shots');
fs.mkdirSync(SHOTS, { recursive: true });

const id = process.argv[2];
const kw = process.argv[3] || 'Steam';
if (!id) { console.error('用法: node tools/debug-topic.mjs <draftId> <关键词>'); process.exit(1); }

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const log = (m) => console.log('[tp] ' + m);

const ctx = await chromium.launchPersistentContext(PROFILE, {
  headless: false,
  viewport: { width: 1600, height: 1000 },
});
const page = ctx.pages()[0] ?? (await ctx.newPage());

try {
  await page.goto(`https://www.xiaoheihe.cn/creator/editor/edit/article/${id}`, {
    waitUntil: 'domcontentloaded', timeout: 60000,
  });
  await sleep(9000);

  // 找「添加话题」按钮：优先 class，其次包含文本
  for (let i = 0; i < 6; i++) {
    await page.evaluate(() => window.scrollBy(0, 400));
    await sleep(500);
  }
  const btn = await page.evaluate(() => {
    let el = [...document.querySelectorAll('.editor__add-btn')].find(
      (e) => (e.textContent || '').includes('话题')
    );
    if (!el) {
      el = [...document.querySelectorAll('*')].find(
        (e) => (e.textContent || '').trim() === '添加话题'
      );
    }
    if (!el) return null;
    el.scrollIntoView({ block: 'center' });
    const r = el.getBoundingClientRect();
    return { x: r.x + r.width / 2, y: r.y + r.height / 2, cls: (el.className || '').slice(0, 50) };
  });
  log('添加话题按钮: ' + JSON.stringify(btn));
  if (!btn) throw new Error('找不到「添加话题」');
  // 先清掉遗留遮罩/弹层，再点
  await page.keyboard.press('Escape').catch(() => {});
  await sleep(600);
  const removed = await page.evaluate(() => {
    const sels = ['.hb-cpt__mask', '.t-mask', '.hb-toast__wrapper', '[class*=lightbox]', '[class*=preview-mask]'];
    let n = 0;
    sels.forEach((s) => document.querySelectorAll(s).forEach((e) => { e.remove(); n++; }));
    return n;
  });
  log('清掉遮罩 ' + removed + ' 个');

  // 用元素点击（会做可点性检查），失败再退回坐标
  let clicked = false;
  try {
    await page.click('.editor__add-btn:has-text("话题")', { timeout: 8000 });
    clicked = true;
    log('元素点击成功');
  } catch (e) {
    log('元素点击失败: ' + e.message.split('\n')[0]);
    await page.mouse.click(btn.x, btn.y);
    log('用坐标点击兜底');
  }
  await sleep(3500);

  // 弹窗结构
  const mask = await page.evaluate(() => {
    const m = document.querySelector('.hb-cpt__mask-wrapper');
    if (!m) return null;
    const inputs = [...m.querySelectorAll('input')].map((i) => ({
      cls: (i.className || '').slice(0, 60),
      ph: i.placeholder || '',
      visible: i.offsetParent !== null,
    }));
    return { found: true, inputs, html: m.outerHTML.replace(/\s+/g, ' ').slice(0, 900) };
  });
  log('弹窗: ' + (mask ? '有' : '没有'));
  if (mask) {
    log('弹窗里的 input: ' + JSON.stringify(mask.inputs));
    log('弹窗 HTML 片段:\n' + mask.html);
  }

  // 输入关键词
  const inputSel = '.hb-cpt__mask-wrapper input';
  const input = await page.$(inputSel);
  if (input) {
    await input.click();
    await input.fill(kw);
    log('已输入: ' + kw);
    for (const wait of [3000, 3000, 4000]) {
      await sleep(wait);
      const items = await page.evaluate(() => {
        const m = document.querySelector('.hb-cpt__mask-wrapper');
        if (!m) return { any: 0, list: [] };
        const all = [...m.querySelectorAll('*')]
          .filter((e) => e.children.length === 0 && (e.textContent || '').trim())
          .map((e) => ({ t: (e.textContent || '').trim().slice(0, 30), cls: (e.className || '').slice(0, 40) }));
        return { any: all.length, list: all.slice(0, 18) };
      });
      log(`等 ${wait}ms 后，弹窗内文本节点 ${items.any} 个:`);
      items.list.forEach((x) => log(`   ${x.t}   .${x.cls}`));
      if (items.any > 8) break;
    }
  } else {
    log('!! 弹窗里没有 input');
  }

  await page.screenshot({ path: path.join(SHOTS, `topic-debug-${Date.now()}.png`) });
  log('截图已存');
} catch (e) {
  log('❌ ' + e.message);
  await page.screenshot({ path: path.join(SHOTS, `topic-err-${Date.now()}.png`) }).catch(() => {});
} finally {
  await ctx.close().catch(() => {});
}
