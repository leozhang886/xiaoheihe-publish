// session.mjs —— 常驻浏览器会话
// 启动一个带调试端口的独立 Chromium，保持运行；后续脚本通过 CDP 连上来干活。
import { chromium } from 'playwright';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// 项目根 = 本文件所在目录。
// 必须用 fileURLToPath：import.meta.url 里的中文是百分号编码的（桌面 -> %E6%A1%8C%E9%9D%A2），
// 直接取 .pathname 会建出一个错名字的目录。
const ROOT = path.dirname(fileURLToPath(import.meta.url));
const PROFILE = path.join(ROOT, 'profile');
const PORT = 9222;

const ctx = await chromium.launchPersistentContext(PROFILE, {
  headless: false,
  viewport: null,
  args: [
    `--remote-debugging-port=${PORT}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--start-maximized',
    '--disable-blink-features=AutomationControlled',
  ],
  ignoreDefaultArgs: ['--enable-automation'],
});

// 降低自动化特征
await ctx.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
});

const page = ctx.pages()[0] ?? (await ctx.newPage());
await page.goto('https://www.xiaoheihe.cn/', { waitUntil: 'domcontentloaded' }).catch(() => {});

console.log(`SESSION_READY pid=${process.pid} cdp=http://127.0.0.1:${PORT}`);

// 窗口被关掉时直接退出，避免进程空转（否则 CDP 端口没了但 job 还显示 running）
ctx.on('close', () => {
  console.log('BROWSER_CLOSED 浏览器已关闭，退出会话');
  process.exit(0);
});

const shutdown = async () => {
  try { await ctx.close(); } catch {}
  process.exit(0);
};
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

// 保活
setInterval(() => {}, 1 << 30);
