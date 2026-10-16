// lib/md2xhh.mjs —— Markdown 转「小黑盒文章编辑器」可接受的 HTML
//
// 核心映射（实测得出，见 NOTES.md）：
//   #   -> <h2>   （小黑盒的「一级标题」）
//   ##  -> <h3>   （小黑盒的「二级标题」）
//   ### -> 加粗段落（平台只支持两级标题）
//   其余为平台原生支持的：p / strong / blockquote / ul / ol / a
//   表格、代码块、斜体、下划线、删除线、hr —— 平台不支持，这里直接不生成。

/** HTML 转义 */
function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/** 行内语法：**加粗** / [文字](链接) / `代码`(降级为纯文本) */
function inline(s) {
  let t = esc(s);
  // 行内代码：去掉反引号（平台不支持 code 标签）
  t = t.replace(/`([^`]+)`/g, '$1');
  // 加粗
  t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  // 链接
  t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>');
  return t;
}

/** 解析 frontmatter，返回 {meta, body} */
export function parseFrontmatter(md) {
  const m = md.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return { meta: {}, body: md };
  const meta = {};
  for (const line of m[1].split(/\r?\n/)) {
    const i = line.indexOf(':');
    if (i < 0) continue;
    const k = line.slice(0, i).trim();
    const v = line.slice(i + 1).trim();
    if (k) meta[k] = v;
  }
  return { meta, body: md.slice(m[0].length) };
}

/**
 * 把 Markdown 正文切成有序片段。
 * @returns {Array<{type:'html', html:string} | {type:'image', url:string}>}
 */
export function mdToSegments(body) {
  const lines = body.replace(/\r\n/g, '\n').split('\n');
  const segs = [];
  let buf = [];        // 当前累积的块级 HTML
  let para = [];       // 当前段落行
  let list = null;     // { ordered:boolean, items:[] }
  let quote = [];      // 引用行

  const flushPara = () => {
    if (para.length) {
      buf.push(`<p>${inline(para.join(' '))}</p>`);
      para = [];
    }
  };
  const flushList = () => {
    if (list) {
      const tag = list.ordered ? 'ol' : 'ul';
      buf.push(`<${tag}>${list.items.map((i) => `<li><p>${inline(i)}</p></li>`).join('')}</${tag}>`);
      list = null;
    }
  };
  const flushQuote = () => {
    if (quote.length) {
      // 引用内每行独立成段，方便承载「可复制的提示词」这类多行内容
      buf.push(`<blockquote>${quote.map((q) => `<p>${inline(q)}</p>`).join('')}</blockquote>`);
      quote = [];
    }
  };
  const flushAll = () => { flushPara(); flushList(); flushQuote(); };
  const pushHtml = () => {
    flushAll();
    if (buf.length) {
      segs.push({ type: 'html', html: buf.join('') });
      buf = [];
    }
  };

  for (const raw of lines) {
    const line = raw.trimEnd();
    const t = line.trim();

    // 图片独立成段（也允许带标题的图片）
    const img = t.match(/^!\[[^\]]*\]\((\S+)\)$/);
    if (img) {
      pushHtml();
      segs.push({ type: 'image', url: img[1] });
      continue;
    }

    // 空行 = 块结束
    if (!t) { flushAll(); continue; }

    // 分隔线：平台不支持，直接丢弃
    if (/^-{3,}$/.test(t) || /^\*{3,}$/.test(t)) { flushAll(); continue; }

    // 标题
    let h = t.match(/^(#{1,6})\s+(.*)$/);
    if (h) {
      flushAll();
      const level = h[1].length;
      const text = h[2].trim();
      if (level === 1) buf.push(`<h2>${inline(text)}</h2>`);
      else if (level === 2) buf.push(`<h3>${inline(text)}</h3>`);
      else buf.push(`<p><strong>${inline(text)}</strong></p>`);
      continue;
    }

    // 引用
    if (/^>\s?/.test(t)) {
      flushPara(); flushList();
      quote.push(t.replace(/^>\s?/, ''));
      continue;
    }

    // 有序列表
    const ol = t.match(/^\d+\.\s+(.*)$/);
    if (ol) {
      flushPara(); flushQuote();
      if (!list || !list.ordered) { flushList(); list = { ordered: true, items: [] }; }
      list.items.push(ol[1]);
      continue;
    }

    // 无序列表
    const ul = t.match(/^[-*+]\s+(.*)$/);
    if (ul) {
      flushPara(); flushQuote();
      if (!list || list.ordered) { flushList(); list = { ordered: false, items: [] }; }
      list.items.push(ul[1]);
      continue;
    }

    // 普通段落行
    flushList(); flushQuote();
    para.push(t);
  }
  pushHtml();
  return segs;
}

/** 便捷入口 */
export function loadArticle(mdText) {
  const { meta, body } = parseFrontmatter(mdText);
  return { meta, segments: mdToSegments(body) };
}
