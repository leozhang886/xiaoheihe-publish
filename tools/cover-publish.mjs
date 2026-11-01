// tools/cover-publish.mjs —— 自包含：起浏览器 → 开草稿 → 选计划 → 上传内容封面 →（可选）发布
//
// 用法:
//   node tools/cover-publish.mjs --draft-id 195484475 --cover "assets/_上传用封面/01 xxx.png" [--publish]
//   node tools/cover-publish.mjs --title "文章标题" --cover "..." [--publish]
//
// 踩出来的关键知识（顺序不能改）：
//   1. 「内容封面」字段只在勾了「创作计划」+ 选中「文章计划」之后才出现在 DOM 里
//   2. 「修改封面」按钮只在 hover 缩略图后才渲染；page.hover('text=修改封面') 最稳
//   3. 弹窗里没有静态 input[type=file]，必须点「点击上传」并监听 filechooser 事件
//   4. 封面为空时点「发布」是静默失败（无提示、URL 不变）
//   5. 弹窗要求：≤10MB，推荐 >1275×680，最低 900×480；白底白边图可能过不了审核

import { chromium } from 'playwright';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const PROJECT_ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const PROFILE = path.join(PROJECT_ROOT, 'profile');
const SHOTS = path.join(PROJECT_ROOT, 'shots');
fs.mkdirSync(SHOTS, { recursive: true });

const argv = process.argv.slice(2);
const arg = (k, d = null) => {
  const i = argv.indexOf(k);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : d;
};
const TITLE = arg('--title');
const COVER = arg('--cover');
const DRAFT_ID = arg('--draft-id');
const DO_PUBLISH = argv.includes('--publish');
const PLAN = (arg('--plan', 'article') || 'article').toLowerCase();   // article | hot
const PLAN_LABEL = PLAN === 'hot' ? '热点计划' : '文章计划';

if (!COVER || (!DRAFT_ID && !TITLE)) {
  console.error('用法: node tools/cover-publish.mjs (--draft-id ID | --title "标题") --cover "封面路径" [--publish]');
  process.exit(1);
}

const log = (m) => console.log('[cv] ' + m);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const shot = (name) => path.join(SHOTS, `${name}-${Date.now()}.png`);

let ctx = null;
let page = null;
let closingByScript = false;

async function closeAll() {
  closingByScript = true;
  await ctx?.close().catch(() => {});
}

try {
  ctx = await chromium.launchPersistentContext(PROFILE, {
    headless: false,
    viewport: { width: 1600, height: 1000 },
    args: ['--disable-blink-features=AutomationControlled'],
  });
  page = ctx.pages()[0] ?? (await ctx.newPage());

  page.on('crash', () => log('PAGE_CRASH'));
  page.on('close', () => log('PAGE_CLOSE' + (closingByScript ? ' (script-initiated)' : '')));
  ctx.on('close', () => log('CTX_CLOSE' + (closingByScript ? ' (script-initiated)' : '')));

  // ---------- 1. 打开草稿 ----------
  if (DRAFT_ID) {
    await page.goto(`https://www.xiaoheihe.cn/creator/editor/edit/article/${DRAFT_ID}`, {
      waitUntil: 'domcontentloaded', timeout: 60000,
    });
    log(`打开草稿 ${DRAFT_ID}`);
  } else {
    await page.goto('https://www.xiaoheihe.cn/creator/draft', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await sleep(5000);
    const ok = await page.evaluate((t) => {
      const el = [...document.querySelectorAll('*')].find((e) => e.children.length === 0 && (e.textContent || '').trim() === t);
      if (!el) return false;
      el.scrollIntoView({ block: 'center' });
      el.click();
      return true;
    }, TITLE);
    if (!ok) throw new Error(`草稿箱里没找到「${TITLE}」`);
    log('从草稿箱点进去');
    await sleep(9000);
  }
  log('URL: ' + page.url());

  // ---------- 2. 勾创作计划 ----------
  let planVisible = false;
  for (let i = 0; i < 15; i++) {
    await page.evaluate(() => window.scrollBy(0, 700));
    await sleep(900);
    planVisible = await page.evaluate(() => !!document.querySelector('.creation-plan-join'));
    if (planVisible) break;
  }
  if (!planVisible) throw new Error('找不到「创作计划」开关（页面可能没加载出来）');

  const planOn = await page.evaluate(() =>
    !!document.querySelector('.creation-plan-join')?.querySelector('.switch__true-label.active')
  );
  if (!planOn) {
    await page.click('.creation-plan-join .switch__button', { timeout: 8000 }).catch(() => {});
    await sleep(2000);
  }
  log('创作计划: 参与');

  // ---------- 3. 选「文章计划」 ----------
  let planPicked = 'no-label';
  for (let i = 0; i < 15; i++) {
    planPicked = await page.evaluate((WANT_PLAN) => {
      const want = WANT_PLAN;
      const el = [...document.querySelectorAll('.radio__select-label, label, span')].find(
        (e) => e.children.length === 0 && (e.textContent || '').trim() === want
      );
      if (!el) return 'no-label';
      el.scrollIntoView({ block: 'center' });
      el.click();
      return 'clicked';
    }, PLAN_LABEL);
    if (planPicked === 'clicked') break;
    await page.evaluate(() => window.scrollBy(0, 300));
    await sleep(1000);
  }
  log(PLAN_LABEL + ': ' + planPicked);
  if (planPicked !== 'clicked') throw new Error('选不到「' + PLAN_LABEL + '」');
  await sleep(3000);

  // ---------- 4. 等「内容封面」出现 ----------
  let hasCoverField = false;
  for (let i = 0; i < 20; i++) {
    await page.evaluate(() => window.scrollBy(0, 600));
    await sleep(900);
    hasCoverField = await page.evaluate(() =>
      [...document.querySelectorAll('.creator-editor__form-label')].some((e) => (e.textContent || '').trim() === '内容封面')
    );
    if (hasCoverField) { log(`第 ${i + 1} 轮找到「内容封面」`); break; }
  }
  if (!hasCoverField) {
    const labels = await page.evaluate(() =>
      [...document.querySelectorAll('.creator-editor__form-label')].map((e) => (e.textContent || '').trim())
    );
    throw new Error('没有「内容封面」字段。现有: ' + JSON.stringify(labels));
  }
  await page.evaluate(() => {
    const lbl = [...document.querySelectorAll('.creator-editor__form-label')].find((e) => (e.textContent || '').trim() === '内容封面');
    lbl?.closest('.creator-editor__form-item')?.scrollIntoView({ block: 'center' });
  });
  await sleep(1200);

  // ---------- 5. 悬停缩略图 → 点「修改封面」----------
  const thumb = await page.evaluate(() => {
    const lbl = [...document.querySelectorAll('.creator-editor__form-label')].find((e) => (e.textContent || '').trim() === '内容封面');
    const row = lbl?.closest('.creator-editor__form-item');
    const el = row?.querySelector('.thumb-card__right') || row?.querySelector('.hb-cpt__image') || row?.querySelector('img');
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2) };
  });
  log('缩略图位置: ' + JSON.stringify(thumb));
  if (thumb) {
    for (const p of [[0, 0], [8, 0], [0, 8], [0, 0]]) {
      await page.mouse.move(thumb.x + p[0], thumb.y + p[1], { steps: 6 });
      await sleep(500);
    }
  }

  let modalOpened = false;
  try {
    await page.hover('text=修改封面', { timeout: 8000 });
    await page.click('text=修改封面', { timeout: 8000 });
    modalOpened = true;
    log('点中「修改封面」');
  } catch (e) {
    log('文本定位失败: ' + e.message.split('\n')[0]);
  }
  if (!modalOpened) throw new Error('点不到「修改封面」');
  await sleep(3500);

  const modalTitle = await page.evaluate(() =>
    [...document.querySelectorAll('*')].some((e) => e.children.length === 0 && (e.textContent || '').trim() === '上传封面')
      ? '上传封面' : '没检测到弹窗标题'
  );
  log('弹窗: ' + modalTitle);

  // ---------- 6. 上传：点「点击上传」并监听 filechooser ----------
  const staticInput = await page.$('input[type=file]');
  if (staticInput) {
    await staticInput.setInputFiles(COVER);
    log('用静态 input 上传');
  } else {
    const fcPromise = page.waitForEvent('filechooser', { timeout: 15000 }).catch(() => null);
    const clicked = await page.evaluate(() => {
      const el = [...document.querySelectorAll('*')].find(
        (e) => e.children.length === 0 && ['点击上传', '点击选择', '上传图片', '选择图片'].includes((e.textContent || '').trim())
      );
      if (!el) return false;
      el.scrollIntoView({ block: 'center' });
      el.click();
      return true;
    });
    log('点「点击上传」: ' + clicked);
    let chooser = await fcPromise;
    if (!chooser) {
      const fc2 = page.waitForEvent('filechooser', { timeout: 12000 }).catch(() => null);
      await page.click('text=点击上传', { timeout: 8000 }).catch(() => {});
      chooser = await fc2;
    }
    if (!chooser) {
      await page.screenshot({ path: shot('no-chooser') });
      throw new Error('点击上传后没有出现文件选择框');
    }
    await chooser.setFiles(COVER);
    log('文件已提交: ' + path.basename(COVER));
  }
  await sleep(9000);

  // ---------- 7. 点「确定」 ----------
  const confirmed = await page.evaluate(() => {
    const b = [...document.querySelectorAll('button, [class*=btn], div')].find((e) => {
      const t = (e.textContent || '').trim();
      const r = e.getBoundingClientRect();
      return r.width > 0 && t === '确定';
    });
    if (!b) return false;
    b.click();
    return true;
  });
  log('点「确定」: ' + confirmed);
  await sleep(6000);

  // ---------- 8. 校验封面 ----------
  const coverSrc = await page.evaluate(() => {
    const lbl = [...document.querySelectorAll('.creator-editor__form-label')].find((e) => (e.textContent || '').trim() === '内容封面');
    const row = lbl?.closest('.creator-editor__form-item');
    const img = row?.querySelector('img');
    return img ? (img.getAttribute('src') || '(空)').slice(0, 90) : '(没有 img 元素)';
  });
  log('封面 img src: ' + coverSrc);
  await page.screenshot({ path: shot('cover-result') });

  // ---------- 8.5 保存草稿，把封面持久化 ----------
  const saved = await page.evaluate(() => {
    const el = [...document.querySelectorAll('*')].find(
      (e) => e.children.length === 0 && (e.textContent || '').trim() === '保存草稿'
    );
    if (!el) return false;
    el.scrollIntoView({ block: 'center' });
    el.click();
    return true;
  });
  log('保存草稿: ' + saved);
  await sleep(6000);
  log('保存后 URL: ' + page.url());

  if (!DO_PUBLISH) {
    log('没加 --publish，停在这里。');
    await closeAll();
    process.exit(0);
  }

  // ---------- 9. 发布 ----------
  log('点发布…');
  await page.click('.editor-publish__btn.main-btn', { timeout: 15000 });
  await sleep(7000);
  const after = await page.evaluate(() => ({
    url: location.href,
    text: (document.body.innerText || '').replace(/\s+/g, ' ').slice(0, 150),
  }));
  log('发布后 URL: ' + after.url);
  log('页面: ' + after.text.slice(0, 100));
  await page.screenshot({ path: shot('published') });

  await closeAll();
  process.exit(0);
} catch (e) {
  log('❌ ' + e.message);
  try { await page?.screenshot({ path: shot('err') }); } catch {}
  log('ERROR_STATE pageClosed=' + (page ? page.isClosed() : 'no-page'));
  await closeAll();
  process.exit(1);
}
