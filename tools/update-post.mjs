// tools/update-post.mjs —— 更新「已发布」文章的正文
//
// 用法：
//   node tools/update-post.mjs <post_id> <文章.md>            # 只填进编辑页，不保存（安全）
//   node tools/update-post.mjs <post_id> <文章.md> --save     # 填完点「修改」保存
//
// 前提：node session.mjs 已在跑（CDP 9222），且浏览器处于登录状态。
// 注意：这是改线上内容，默认不保存。

import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadArticle } from '../lib/md2xhh.mjs';

const argv = process.argv.slice(2);
const postId = argv.find((a) => /^\d+$/.test(a));
const file = argv.find((a) => a.endsWith('.md'));
const DO_SAVE = argv.includes('--save');

if (!postId || !file) {
  console.error('用法: node tools/update-post.mjs <post_id> <文章.md> [--save]');
  process.exit(1);
}

const PROJECT_ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const SHOT_DIR = path.join(PROJECT_ROOT, 'shots');
fs.mkdirSync(SHOT_DIR, { recursive: true });

const log = (...a) => console.log('[edit]', ...a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const md = fs.readFileSync(path.resolve(file), 'utf8');
const { meta, segments } = loadArticle(md);
log(`文章: ${meta.title}`);
log(`片段: ${segments.length} 个（含 ${segments.filter((s) => s.type === 'image').length} 张图）`);

const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = browser.contexts()[0];
const page = ctx.pages().find((p) => !p.url().startsWith('devtools://')) ?? ctx.pages()[0];

const EDITORS = `[...document.querySelectorAll('div.ProseMirror.hb-editor')]`;
const pick = (which) => `${EDITORS}[${which === 'title' ? '0' : `length - 1`}]`;

async function focusEditor(which) {
  await page.evaluate(({ which, EDITORS }) => {
    const e = eval(EDITORS);
    const ed = which === 'title' ? e[0] : e[e.length - 1];
    ed.focus();
  }, { which, EDITORS });
}

async function collapseToEnd(which) {
  await page.evaluate(({ which, EDITORS }) => {
    const e = eval(EDITORS);
    const ed = which === 'title' ? e[0] : e[e.length - 1];
    ed.focus();
    const s = window.getSelection();
    const r = document.createRange();
    r.selectNodeContents(ed);
    r.collapse(false);
    s.removeAllRanges();
    s.addRange(r);
  }, { which, EDITORS });
}

async function clearEditor(which) {
  for (let attempt = 0; attempt < 3; attempt++) {
    await page.evaluate(({ which, EDITORS }) => {
      const e = eval(EDITORS);
      const ed = which === 'title' ? e[0] : e[e.length - 1];
      ed.focus();
      const s = window.getSelection();
      const r = document.createRange();
      r.selectNodeContents(ed);
      s.removeAllRanges();
      s.addRange(r);
    }, { which, EDITORS });
    await page.keyboard.press('Delete');
    await sleep(500);
    const left = await page.evaluate(({ which, EDITORS }) => {
      const e = eval(EDITORS);
      const ed = which === 'title' ? e[0] : e[e.length - 1];
      return (ed.innerText || '').replace(/[\u200b\s]/g, '').length;
    }, { which, EDITORS });
    if (left === 0) return;
    await focusEditor(which);
    await page.keyboard.press('Control+A');
    await page.keyboard.press('Delete');
    await sleep(500);
  }
  const left = await page.evaluate(({ which, EDITORS }) => {
    const e = eval(EDITORS);
    const ed = which === 'title' ? e[0] : e[e.length - 1];
    return (ed.innerText || '').replace(/[\u200b\s]/g, '').length;
  }, { which, EDITORS });
  if (left > 0) throw new Error(`${which} 清空失败，还剩 ${left} 字`);
}

async function pasteHtml(html) {
  await collapseToEnd('body');
  await page.evaluate((h) => {
    const e = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
    const ed = e[e.length - 1];
    ed.focus();
    const dt = new DataTransfer();
    dt.setData('text/html', h);
    dt.setData('text/plain', h.replace(/<[^>]+>/g, ''));
    ed.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }));
  }, html);
  await sleep(700);
}

async function insertImage(src) {
  const isLocal = !/^https?:\/\//i.test(src);
  await collapseToEnd('body');
  await page.evaluate(() => document.querySelectorAll('.t-mask').forEach((m) => m.remove()));
  await page.evaluate(() => document.querySelector('button[data-name="插入图片"]')?.click());
  await page.waitForSelector('.hb-cpt__mask-wrapper', { timeout: 15000 });
  await sleep(700);

  if (isLocal) {
    await page.evaluate(() => document.querySelectorAll('.t-mask').forEach((m) => m.remove()));
    await sleep(300);
    const c = await page.evaluate(() => {
      const m = document.querySelector('.hb-cpt__mask-wrapper');
      const up = m.querySelector('.editor-image-wrapper__box.upload') || m.querySelector('.model-image__local-box');
      const r = up.getBoundingClientRect();
      return { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2) };
    });
    const chooserPromise = page.waitForEvent('filechooser', { timeout: 12000 });
    await page.mouse.click(c.x, c.y);
    const chooser = await chooserPromise;
    await chooser.setFiles(path.resolve(src));
    log(`  (本地文件上传: ${path.basename(src)})`);
  } else {
    await page.evaluate((src) => {
      const inp = document.querySelector('.hb-cpt__mask-wrapper input.hb-cpt__input-item');
      if (!inp) throw new Error('no url input');
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      setter.call(inp, src);
      inp.dispatchEvent(new Event('input', { bubbles: true }));
      inp.dispatchEvent(new Event('change', { bubbles: true }));
    }, src);
    await sleep(400);
    await page.evaluate(() => document.querySelector('.hb-cpt__mask-wrapper .editor-model__import-btn')?.click());
  }

  await page.waitForFunction(() => {
    const m = document.querySelector('.hb-cpt__mask-wrapper');
    if (!m) return false;
    return [...m.querySelectorAll('img')].some((i) => i.src.includes('imgheybox'));
  }, { timeout: 60000 }).catch(() => log('  ⚠ 图片上传等待超时，仍尝试确认'));
  await sleep(900);
  await page.evaluate(() =>
    document.querySelector('.hb-cpt__mask-wrapper .editor-__model-frame-bottom-btn.hb-color__btn--confirm')?.click()
  );
  await sleep(1300);
}

/* ---------------- 主流程 ---------------- */

log(`打开编辑页（post ${postId}）…`);
await page.goto(`https://www.xiaoheihe.cn/creator/editor/edit/article/${postId}`, {
  waitUntil: 'domcontentloaded',
  timeout: 45000,
});
await page.waitForSelector('div.ProseMirror.hb-editor', { timeout: 30000 });
await sleep(5000);

const before = await page.evaluate(() => {
  const e = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
  return {
    title: (e[0]?.innerText || '').trim(),
    bodyLen: (e[e.length - 1]?.innerText || '').trim().length,
  };
});
log(`  原稿: 标题「${before.title}」，正文 ${before.bodyLen} 字`);

log('清空原标题与正文…');
await clearEditor('title');
await clearEditor('body');

log('填标题…');
await focusEditor('title');
await page.keyboard.type(meta.title, { delay: 12 });
await sleep(600);
const gotTitle = await page.evaluate(() => {
  const e = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
  return (e[0]?.innerText || '').trim();
});
log(`  标题 = ${gotTitle}`);
if (gotTitle.replace(/\s/g, '') !== String(meta.title).replace(/\s/g, '')) log('  ⚠ 标题不一致');

log('填充正文…');
let i = 0;
for (const seg of segments) {
  i++;
  if (seg.type === 'html') await pasteHtml(seg.html);
  else if (seg.type === 'image') await insertImage(seg.url);
}

const after = await page.evaluate(() => {
  const e = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
  const body = e[e.length - 1];
  return {
    text: (body?.innerText || '').replace(/\s/g, '').length,
    imgs: body?.querySelectorAll('img').length || 0,
    community: [...document.querySelectorAll('[class*="community"], [class*="topic"]')]
      .map((x) => (x.textContent || '').trim()).filter((t) => t && t.length < 14).slice(0, 6),
  };
});
log(`  新正文 ${after.text} 字，图片 ${after.imgs} 张`);
log(`  关联: ${JSON.stringify(after.community)}`);

const shot = path.join(SHOT_DIR, `edited-${postId}-${Date.now()}.png`);
await page.screenshot({ path: shot, fullPage: false });
log('截图: ' + shot);

if (!DO_SAVE) {
  log('=== 安全模式：内容已填进编辑页，但【没有保存】 ===');
  log('你在浏览器里审核，确认后执行: node tools/update-post.mjs ' + postId + ' "' + file + '" --save');
  process.exit(0);
}

log('点击「修改」保存…');
await page.evaluate(() => {
  const btn = [...document.querySelectorAll('button')]
    .find((b) => (b.textContent || '').trim() === '修改');
  if (!btn) throw new Error('找不到「修改」按钮');
  btn.click();
});
await sleep(6000);

const finalUrl = page.url();
const finalText = await page.evaluate(() => (document.body?.innerText || '').slice(0, 600));
log('保存后 URL: ' + finalUrl);
log('页面提示: ' + finalText.replace(/\n+/g, ' ').slice(0, 300));

process.exit(0);
