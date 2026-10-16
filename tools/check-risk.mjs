// check-risk.mjs —— 只读检查风控状态
import { chromium } from 'playwright';

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const page = b.contexts()[0].pages()[0];

const st = await page.evaluate(() => {
  const iframes = [...document.querySelectorAll('iframe')].map((f) => ({ id: f.id, src: (f.src || '').slice(0, 60) }));
  const cap = document.querySelector('.tcaptcha-transform, #tcaptcha_iframe_dy, [id*="tcaptcha"]');
  let capText = null;
  if (cap) {
    const host = cap.closest('.tcaptcha-transform') || cap.parentElement;
    capText = (host?.textContent || '').replace(/\s+/g, ' ').slice(0, 120);
  }
  return {
    url: location.href,
    captchaPresent: !!cap,
    captchaText: capText,
    iframes,
    masks: document.querySelectorAll('.hb-cpt__mask-wrapper, .t-mask').length,
    editors: document.querySelectorAll('div.ProseMirror.hb-editor').length,
    title: document.querySelector('div.ProseMirror.hb-editor')?.innerText?.trim()?.slice(0, 50),
    counts: [...document.querySelectorAll('.editor__more-info-desc')].map((e) => e.textContent.trim()),
  };
});
console.log(JSON.stringify(st, null, 2));
process.exit(0);
