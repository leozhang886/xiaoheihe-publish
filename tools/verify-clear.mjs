// verify-clear.mjs —— 判断验证码是真的消失了还是只是隐藏
import { chromium } from 'playwright';

const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
const page = b.contexts()[0].pages()[0];
await page.bringToFront().catch(() => {});

const st = await page.evaluate(() => {
  const out = { candidates: [] };
  // 天御验证码常见的容器
  ['.tcaptcha-transform', '#tcaptcha_iframe_dy', '[id*="tcaptcha"]', '.tcaptcha-popup', '#tcaptcha_popup'].forEach((sel) => {
    document.querySelectorAll(sel).forEach((e) => {
      const r = e.getBoundingClientRect();
      const cs = getComputedStyle(e);
      out.candidates.push({
        sel,
        tag: e.tagName,
        visible: r.width > 0 && r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden' && cs.opacity !== '0',
        rect: { w: Math.round(r.width), h: Math.round(r.height), x: Math.round(r.x), y: Math.round(r.y) },
        display: cs.display,
        opacity: cs.opacity,
      });
    });
  });
  out.bodyText = (document.body.innerText || '').replace(/\s+/g, ' ').slice(0, 200);
  out.hasVerifyWord = /验证|尝试太多/.test(document.body.innerText || '');
  return out;
});
console.log(JSON.stringify(st, null, 2));
await page.screenshot({ path: 'C:\\Users\\86153\\xhh\\shots\\now.png' });
process.exit(0);
