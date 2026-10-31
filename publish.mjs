// publish.mjs —— 把 Markdown 文章发布到小黑盒
//
// 用法：
//   node publish.mjs articles/uncharted.md            # 只填充并截图，供人工确认（安全，默认）
//   node publish.mjs articles/uncharted.md --publish  # 填充后真的点发布
//
// 依赖常驻会话：node session.mjs（CDP 127.0.0.1:9222）
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadArticle } from './lib/md2xhh.mjs';

const argv = process.argv.slice(2);
const file = argv.find((a) => !a.startsWith('--'));
const DO_PUBLISH = argv.includes('--publish');
const DO_DRAFT = argv.includes('--draft');
// 项目根 = 本文件所在目录；截图写进项目内的 shots\。
// 必须用 fileURLToPath：import.meta.url 里的中文是百分号编码的（桌面 -> %E6%A1%8C%E9%9D%A2）。
const PROJECT_ROOT = path.dirname(fileURLToPath(import.meta.url));
const SHOT_DIR = path.join(PROJECT_ROOT, 'shots');
if (!file) { console.error('用法: node publish.mjs <文章.md> [--publish|--draft]'); process.exit(1); }
fs.mkdirSync(SHOT_DIR, { recursive: true });

const log = (...a) => console.log('[xhh]', ...a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const md = fs.readFileSync(path.resolve(file), 'utf8');
const { meta, segments } = loadArticle(md);
log(`文章: ${meta.title}`);
log(`片段: ${segments.length} 个（含 ${segments.filter((s) => s.type === 'image').length} 张图）`);

const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
const ctx = browser.contexts()[0];
const page = ctx.pages().find((p) => !p.url().startsWith('devtools://')) ?? ctx.pages()[0];

/* ---------------- 页面内工具（不使用 eval，避免 CSP 限制） ---------------- */

// which: 'title' | 'body'
const pick = `(which) => { const e=[...document.querySelectorAll('div.ProseMirror.hb-editor')]; return which==='title' ? e[0] : e[e.length-1]; }`;

async function focusEditor(which) {
  await page.evaluate(
    ({ which }) => {
      const e = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
      const ed = which === 'title' ? e[0] : e[e.length - 1];
      ed.focus();
    },
    { which }
  );
}

async function collapseToEnd(which) {
  await page.evaluate(
    ({ which }) => {
      const e = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
      const ed = which === 'title' ? e[0] : e[e.length - 1];
      ed.focus();
      const s = window.getSelection();
      const r = document.createRange();
      r.selectNodeContents(ed);
      r.collapse(false);
      s.removeAllRanges();
      s.addRange(r);
    },
    { which }
  );
}

async function clearEditor(which) {
  for (let attempt = 0; attempt < 2; attempt++) {
    await page.evaluate(
      ({ which }) => {
        const e = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
        const ed = which === 'title' ? e[0] : e[e.length - 1];
        ed.focus();
        const s = window.getSelection();
        const r = document.createRange();
        r.selectNodeContents(ed);
        s.removeAllRanges();
        s.addRange(r);
      },
      { which }
    );
    await page.keyboard.press('Delete');
    await sleep(500);
    const left = await page.evaluate(
      ({ which }) => {
        const e = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
        const ed = which === 'title' ? e[0] : e[e.length - 1];
        return (ed.innerText || '').replace(/[\u200b\s]/g, '').length;
      },
      { which }
    );
    if (left === 0) return;
    await focusEditor(which);
    await page.keyboard.press('Control+A');
    await page.keyboard.press('Delete');
    await sleep(500);
  }
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

async function clickText(text) {
  // 页面变长后按钮会在视口外；另外可能有 .t-mask 遮罩拦截鼠标事件。
  // 所以：先滚进视口 → 检测该点是否被遮挡 → 被挡就退回 JS 直接 click。
  const probe = await page.evaluate((t) => {
    const cands = [];
    document.querySelectorAll('*').forEach((el) => {
      if ((el.textContent || '').trim() !== t) return;
      const r = el.getBoundingClientRect();
      if (r.width <= 0 || r.height <= 0) return;
      let d = 0, p = el;
      while (p.parentElement) { d++; p = p.parentElement; }
      cands.push({ el, d });
    });
    if (!cands.length) return null;
    cands.sort((a, b) => b.d - a.d);
    const el = cands[0].el;
    el.scrollIntoView({ block: 'center', inline: 'center' });
    const r = el.getBoundingClientRect();
    const x = Math.round(r.x + r.width / 2);
    const y = Math.round(r.y + r.height / 2);
    const at = document.elementFromPoint(x, y);
    const blocked = !(at === el || el.contains(at) || at?.contains(el));
    return { x, y, blocked, blocker: at ? `${at.tagName}.${(at.className || '').toString().slice(0, 50)}` : null };
  }, text);

  if (!probe) throw new Error(`找不到可点元素: ${text}`);
  await sleep(350);

  if (probe.blocked) {
    log(`  (${text} 被 ${probe.blocker} 遮挡，改用 JS 点击)`);
    await page.evaluate((t) => {
      const cands = [];
      document.querySelectorAll('*').forEach((el) => {
        if ((el.textContent || '').trim() !== t) return;
        const r = el.getBoundingClientRect();
        if (r.width <= 0 || r.height <= 0) return;
        let d = 0, p = el;
        while (p.parentElement) { d++; p = p.parentElement; }
        cands.push({ el, d });
      });
      cands.sort((a, b) => b.d - a.d);
      cands[0].el.click();
    }, text);
  } else {
    const c2 = await page.evaluate((t) => {
      const cands = [];
      document.querySelectorAll('*').forEach((el) => {
        if ((el.textContent || '').trim() !== t) return;
        const r = el.getBoundingClientRect();
        if (r.width <= 0 || r.height <= 0) return;
        let d = 0, p = el;
        while (p.parentElement) { d++; p = p.parentElement; }
        cands.push({ el, d });
      });
      cands.sort((a, b) => b.d - a.d);
      const r = cands[0].el.getBoundingClientRect();
      return { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2) };
    }, text);
    await page.mouse.click(c2.x, c2.y);
  }
  return probe;
}

/** 清掉可能残留的遮罩/弹窗，避免后续点击被拦 */
async function dismissOverlays() {
  await page.keyboard.press('Escape').catch(() => {});
  await sleep(500);
  await page.keyboard.press('Escape').catch(() => {});
  await sleep(500);
  const n = await page.evaluate(() => {
    let removed = 0;
    document.querySelectorAll('.t-mask, .hb-cpt__mask-wrapper').forEach((m) => {
      // 只在它内部没有真实弹窗内容时才移除
      const hasDialog = m.querySelector('.editor__model-frame, .hb-cpt__dialog, [class*="model-frame"]');
      if (!hasDialog) { m.remove(); removed++; }
    });
    return removed;
  });
  if (n) log(`  清理了 ${n} 个残留遮罩`);
  await sleep(300);
}

/** 给 Vue 绑定的 input 赋值（必须用原生 setter 才能触发更新） */
async function setInput(selector, value) {
  await page.evaluate(
    ({ selector, value }) => {
      const inp = document.querySelector(selector);
      if (!inp) throw new Error('no input ' + selector);
      inp.focus();
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      setter.call(inp, value);
      inp.dispatchEvent(new Event('input', { bubbles: true }));
      inp.dispatchEvent(new Event('change', { bubbles: true }));
    },
    { selector, value }
  );
}

async function insertImage(src) {
  const isLocal = !/^https?:\/\//i.test(src);
  await collapseToEnd('body');
  // 先清残留遮罩，否则点击会被 .t-mask 拦掉
  await page.evaluate(() => document.querySelectorAll('.t-mask').forEach((m) => m.remove()));
  await page.evaluate(() => document.querySelector('button[data-name="插入图片"]')?.click());
  await page.waitForSelector('.hb-cpt__mask-wrapper', { timeout: 15000 });
  await sleep(700);

  if (isLocal) {
    // 本地上传：点上传框 → 接 filechooser
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
    await setInput('.hb-cpt__mask-wrapper input.hb-cpt__input-item', src);
    await sleep(400);
    await page.evaluate(() => document.querySelector('.hb-cpt__mask-wrapper .editor-model__import-btn')?.click());
  }

  await page
    .waitForFunction(
      () => {
        const m = document.querySelector('.hb-cpt__mask-wrapper');
        if (!m) return false;
        return [...m.querySelectorAll('img')].some((i) => i.src.includes('imgheybox'));
      },
      { timeout: 60000 }
    )
    .catch(() => log('  ⚠ 图片上传等待超时，仍尝试确认'));
  await sleep(900);

  await page.evaluate(() =>
    document.querySelector('.hb-cpt__mask-wrapper .editor-__model-frame-bottom-btn.hb-color__btn--confirm')?.click()
  );
  await sleep(1300);
}

async function selectCommunity(name) {
  await clickText('添加社区');
  await page.waitForSelector('.hb-cpt__mask-wrapper', { timeout: 15000 });
  await sleep(700);
  await setInput('.hb-cpt__mask-wrapper input.editor__search-input--input', name);
  await sleep(4000);

  const picked = await page.evaluate((kw) => {
    const m = document.querySelector('.hb-cpt__mask-wrapper');
    if (!m) return null;
    const items = [...m.querySelectorAll('.editor-model__topic-list-item')];
    if (!items.length) return null;
    const titleOf = (it) => it.querySelector('.topic-list-item__title')?.textContent?.trim() || '';
    const hit = items.find((it) => titleOf(it) === kw)
             || items.find((it) => titleOf(it).includes(kw))
             || items[0];
    const r = hit.getBoundingClientRect();
    return { title: titleOf(hit), x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2) };
  }, name);

  if (!picked) throw new Error(`社区搜索无结果: ${name}`);
  // 先鼠标点，没生效就退回 JS 点击（页面上常驻 .t-mask 会拦鼠标事件）
  await page.mouse.click(picked.x, picked.y);
  await sleep(1800);
  let closed = await page.evaluate(() => !document.querySelector('.hb-cpt__mask-wrapper'));
  if (!closed) {
    await page.evaluate((t) => {
      const dead = document.querySelector('.t-mask');
      if (dead) dead.remove();
      const items = [...document.querySelectorAll('.editor-model__topic-list-item')];
      const hit = items.find(
        (it) => (it.querySelector('.topic-list-item__title')?.textContent || '').trim() === t
      ) || items[0];
      hit?.click();
    }, picked.title);
    await sleep(2000);
    closed = await page.evaluate(() => !document.querySelector('.hb-cpt__mask-wrapper'));
  }
  log(`  社区已选 → ${picked.title}${closed ? '' : '（弹窗未关闭，请人工确认）'}`);
  return picked.title;
}

async function addTopic(name) {
  try {
    await clickText('添加话题');
    await page.waitForSelector('.hb-cpt__mask-wrapper', { timeout: 10000 });
    await sleep(700);
    await setInput('.hb-cpt__mask-wrapper input.editor__search-input--input', name);
    await sleep(3500);
    const picked = await page.evaluate(() => {
      const m = document.querySelector('.hb-cpt__mask-wrapper');
      const it = m?.querySelector('.editor-model__topic-list-item');
      if (!it) return null;
      const r = it.getBoundingClientRect();
      return {
        title: it.querySelector('.topic-list-item__title')?.textContent?.trim(),
        x: Math.round(r.x + r.width / 2),
        y: Math.round(r.y + r.height / 2),
      };
    });
    if (!picked) {
      log(`  ⚠ 话题无结果，跳过: ${name}`);
      await page.keyboard.press('Escape');
      return;
    }
    await page.mouse.click(picked.x, picked.y);
    await sleep(2000);
    log(`  话题已加 → ${picked.title}`);
  } catch (e) {
    log(`  ⚠ 话题添加失败（跳过）: ${e.message}`);
    await page.keyboard.press('Escape').catch(() => {});
  }
}

/** 勾选「其他声明 → 包含AI辅助创作」（发布设置里，不在“内容声明”那栏） */
async function setAiDeclaration() {
  const open = await page.evaluate(() => {
    const items = [...document.querySelectorAll('.creator-editor__form-item')];
    const item = items.find(
      (it) => (it.querySelector('.creator-editor__form-label')?.textContent || '').trim() === '其他声明'
    );
    if (!item) return { ok: false, why: '没找到「其他声明」这一项' };
    const box = item.querySelector('.selector__box');
    if (!box) return { ok: false, why: '没找到下拉框' };
    box.scrollIntoView({ block: 'center' });
    document.querySelectorAll('.t-mask').forEach((m) => m.remove());
    box.click();
    return { ok: true };
  });
  if (!open.ok) { log(`  ⚠ AI 声明：${open.why}`); return false; }
  await sleep(1200);

  const picked = await page.evaluate(() => {
    const all = [...document.querySelectorAll('.selector__pull-list-item')];
    const hit = all.find((e) => (e.textContent || '').trim() === '包含AI辅助创作');
    if (!hit) return { ok: false, why: '下拉里没有「包含AI辅助创作」', saw: all.map((e) => (e.textContent || '').trim()) };
    document.querySelectorAll('.t-mask').forEach((m) => m.remove());
    hit.click();
    return { ok: true };
  });
  await sleep(1200);

  if (!picked.ok) { log(`  ⚠ AI 声明：${picked.why} 现有选项=${JSON.stringify(picked.saw)}`); return false; }

  const confirmed = await page.evaluate(() => {
    const items = [...document.querySelectorAll('.creator-editor__form-item')];
    const item = items.find(
      (it) => (it.querySelector('.creator-editor__form-label')?.textContent || '').trim() === '其他声明'
    );
    return (item?.querySelector('.selector__active')?.textContent || '').trim();
  });
  log(`  其他声明 = ${confirmed}`);
  return confirmed.includes('AI');
}

/* ---------------- 主流程 ---------------- */

log('打开创作页…');
await page.goto('https://www.xiaoheihe.cn/', { waitUntil: 'domcontentloaded', timeout: 60000 });
await sleep(3500);
await clickText('发布内容');
await sleep(5500);

const clickedTab = await page.evaluate(() => {
  const t = [...document.querySelectorAll('.slide-tab__tab-item')].find(
    (e) => (e.textContent || '').trim() === '发布文章'
  );
  if (!t) return false;
  if (!t.className.includes('active')) { t.click(); return true; }
  return false;
});
if (clickedTab) await sleep(5500);
log('编辑器 URL: ' + page.url());

await page.waitForFunction(() => document.querySelectorAll('div.ProseMirror.hb-editor').length >= 2, {
  timeout: 30000,
});
await sleep(1500);

// 标题
log('填写标题…');
await clearEditor('title');
await focusEditor('title');
await page.keyboard.insertText(meta.title);
await sleep(1300);
const gotTitle = await page.evaluate(() => {
  const e = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
  return (e[0].innerText || '').trim();
});
log('  标题 = ' + gotTitle);
if (gotTitle.replace(/\s/g, '') !== String(meta.title).replace(/\s/g, '')) log('  ⚠ 标题不一致（可能超 30 字被截断）');

// 正文
log('填充正文…');
await clearEditor('body');
let want = 0;
for (const [i, seg] of segments.entries()) {
  if (seg.type === 'html') await pasteHtml(seg.html);
  else {
    want++;
    log(`  [${i + 1}/${segments.length}] 插图 ${want}…`);
    await insertImage(seg.url);
  }
}
const bodyStat = await page.evaluate(() => {
  const e = [...document.querySelectorAll('div.ProseMirror.hb-editor')];
  const ed = e[e.length - 1];
  return { chars: (ed.innerText || '').replace(/\s/g, '').length, imgs: ed.querySelectorAll('img').length };
});
log(`  正文 ${bodyStat.chars} 字，图片 ${bodyStat.imgs}/${want} 张`);

// 社区
log('选择社区…');
await selectCommunity(meta.community);

// 话题
if (meta.topics) {
  for (const t of String(meta.topics).split(/[,，]/).map((s) => s.trim()).filter(Boolean)) {
    log(`添加话题: ${t}`);
    await addTopic(t);
  }
}

// AI 辅助创作声明（frontmatter 里 ai: true 时勾选）
if (String(meta.ai).toLowerCase() === 'true') {
  log('勾选 AI 辅助创作声明…');
  await setAiDeclaration();
}

// 存证截图
const shot = path.join(SHOT_DIR, `filled-${Date.now()}.png`);
await page.screenshot({ path: shot, fullPage: false });
log('截图: ' + shot);

const counts = await page.evaluate(() =>
  [...document.querySelectorAll('.editor__more-info-desc')].map((e) => e.textContent.trim())
);
log('关联计数: ' + JSON.stringify(counts));

// 创作计划 / 创作任务：开关默认「不参与」，要主动切到「参与」
// 注意：实测这两项**存不进草稿**（存草稿后重开还是「不参与」），
// 而且提前切换会干扰草稿保存（会退化成 local_ 本地草稿）。
// 所以只在真正发布时才动它们。
async function joinCreationPlans(which = '文章计划') {
  for (const [name, sel] of [['创作计划', '.creation-plan-join'], ['创作任务', '.cm-task-join']]) {
    const state = await page.evaluate((s) => {
      const el = document.querySelector(s);
      if (!el) return 'missing';
      return el.querySelector('.switch__true-label.active') ? 'on' : 'off';
    }, sel);
    if (state === 'missing') { log(`  ⚠ ${name}: 没找到开关`); continue; }
    if (state === 'off') {
      await page.click(`${sel} .switch__button`, { timeout: 8000 }).catch(() => {});
      await sleep(800);
    }
    const now = await page.evaluate((s) => {
      const el = document.querySelector(s);
      return el?.querySelector('.switch__true-label.active') ? 'on' : 'off';
    }, sel);
    log(`  ${name}: ${now === 'on' ? '参与' : '不参与'}`);
  }

  // 「选择计划」下面有两个单选项：文章计划 / 热点计划，必须二选一
  await sleep(900);
  const picked = await page.evaluate((want) => {
    const labels = [...document.querySelectorAll('label, span, div')]
      .filter((e) => e.children.length === 0 && (e.textContent || '').trim() === want);
    if (!labels.length) return 'label-not-found';
    const el = labels[0];
    el.scrollIntoView({ block: 'center' });
    el.click();
    return 'clicked';
  }, which).catch(() => 'err');
  await sleep(900);
  const checked = await page.evaluate((want) => {
    const labels = [...document.querySelectorAll('label, span, div')]
      .filter((e) => e.children.length === 0 && (e.textContent || '').trim() === want);
    if (!labels.length) return '?';
    const r = labels[0].closest('label')?.querySelector('input') || labels[0].parentElement?.querySelector('input');
    return r ? (r.checked ? 'checked' : 'unchecked') : 'no-input';
  }, which);
  log(`  选择计划 → ${which}（${picked} / ${checked}）`);
}

if (DO_DRAFT) {
  log('保存到服务器草稿箱…');
  await clickText('保存草稿');
  await sleep(4500);

  // 保存后页面可能弹提示，或直接留在编辑器
  const after = await page.evaluate(() => ({
    url: location.href,
    text: (document.body.innerText || '').replace(/\s+/g, ' ').slice(0, 200),
  }));
  log('  当前 URL: ' + after.url);
  log('  页面提示: ' + after.text.slice(0, 160));

  const savedShot = path.join(SHOT_DIR, `draft-saved-${Date.now()}.png`);
  await page.screenshot({ path: savedShot, fullPage: false });
  log('截图: ' + savedShot);

  // 去草稿箱核对是否出现
  log('去草稿箱核对…');
  await page.goto('https://www.xiaoheihe.cn/creator/draft', { waitUntil: 'domcontentloaded', timeout: 45000 });
  await sleep(4500);
  const list = await page.evaluate(() =>
    [...document.querySelectorAll('.creator-draft__content')].map((e) => (e.textContent || '').trim()).slice(0, 12)
  );
  log('  草稿箱前几条: ' + JSON.stringify(list, null, 0));
  const titleOk = list.some((t) => t && String(meta.title).includes(t.slice(0, 8)));
  log(`  ${titleOk ? '✅ 已出现在草稿箱' : '⚠️ 没在草稿箱前几条里看到，可能位置靠后'}`);
  process.exit(0);
}

if (!DO_PUBLISH) {
  log('=== 安全模式：未发布 ===');
  log('确认无误后执行: node publish.mjs "' + file + '" --publish');
  log('或存进草稿箱:   node publish.mjs "' + file + '" --draft');
  process.exit(0);
}

log('点击发布…');
// 按 frontmatter 的 plan 字段决定参不参与：
//   plan: false → 不参与（新闻类本来就不符合「非新闻」条件，报了也拿不到钱）
//   缺省或其它 → 参与
if (String(meta.plan).toLowerCase() === 'false') {
  log('  frontmatter 写的是 plan: false → 跳过创作计划');
} else {
  // plan: hot → 热点计划；其它（true/缺省）→ 文章计划
  const which = String(meta.plan).toLowerCase() === 'hot' ? '热点计划' : '文章计划';
  log(`设置创作计划 / 创作任务…（${which}）`);
  await joinCreationPlans(which);
}
await clickText('发布');
await sleep(5500);

const confirmed = await page.evaluate(() => {
  const btns = [...document.querySelectorAll('button')].filter((b) => {
    const t = (b.textContent || '').trim();
    const r = b.getBoundingClientRect();
    return r.width > 0 && ['确定', '确认发布', '继续发布'].includes(t);
  });
  if (!btns.length) return false;
  btns[0].click();
  return true;
});
if (confirmed) { log('  已处理二次确认'); await sleep(6000); }

await page.screenshot({ path: path.join(SHOT_DIR, `published-${Date.now()}.png`) });
const after = await page.evaluate(() => ({
  url: location.href,
  text: (document.body.innerText || '').replace(/\s+/g, ' ').slice(0, 250),
}));
log('发布后 URL: ' + after.url);
log('页面提示: ' + after.text);

process.exit(0);
