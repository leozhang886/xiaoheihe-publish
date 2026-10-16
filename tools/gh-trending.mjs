// 抓 GitHub Trending（按周），解析出项目名/简介/语言/总星/本周新增星
// 用法: node tools/gh-trending.mjs [language] [since]
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36';

async function trending(lang = '', since = 'weekly') {
  const url = `https://github.com/trending${lang ? '/' + lang : ''}?since=${since}`;
  const res = await fetch(url, { headers: { 'User-Agent': UA } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const html = await res.text();

  const out = [];
  // GitHub 会不定期改 class 名（pr-4 → tmp-pr-4），所以按 Box-row 宽松切分
  const blocks = html.split('Box-row').slice(1);
  for (const b of blocks) {
    // 项目名：排除 sponsors/ 这种赞助跳转链接
    let full = '';
    for (const m of b.matchAll(/href="\/([A-Za-z0-9._-]+\/[A-Za-z0-9._-]+)"/g)) {
      if (!m[1].startsWith('sponsors/')) { full = m[1]; break; }
    }
    if (!full) continue;

    const descM = b.match(/<p class="[^"]*color-fg-muted[^"]*my-1[^"]*">\s*([\s\S]*?)\s*<\/p>/);
    let desc = descM ? descM[1].replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim() : '';

    const langM = b.match(/itemprop="programmingLanguage">([^<]+)</);
    const langName = langM ? langM[1].trim() : '';

    // 总星数：跳过 stargazers 里的 svg 路径数据，取 </svg> 之后的数字
    const starM = b.match(/\/stargazers"[\s\S]*?<\/svg>\s*([\d,]+)/);
    const stars = starM ? parseInt(starM[1].replace(/,/g, ''), 10) : 0;

    // 本周新增星
    const weekM = b.match(/float-sm-right">\s*([\s\S]*?)<\/span>/);
    let gained = 0, period = '';
    if (weekM) {
      const txt = weekM[1].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
      const gm = txt.match(/([\d,]+)\s*stars?\s*(today|this week|this month)/i);
      if (gm) { gained = parseInt(gm[1].replace(/,/g, ''), 10); period = gm[2]; }
    }

    out.push({ full, desc, lang: langName, stars, gained, period });
  }
  return out;
}

const lang = process.argv[2] || '';
const since = process.argv[3] || 'weekly';
const list = await trending(lang, since);
console.log(`共 ${list.length} 个${lang ? ' [' + lang + ']' : ''}，since=${since}\n`);
for (const r of list) {
  console.log(`${r.full}  ★${r.stars}  (+${r.gained} ${r.period})  [${r.lang}]`);
  console.log(`   ${r.desc.slice(0, 130)}`);
}
