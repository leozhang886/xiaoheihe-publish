// tools/find-topic.mjs —— 查小黑盒真实话题名
//
// 为什么要这个：frontmatter 里的 topics 如果写的是"想当然"的词（显卡、硬盘、带宽），
// 平台上根本不存在，addTopic() 会静默跳过，那条"加话题"的加分项就白丢了。
//
// 用法:
//   node tools/find-topic.mjs 显卡 Steam 使命召唤     # 列出候选
//   node tools/find-topic.mjs --pick Steam 使命召唤    # 只给建议填的那个
//
// 依赖 xiaoheihe-cli（uv tool 装的）。
//
// 匹配规则（重要）：接口是模糊匹配，会返回一堆不相干的小游戏话题。
// 所以只接受三种情况，其余一律判定"不可用"：
//   1. 名称完全等于关键词
//   2. 名称包含关键词，且热度 >= 10 万
//   3. 关键词包含名称，且热度 >= 10 万
// 候选按热度降序取第一。

import { execFileSync } from 'node:child_process';

const CLI = 'C:\\Users\\86153\\AppData\\Roaming\\uv\\tools\\xiaoheihe-cli\\Scripts\\xiaoheihe-cli.exe';
const MIN_HOT = 100000;

const args = process.argv.slice(2);
const PICK = args[0] === '--pick';
const words = PICK ? args.slice(1) : args;

if (!words.length) {
  console.error('用法: node tools/find-topic.mjs [--pick] 关键词 [关键词...]');
  process.exit(1);
}

const hot = (t) => Number(t.hot?.raw_hot_value ?? 0);

for (const w of words) {
  let out = '';
  try {
    out = execFileSync(CLI, ['search', w, '--type', 'topic', '--limit', '10'], {
      encoding: 'utf8',
      timeout: 60000,
    });
  } catch (e) {
    console.log(`\n[${w}] 查询失败: ${String(e.message).split('\n')[0]}`);
    continue;
  }

  let topics = [];
  try {
    topics = JSON.parse(out).data?.result?.topics ?? [];
  } catch {
    console.log(`\n[${w}] 返回解析失败`);
    continue;
  }

  const exact = topics.filter((t) => t.name === w);
  const loose = topics
    .filter((t) => t.name !== w && (t.name.includes(w) || w.includes(t.name)) && hot(t) >= MIN_HOT)
    .sort((a, b) => hot(b) - hot(a));

  const best = exact[0] ?? loose[0] ?? null;

  console.log(`\n[${w}] 原始 ${topics.length} 个结果`);
  topics.slice(0, 6).forEach((t, i) => {
    const mark = t === best ? ' ★' : '';
    console.log(`  ${i + 1}. ${t.name}  (热度 ${t.hot?.raw_hot_value?.toLocaleString?.() ?? t.hot?.raw_hot_value ?? 0})${mark}`);
  });

  if (best) {
    console.log(`  → 可用: ${best.name}${PICK ? '' : `   (topic_id ${best.topic_id})`}`);
  } else {
    console.log(`  → ❌ 没有可用话题，这个词别写进 frontmatter`);
  }
}
