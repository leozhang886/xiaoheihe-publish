// 抓 Steam 搜索页，取「价格 + 好评率 + 评测数」样本
// 用法: node tools/scrape-prices.mjs
import fs from 'node:fs';

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36';

// 多种排序，避免样本只集中在热门高价区
const SORTS = [
  'Reviews_DESC', 'Released_DESC', 'Price_ASC', 'Price_DESC',
  'ReviewScore_DESC', 'Name_ASC', 'Metacritic_DESC', 'Discount_DESC',
];
const PAGES = 6; // 每种排序抓几页

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function fetchPage(sort, page) {
  // 注意：不要加 infinite=1，那时返回的是 JSON 且 HTML 被转义，正则匹配不到
  const url = `https://store.steampowered.com/search/?sort_by=${sort}&category1=998`
    + `&cc=cn&l=schinese&start=${page * 50}`;
  const res = await fetch(url, { headers: { 'User-Agent': UA, 'Accept-Language': 'zh-CN,zh;q=0.9' } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const text = await res.text();
  if (text.trimStart().startsWith('{')) throw new Error('拿到了 JSON，预期是 HTML');
  return text;
}

function parse(html) {
  const out = [];
  // 注意：data-ds-appid 在 class="search_result_row" 之前，
  // 所以必须整块匹配 <a ...>...</a>，不能按 class 切。
  const rowRe = /<a\s+href="[^"]*?\/app\/(\d+)[^"]*"[^>]*?class="search_result_row[\s\S]*?<\/a>/g;
  const rows = html.match(rowRe) || [];

  const toNum = (s) => {
    if (!s) return null;
    const m = s.replace(/,/g, '').match(/(\d+(?:\.\d+)?)/);
    return m ? parseFloat(m[1]) : null;
  };

  for (const block of rows) {
    const appid = (block.match(/\/app\/(\d+)/) || [])[1];
    const name = (block.match(/<span class="title">([^<]+)<\/span>/) || [])[1];
    if (!appid || !name) continue;

    const discount = parseInt((block.match(/data-discount="(\d+)"/) || [])[1] || '0', 10);
    const finalM = block.match(/class="discount_final_price">([^<]*)</);
    const origM = block.match(/class="discount_original_price">([^<]*)</);
    const plainM = block.match(/class="search_price[^"]*">\s*([^<]*)/);

    let price = null, original = null;
    if (finalM) { price = toNum(finalM[1]); original = toNum(origM ? origM[1] : null); }
    else if (plainM) { price = toNum(plainM[1]); }
    if (price === null) continue; // 免费或没价

    // 评测：tooltip 形如「此游戏的 207 篇用户评测中有 99% 为好评。」
    let pct = null, reviews = null;
    const tipM = block.match(/data-tooltip-html="([^"]*)"/);
    if (tipM) {
      const tip = tipM[1].replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"');
      const m = tip.match(/([\d,]+)\s*篇用户评测中有\s*(\d+)%\s*为好评/)
             || tip.match(/(\d+)%\s*of the\s*([\d,]+)/i);
      if (m) {
        // 两种写法顺序不同
        if (/篇用户评测/.test(tip)) { reviews = parseInt(m[1].replace(/,/g, ''), 10); pct = parseInt(m[2], 10); }
        else { pct = parseInt(m[1], 10); reviews = parseInt(m[2].replace(/,/g, ''), 10); }
      }
    }

    const sumM = block.match(/class="search_review_summary[^"]*">([^<]*)</);
    const relM = block.match(/class="search_released[^"]*">\s*([^<]*?)\s*</);
    out.push({
      appid, name: name.trim(), price, original, discount,
      pct, reviews, summary: sumM ? sumM[1].trim() : null,
      released: relM ? relM[1].trim() : null,
    });
  }
  return out;
}

const all = new Map();
for (const sort of SORTS) {
  for (let p = 0; p < PAGES; p++) {
    try {
      const html = await fetchPage(sort, p);
      const rows = parse(html);
      let added = 0;
      for (const r of rows) if (!all.has(r.appid)) { all.set(r.appid, r); added++; }
      process.stdout.write(`  ${sort} p${p}: 解析 ${rows.length}, 新增 ${added}, 累计 ${all.size}\n`);
      if (rows.length === 0) break;
    } catch (e) {
      process.stdout.write(`  ${sort} p${p}: 失败 ${e.message}\n`);
    }
    await sleep(1200); // 别把 Steam 惹毛
  }
}

const data = [...all.values()].filter((d) => d.pct !== null && d.price !== null);
fs.writeFileSync('data/steam-prices.json', JSON.stringify(data, null, 1), 'utf8');
console.log(`\n有效样本 ${data.length} 条 → data/steam-prices.json`);
