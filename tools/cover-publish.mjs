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
const FORCE_SKIP_COVER = argv.includes('--skip-cover');
const PLAN = (arg('--plan', 'article') || 'article').toLowerCase();   // article | hot
const PLAN_LABEL = PLAN === 'hot' ? '热点计划' : '文章计划';

if (!COVER || (!DRAFT_ID && !TITLE)) {
  console.error('用法: node tools/cover-publish.mjs (--draft-id ID | --title "标题") --cover "封面路径" [--publish]');
  process.exit(1);
}

const log = (m) => console.log('[cv] ' + m);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const shot = (name) => path.join(SHOTS, `${name}-${Date.now()}.png`);

/**
 * 点掉「你还有上次未发布的内容」这条提示。
 * 它会一直挂在页面顶部，且渲染得比检查时机晚，所以要在多个位置调用。
 */
async function clearStaleBanner() {
  const hit = await page.evaluate(() => {
    const t = document.body.innerText || '';
    if (!/上次未发布的内容/.test(t)) return null;
    for (const el of document.querySelectorAll('span, button, div, a')) {
      if (el.children.length === 0 && (el.textContent || '').trim() === '忽略') {
        const r = el.getBoundingClientRect();
        if (r.width > 0) return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
      }
    }
    return null;
  }).catch(() => null);
  if (!hit) return false;
  await page.mouse.click(hit.x, hit.y);
  log('已点掉「上次未发布内容」提示');
  await sleep(3500);
  return true;
}

/** 失败时把页面真实状态存成 JSON，方便定位 */
async function dumpState(tag) {
  try {
    const st = await page.evaluate(() => {
      const txt = document.body.innerText || '';
      const btnTexts = [...document.querySelectorAll('button, .editor__add-btn, .editor-publish__btn')]
        .filter((e) => e.offsetParent !== null)
        .map((e) => (e.textContent || '').trim().slice(0, 24))
        .filter(Boolean);
      const items = [...document.querySelectorAll('.creator-editor__form-item')].map((it) =>
        (it.querySelector('.creator-editor__form-label')?.textContent || '').trim()
      );
      return {
        url: location.href,
        hasBanner: /上次未发布的内容/.test(txt),
        hasPublishPanel: items.length > 0,
        formItems: items,
        buttons: [...new Set(btnTexts)].slice(0, 30),
        hasMask: !!document.querySelector('.hb-cpt__mask-wrapper'),
        hasFileInput: !!document.querySelector('input[type=file]'),
        hasCaptcha: !!document.querySelector('#tcaptcha_iframe_dy, iframe[src*=turing]'),
        textHead: txt.replace(/\s+/g, ' ').slice(0, 300),
      };
    });
    const f = path.join(SHOTS, `state-${tag}-${Date.now()}.json`);
    fs.writeFileSync(f, JSON.stringify(st, null, 2));
    log('状态已存: ' + path.basename(f));
    log('  URL: ' + st.url);
    log('  发布设置面板: ' + st.hasPublishPanel + '  项: ' + JSON.stringify(st.formItems));
    log('  遗留提示: ' + st.hasBanner + '  弹窗: ' + st.hasMask + '  file input: ' + st.hasFileInput + '  验证码: ' + st.hasCaptcha);
    log('  可见按钮: ' + JSON.stringify(st.buttons));
    return st;
  } catch (e) {
    log('dumpState 失败: ' + e.message.split('\n')[0]);
    return null;
  }
}

/**
 * 检测是否弹出了「安全验证」，弹了就等人来点。
 * 这是把控制权交回真人——不自动过验证码。
 */
async function waitForCaptcha(label = '') {
  // 腾讯验证码经常渲染在 iframe 里，主文档 innerText 取不到，所以要多种判断
  const hasCaptcha = () =>
    page.evaluate(() => {
      // 1) 主文档里能直接看到验证文字
      const txt = document.body.innerText || '';
      if (/安全验证|请依次点击|拖动滑块|点击完成验证|点击按钮完成/.test(txt)) return true;

      // 2) 任意 iframe 的 src / id / class 像验证码
      for (const f of document.querySelectorAll('iframe')) {
        const sig = [f.src, f.id, f.className, f.getAttribute('name')].filter(Boolean).join(' ');
        if (/captcha|tcaptcha|verify|yidun|geetest|punish|verifyframe/i.test(sig)) return true;
      }

      // 3) 常见验证码容器
      if (document.querySelector(
        '[class*=tcaptcha],[id*=tcaptcha],[class*=captcha],[id*=captcha],[class*=yidun],[class*=geetest]'
      )) return true;

      return false;
    }).catch(() => false);

  if (!(await hasCaptcha())) return false;

  log('🔒 检测到安全验证（' + (label || '页面') + '）——请在浏览器窗口里手动完成');
  log('   我会一直等，完成后自动继续。最多等 10 分钟。');
  const deadline = Date.now() + 10 * 60 * 1000;
  while (Date.now() < deadline) {
    await sleep(3000);
    if (!(await hasCaptcha())) {
      log('✅ 验证已通过，继续');
      await sleep(2000);
      return true;
    }
  }
  throw new Error('等待安全验证超时（10 分钟）——请手动发这篇');
}

let ctx = null;
let page = null;
let closingByScript = false;
let SHARED = false;
let browser = null;

async function closeAll() {
  closingByScript = true;
  if (SHARED) {
    // 共用浏览器：只关自己开的标签页，不关整个浏览器
    await page?.close().catch(() => {});
  } else {
    await ctx?.close().catch(() => {});
  }
}

try {
  // 优先连已经开着的浏览器（session.mjs 常驻在 9222）。
  // 这样不会反复启停同一个 profile——反复开关会留下残留编辑状态，也更容易触发验证码。
  try {
    browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
    SHARED = true;
    ctx = browser.contexts()[0] ?? (await browser.newContext());
    page = await ctx.newPage();
    log('已连接常驻浏览器（9222）');
  } catch {
    log('9222 没开，自己起一个');
    ctx = await chromium.launchPersistentContext(PROFILE, {
      headless: false,
      viewport: { width: 1600, height: 1000 },
      args: ['--disable-blink-features=AutomationControlled'],
    });
    page = ctx.pages()[0] ?? (await ctx.newPage());
  }

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

  // 打开草稿后可能弹出「你还有上次未发布的内容」提示，它会挡住整个发布设置
  const banner = await page.evaluate(() => {
    const t = document.body.innerText || '';
    if (!/上次未发布的内容/.test(t)) return null;
    for (const el of document.querySelectorAll('span, button, div, a')) {
      if (el.children.length === 0 && ['忽略', '继续编辑'].includes((el.textContent || '').trim())) {
        const r = el.getBoundingClientRect();
        if (r.width > 0) return { text: el.textContent.trim(), x: r.x + r.width / 2, y: r.y + r.height / 2 };
      }
    }
    return { text: 'not-found' };
  });
  if (banner) {
    log('检测到「上次未发布内容」提示: ' + banner.text);
    if (banner.x) {
      await page.mouse.click(banner.x, banner.y);
      log('已点「忽略」，等页面重载发布设置');
      await sleep(4000);
    }
  }

  // 打开后可能先弹验证
  await waitForCaptcha('打开草稿后');

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
  if (planPicked !== 'clicked') {
    // 很可能是验证码盖住了页面，让人处理完再试一次
    const had = await waitForCaptcha('选计划时');
    if (had) {
      for (let i = 0; i < 8; i++) {
        planPicked = await page.evaluate((WANT_PLAN) => {
          const el = [...document.querySelectorAll('.radio__select-label, label, span')].find(
            (e) => e.children.length === 0 && (e.textContent || '').trim() === WANT_PLAN
          );
          if (!el) return 'no-label';
          el.scrollIntoView({ block: 'center' });
          el.click();
          return 'clicked';
        }, PLAN_LABEL);
        if (planPicked === 'clicked') break;
        await page.evaluate(() => window.scrollBy(0, 300));
        await sleep(1200);
      }
    }
  }
  log(PLAN_LABEL + ': ' + planPicked);
  if (planPicked !== 'clicked') throw new Error('选不到「' + PLAN_LABEL + '」');
  await sleep(3000);

  // 选完计划后再查一次「上次未发布内容」提示——它经常是延迟渲染的，
  // 不点掉会让后面的「点击上传」点不动（按钮在但被浮层挡住/文案不同）
  await clearStaleBanner();

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

  // 封面已经传过的话，弹窗打开会是裁剪状态，没有「点击上传」按钮，硬走会卡死。
  const coverAlready = await page.evaluate(() => {
    const lbl = [...document.querySelectorAll('.creator-editor__form-label')].find(
      (e) => (e.textContent || '').trim() === '内容封面'
    );
    const row = lbl?.closest('.creator-editor__form-item');
    if (!row) return false;
    // 没封面时这里也有一个占位 img（.hb-cpt__image--default），不能算"已有图"
    const img = row.querySelector('img');
    if (!img) return false;
    if (img.classList.contains('hb-cpt__image--default')) return false;
    if (img.closest('.hb-cpt__image--default')) return false;
    return img.complete && img.naturalWidth > 50;
  }).catch(() => false);

  if (FORCE_SKIP_COVER) log('指定了 --skip-cover，跳过上传');
  const doSkip = coverAlready || FORCE_SKIP_COVER;
  if (coverAlready) log('内容封面已有图，跳过上传步骤');
  if (!doSkip) {
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
      // 兜底一：弹窗打开后可能才动态生成 input[type=file]
      const dyn = await page.$('.hb-cpt__mask-wrapper input[type=file], input[type=file]');
      if (dyn) {
        await dyn.setInputFiles(COVER);
        log('用点击后出现的 input 上传');
        chooser = { done: true };
      }
    }
    if (!chooser) {
      // 兜底二：重载页面再走一次（弹窗没正常挂载时有效）
      log('⚠ 没出文件选择框，重载页面重试一次');
      await page.reload({ waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
      await sleep(9000);
      const reopen = await page.evaluate(() => {
        const el = [...document.querySelectorAll('.editor__add-btn, span, button')].find(
          (e) => (e.textContent || '').trim() === '修改封面'
        );
        return !!el;
      }).catch(() => false);
      log('重载后页面可用: ' + reopen);
      const fc3 = page.waitForEvent('filechooser', { timeout: 15000 }).catch(() => null);
      await page.evaluate(() => {
        const el = [...document.querySelectorAll('*')].find(
          (e) => e.children.length === 0 && ['点击上传', '点击选择', '上传图片', '选择图片'].includes((e.textContent || '').trim())
        );
        if (el) { el.scrollIntoView({ block: 'center' }); el.click(); }
      }).catch(() => {});
      chooser = await fc3;
      if (!chooser) {
        const dyn2 = await page.$('input[type=file]').catch(() => null);
        if (dyn2) { await dyn2.setInputFiles(COVER); log('重载后用 input 上传'); chooser = { done: true }; }
      }
    }
    if (!chooser) {
      await page.screenshot({ path: shot('no-chooser') });
      await dumpState('no-chooser');
      throw new Error('点击上传后没有出现文件选择框（已重试一次）');
    }
    if (!chooser.done) await chooser.setFiles(COVER);
    log('文件已提交: ' + path.basename(COVER));
  }
  // 等裁剪区里的图片真正加载出来，再点确定（原来死等 14s，图没出来就会传成空封面）
  {
    let ready = false;
    for (let i = 0; i < 30; i++) {
      const st = await page.evaluate(() => {
        const m = document.querySelector('.hb-cpt__mask-wrapper');
        if (!m) return { hasModal: false };
        const imgs = [...m.querySelectorAll('img')].filter((e) => e.offsetParent !== null);
        return {
          hasModal: true,
          count: imgs.length,
          loaded: imgs.filter((i) => i.complete && i.naturalWidth > 50).length,
          nat: imgs.map((i) => i.naturalWidth).slice(0, 3),
        };
      }).catch(() => ({ hasModal: false }));
      if (st.hasModal && st.loaded > 0) { ready = true; log('裁剪图已加载: ' + JSON.stringify(st.nat)); break; }
      await sleep(1000);
    }
    if (!ready) log('⚠ 30 秒内没等到裁剪图加载，仍然尝试点确定');
  }
  await sleep(1500);

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

  }

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
  // 已发布的文章，主按钮是「修改」而不是「发布」。
  // 对它点发布只会回到编辑页，URL 也不会变成 /app/bbs/link/，会被误判为失败。
  const mainBtnText = await page.evaluate(() => {
    const b = document.querySelector('.editor-publish__btn.main-btn');
    return (b?.textContent || '').trim();
  }).catch(() => '');
  if (mainBtnText && mainBtnText !== '发布') {
    log(`主按钮是「${mainBtnText}」，不是「发布」——这篇已经是已发布状态，跳过发布`);
    log('按已发布处理，不再点击');
    await closeAll();
    process.exit(0);
  }

  log('点发布…');
  // 页面上的 toast 提示层会挡住发布按钮，先清掉
  await page.evaluate(() => {
    document.querySelectorAll('.hb-toast__wrapper, .hb-cpt__message, .t-mask').forEach((e) => e.remove());
  });
  await sleep(800);
  try {
    await page.click('.editor-publish__btn.main-btn', { timeout: 15000 });
  } catch (e) {
    log('普通点击失败，改用 force 点击: ' + e.message.split('\n')[0]);
    await page.evaluate(() => {
      document.querySelectorAll('.hb-toast__wrapper').forEach((x) => x.remove());
    });
    await page.click('.editor-publish__btn.main-btn', { timeout: 10000, force: true });
  }
  await sleep(3000);
  await waitForCaptcha('点发布后');
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
