// tools/check-readability.mjs —— 小黑盒文章扫读性检查
// 用法: node tools/check-readability.mjs articles/xxx.md [更多文件...]
//
// 判定依据来自 ~/.dsh/AGENTS.md 第 6 条「扫读优先」：
//   段落最多 3 行（约 45 字）、每节至少有一个可扫元素、小标题不许是空壳词

import fs from 'node:fs';
import path from 'node:path';

const MAX_PARA = 45;        // 单段最大字数（手机 3 行）
const MAX_HEADING = 24;     // 小标题最大字数
const MAX_BOLD = 18;        // 全文加粗处数上限
const EMPTY_HEADINGS = ['最后', '总结', '其他', '小结', '结语', '写在最后', '结论'];
// 小标题序号：中文序号（一、二、……）或阿拉伯数字（1. 1、01 ）
const NUMBERED = /^([一二三四五六七八九十]+[、.]|\d+[、.)]|0\d\s)/;

function stripFrontmatter(md) {
  return md.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, '');
}

// 去掉链接目标（只留锚文字）和图片，避免 URL 被算进正文长度
function plain(s) {
  return s
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/[*`]/g, '');
}

function check(file) {
  const raw = fs.readFileSync(file, 'utf8');
  const body = stripFrontmatter(raw);
  const lines = body.split(/\r?\n/);

  const problems = [];
  let para = [];
  let paraStart = 0;
  let curHeading = '（开头）';
  let headingHasScan = false;
  let headings = 0;
  let sectionIndex = 0;
  const headingTexts = [];

  const flushPara = () => {
    if (!para.length) return;
    const text = plain(para.join(''));
    const len = text.length;
    if (len > MAX_PARA) {
      problems.push({
        kind: '长段落',
        line: paraStart,
        msg: `${len} 字（上限 ${MAX_PARA}）在「${curHeading}」：${text.slice(0, 34)}…`,
      });
    }
    para = [];
  };

  const flushSection = () => {
    if (headings > 0 && !headingHasScan) {
      problems.push({
        kind: '缺扫读元素',
        line: 0,
        msg: `「${curHeading}」里没有清单/数字/独立判断行`,
      });
    }
    headingHasScan = false;
  };

  for (let i = 0; i < lines.length; i++) {
    const t = lines[i].trim();

    if (!t) { flushPara(); continue; }

    // 图片行也算可扫元素
    if (/^!\[[^\]]*\]\(/.test(t)) { flushPara(); headingHasScan = true; continue; }

    const h = t.match(/^(#{1,6})\s+(.*)$/);
    if (h) {
      flushPara();
      flushSection();
      headings++;
      sectionIndex++;
      curHeading = h[2].trim();
      headingTexts.push(curHeading);
      if (curHeading.length > MAX_HEADING) {
        problems.push({ kind: '标题过长', line: i + 1, msg: `${curHeading.length} 字：「${curHeading}」` });
      }
      if (EMPTY_HEADINGS.includes(curHeading)) {
        problems.push({ kind: '空壳标题', line: i + 1, msg: `「${curHeading}」没有信息量` });
      }
      // 小标题必须带序号：一、二、三…… 或 1. 2. 3.
      if (!NUMBERED.test(curHeading)) {
        problems.push({ kind: '标题没序号', line: i + 1, msg: `「${curHeading}」应以「一、」这类序号开头` });
      }
      continue;
    }

    // 表格行：小黑盒上会转成图片，不按正文段落计
    if (/^\|/.test(t)) { flushPara(); headingHasScan = true; continue; }

    // 列表 / 引用 = 可扫元素
    if (/^([-*+]\s|\d+\.\s|>)/.test(t)) { flushPara(); headingHasScan = true; continue; }

    // 短行（< 20 字）独立成段 = 可扫元素
    if (plain(t).length < 20) headingHasScan = true;
    // 含数字的行
    if (/\d/.test(t)) headingHasScan = true;

    if (!para.length) paraStart = i + 1;
    para.push(t);
  }
  flushPara();
  flushSection();

  // 整体统计
  const boldCount = (body.match(/\*\*/g) || []).length / 2;
  const words = body.replace(/!\[[^\]]*\]\([^)]*\)/g, '').replace(/[#*>\[\]`]/g, '').replace(/\s/g, '').length;

  // 加粗超限
  if (boldCount > MAX_BOLD) {
    problems.push({
      kind: '加粗过多',
      line: 0,
      msg: `${boldCount} 处（上限 ${MAX_BOLD}）—— 加粗成了装饰，不是标记`,
    });
  }

  // 序号连续性（有 3 节以上才检查，避免短文误报）
  if (headingTexts.length >= 3) {
    const CN = '一二三四五六七八九十';
    const nums = headingTexts.map((h) => {
      const m = h.match(NUMBERED);
      if (!m) return null;
      const s = m[1];
      if (/^\d/.test(s)) return parseInt(s, 10);
      const idx = CN.indexOf(s[0]);
      return idx >= 0 ? idx + 1 : null;
    });
    for (let k = 0; k < nums.length; k++) {
      if (nums[k] !== null && nums[k] !== k + 1) {
        problems.push({
          kind: '序号不连续',
          line: 0,
          msg: `第 ${k + 1} 节应为「${k + 1}」，实际是「${headingTexts[k]}」`,
        });
      }
    }
  }

  return { file: path.basename(file), words, sections: headings, bold: boldCount, problems };
}

const files = process.argv.slice(2);
if (!files.length) {
  console.error('用法: node tools/check-readability.mjs <文章.md> [...]');
  process.exit(1);
}

let total = 0;
for (const f of files) {
  if (!fs.existsSync(f)) { console.log(`\n${f}  不存在`); continue; }
  const r = check(f);
  const ok = r.problems.length === 0;
  console.log(`\n=== ${r.file} ===`);
  console.log(`  ${r.words} 字 · ${r.sections} 节 · 加粗 ${r.bold} 处 · ${ok ? '✅ 通过' : '⚠️ ' + r.problems.length + ' 处问题'}`);
  for (const p of r.problems) {
    console.log(`    [${p.kind}]${p.line ? ' L' + p.line : ''} ${p.msg}`);
  }
  total += r.problems.length;
}
console.log(`\n合计问题: ${total}`);
process.exit(total ? 1 : 0);
