# 小黑盒自动发帖项目 —— 交接文档

> 最后更新：2026-10-13
> 本文档说明项目结构、代码、依赖、已实现功能，以及如何导出。
> **⚠️ 文中不含任何账号、密码或 Cookie。导出前请务必阅读第 9 节。**

---

## 0. 这个项目是干什么的

一套用来**往小黑盒（xiaoheihe.cn）发游戏文章**的工具链。

它解决的核心问题是：小黑盒的文章编辑器是 ProseMirror 富文本，直接粘贴 Markdown 会被"降噪"掉格式。所以这套工具做三件事：

1. **转换**：把 Markdown 转成小黑盒编辑器能接受的 HTML（`lib/md2xhh.mjs`）
2. **填充**：驱动一个真实的 Chromium，把标题、正文、配图、社区、声明填进编辑器（`publish.mjs`）
3. **配图**：用 PIL 生成封面和数据图表，因为平台不支持表格（`tools/make_*_images.py`）

配套的还有一套**写作规范**和**去 AI 味规则**，见 `写作规范.md` 和外部文件 `~/.dsh/AGENTS.md`。

---

## 1. 环境与依赖

| 项 | 版本 / 路径 |
|---|---|
| Node.js | v24.19.0 |
| npm | 11.17.0 |
| Playwright | 1.63.0（`playwright` + `playwright-core`） |
| Python（用于配图） | 3.13，需要 Pillow、numpy |
| 浏览器 | Playwright 自带 Chromium（**不用 Edge**，原因见 §10） |

`package.json` 里只有两个依赖：

```json
{
  "dependencies": {
    "playwright": "^1.63.0",
    "playwright-core": "^1.63.0"
  }
}
```

**Python 不是项目依赖**，是环境依赖。配图脚本用到 `Pillow` 和 `numpy`，字体走 Windows 自带的微软雅黑（`C:\Windows\Fonts\msyhbd.ttc` / `msyh.ttc`），**Windows 以外跑要改字体路径**。

---

## 2. 文件目录

```
小黑盒/
├── publish.mjs              主程序：填文 + 发布（18 KB）
├── session.mjs              常驻浏览器会话（CDP 调试端口）
├── comments.mjs             评论自动回复（14 KB，走网页消息中心）
├── 启动自动回复.cmd           评论回复的双击启动入口
├── package.json             依赖声明
├── package-lock.json
├── NOTES.md                 技术笔记（20 KB，踩过的坑全在这）
├── 写作规范.md               写作方法论（标题六律、封面规则、选题方法）
├── README.md                本文档
├── .gitignore               ⚠️ 排除 profile/ 等敏感目录
│
├── lib/
│   └── md2xhh.mjs           Markdown → 小黑盒 HTML 转换器
│
├── articles/                25 篇稿子（Markdown，带 frontmatter）
├── assets/                  69 个配图（约 20 MB），按主题分子目录
│   ├── cp2077/ display/ emu/ gh-weekly/ kcd2/ mouse/
│   ├── news-enshrouded-1.0/   ← 含 SOURCES.md 记录图片来源
│   ├── rdr2/ settings/ upscale/
│   └── cover-*.png            各篇封面
├── shots/                   59 张操作截图（约 20 MB，可删）
├── data/                    运行状态与日志（已 gitignore）
│   ├── comment-replies.json    评论回复去重状态
│   ├── comment-*.log           评论脚本运行日志
│   └── steam-prices.json       价格抓取结果（空，抓取未完成）
├── refs/                    调研文档（3 份）
│   ├── astrbot-xhhrobot-README.md
│   ├── astrbot-部署记录.md
│   └── 评论机器人-调研.md
├── tools/                   35 个辅助脚本（见 §3）
├── _archive/                49 个早期探索脚本（已归档，可删）
│
├── node_modules/            ← 目录联接（Junction），非实体
└── profile/                 ⚠️ 浏览器用户数据，含登录 Cookie（86 MB）
```

**两个特殊条目：**

- **`node_modules/`** 是指向外部目录的**目录联接（Junction）**，不是真实文件夹。这样做的目的是不让 OneDrive 同步上万个小文件。换机器需要重新 `npm install`。
- **`profile/`** 是 Chromium 的用户数据目录，**里面存着小黑盒的登录 Cookie**。**导出前必须排除**（`.gitignore` 里已经写好了），详见 §9。

---

## 3. 我们写的代码

### 3.1 核心链路（两个文件）

**`session.mjs`**（51 行）

启动一个持久化 Chromium，开 CDP 调试端口 9222，然后挂着不动，等别的脚本连上来。

关键设计：
- 用 `launchPersistentContext` 复用 `profile/` 目录，**登录状态得以保留**，不用每次扫码
- 用 `fileURLToPath(import.meta.url)` 取项目根 —— **不能用 `new URL().pathname`**，中文路径会被百分号编码（这个坑见 NOTES.md §15.1）
- 监听 `ctx.on('close')` 主动退出，避免浏览器关了但进程空转

**`publish.mjs`**（491 行）—— 主程序

流程：连上 CDP → 打开创作页 → 填标题 → 逐段填充正文 → 插图 → 选社区 → 加话题 → 勾 AI 声明 → 截图 →（可选）点发布。

主要函数：

| 函数 | 作用 |
|---|---|
| `focusEditor(which)` | 定位标题/正文的 ProseMirror 编辑器 |
| `collapseToEnd(which)` | 把光标移到内容末尾 |
| `clearEditor(which)` | 清空编辑器（重新填充时用） |
| `pasteHtml(html)` | **核心**：用合成 `ClipboardEvent('paste')` 注入富文本 |
| `clickText(text)` | 按文字找元素并点击，带遮挡检测与兜底 |
| `dismissOverlays()` | 清理残留的 `.t-mask` 遮罩 |
| `setInput(selector, value)` | 赋值表单输入框（用原生 setter，绕过 React/Vue 拦截） |
| `insertImage(src)` | 插图。**同时支持 http 图片 URL 和本地文件**（本地上传走 `filechooser`） |
| `selectCommunity(name)` | 搜索并选中关联社区 |
| `addTopic(name)` | 添加关联话题 |
| `setAiDeclaration()` | 勾选「其他声明 → 包含AI辅助创作」 |

**命令用法：**

```powershell
# 安全模式（默认）：只填充 + 截图，不发布
node publish.mjs articles/xxx.md

# 真正发布
node publish.mjs articles/xxx.md --publish
```

**`lib/md2xhh.mjs`**（150 行）—— Markdown 转换器

输出的是**「片段数组」**而不是一整段 HTML：

```js
[ {type:'html', html:'...'}, {type:'image', url:'...'}, ... ]
```

因为插图必须走平台自己的上传流程，不能混在 HTML 里粘贴。

核心映射（实测得出）：

| Markdown | 输出 | 说明 |
|---|---|---|
| `#` | `<h2>` | 小黑盒的「一级标题」 |
| `##` | `<h3>` | 小黑盒的「二级标题」 |
| `###` 及更深 | `<p><strong>` | 平台只支持两级标题 |
| `> 引用` | `<blockquote>`，每行独立 `<p>` | 为承载多行提示词 |
| 表格 / 代码块 / 斜体 / 删除线 / 分隔线 | **直接丢弃** | 平台不支持，要改成图片 |
| 行内 `` `代码` `` | 降级为纯文本 | 平台不支持 code 标签 |

### 3.2 配图生成脚本（`tools/make_*.py`，14 个）

全部是 PIL + numpy，输出到 `assets/`。**因为小黑盒不支持表格，所有数据表都必须转成图片。**

| 脚本 | 用途 |
|---|---|
| `make_images.py` / `make_images2.py` | 最早的通用配图（文章二） |
| `make_deai_images.py` | 去 AI 味那篇：封面 + 改前改后对照 |
| `make_discount_images.py` | Steam 折扣：封面 + 两个真实算例 |
| `make_reviews_image.py` | Steam 三个评分：三栏对比封面 |
| `make_settings_image.py` | 游戏设置：封面（六项清单） |
| `make_setting_comparisons.py` | **设置开/关对比图**：动态模糊、颗粒、色差、暗角、景深、FOV |
| `make_online_image.py` | 单机联网：封面 |
| `make_display_images.py` | 显示器：封面 + 色深分层示意 + 缩放对比 |
| `make_upscale_images.py` | DLSS/FSR：封面 + 两张力表 |
| `make_emu_images.py` | 模拟器：封面 + 四档速查表 |
| `make_mouse_images.py` | 鼠标加速：封面 + 两条输入路径流程图 |
| `make_gh_weekly_images.py` | GitHub 周报：封面 + 涨星对比图 |
| `make_box_truth_01_images.py` | 【盒友大实话01】3A 定价那篇的配图 |
| `make_box_truth_02_images.py` | 【盒友大实话02】难度选择那篇的配图 |
| `crop.py` / `crop2.py` | 裁图小工具 |

**做对比图的通用手法**（`make_setting_comparisons.py` 是模板）：拿一张真实游戏截图当底图，按各选项的光学原理模拟效果，上下两格对比，图上标注「效果示意」。**不能拿别人的对比图，出处和版权都不干净。**

### 3.3 抓取 / 调研脚本（`tools/` 里的 .mjs 和 .py）

| 脚本 | 用途 |
|---|---|
| `gh-trending.mjs` | **抓 GitHub 周榜**，输出项目名/简介/语言/总星/本周新增星，支持指定语言 |
| `scrape-prices.mjs` | 抓 Steam 搜索页的价格和好评率 |
| `check-login.mjs` | 检查小黑盒登录状态 |
| `check-risk.mjs` / `verify-clear.mjs` | 检查风控/验证码状态 |
| `review.mjs` | 截图复查 |
| `start-comments.ps1` | 评论自动回复的后台启动脚本（供 `启动自动回复.cmd` 调用） |
| `api_probe.py` ~ `api_probe4.py` | 小黑盒 App 接口探测（评论机器人线，已废弃） |
| `get_auth.py` / `dump_replies.py` | 取鉴权 / 导出评论 |
| `make_persona.py` / `add_webchat.py` / `setup_astrbot.py` | AstrBot 配置 |
| `xhh_qr.py` | 渲染登录二维码 |

### 3.4 评论机器人（支线一：AstrBot + App 接口）—— 已废弃

这部分**代码不是我们写的**，是调研 + 部署 + 配置。相关文档在 `refs/` 三份文件里。

结论：插件能跑通，但因为**小黑盒服务端在评论接口上做了风控**（返回 `show_captcha` / `缺失参数`），自动回复评论走不通。已停用。

**这条路已经放弃，改走下面 3.5 的网页路线。** 保留本节是为了记录「为什么不用 App 接口」这个结论——接口级风控绕不过去，不是配置问题。

### 3.5 网页评论自动回复（2026-10-15）

`comments.mjs` 使用本项目的 Chromium 登录会话，从网页消息中心读取评论。它只处理**启动基线之后**、直接评论当前账号自己帖子的消息；旧评论和楼中楼都不回复。无论帖子是不是「盒友大实话」，规则都一样。

```powershell
node session.mjs                    # 先启动登录会话，窗口要保持打开
node comments.mjs                   # 只预览，不发送
node comments.mjs --send --one      # 单次只发 1 条，用于验证
node comments.mjs --send --watch    # 每 2 小时检查一次并自动回复
```

电脑重启后可双击项目根目录的 `启动自动回复.cmd`；它会在后台启动浏览器和自动回复，若已在运行则不会重复启动。

回复模型沿用本机 AstrBot 已配置的 DeepSeek 模型，程序只在运行时读取配置，不复制或打印密钥。状态保存在 `data/comment-replies.json`（已被 `.gitignore` 排除）。每轮最多发 3 条，每天最多 20 条，同一帖子累计最多自动回复 20 条，两次发送至少间隔 90 秒。帖子累计数按状态文件中的已发送记录计算。检测到已有本人回复会跳过；发送结果无法确认时停止，不自动重发。遇到平台验证时需手动处理。

2026-10-15 已开启持续运行，首轮自动发送 3 条并在评论区确认。运行日志保存在 `data/comment-watch.out.log` 和 `data/comment-watch.err.log`；关机或关闭浏览器会结束本次运行。

---

## 4. 已实现的功能

### ✅ 发布链路（完整可用）

- [x] 常驻浏览器会话，**登录状态持久化**，不用反复扫码
- [x] Markdown → 小黑盒 HTML 转换，标题层级正确映射
- [x] 标题自动填写 + **超长截断检测**（超 30 字会警告）
- [x] 正文分段填充，富文本（加粗、链接、列表、引用）正常渲染
- [x] **图片插入**：支持网络图片 URL，也支持**本地文件上传**
- [x] 关联社区搜索与选中（上限 2 个）
- [x] 关联话题添加（上限 5 个）
- [x] 勾选「包含AI辅助创作」声明
- [x] 发布前后自动截图，供人工确认
- [x] **安全模式**：默认只填充不发布，确认后才 `--publish`
- [x] **一键发布**：`--publish` 会真的点发布按钮并回读发布后的 URL
- [x] 反自动化特征处理（`--disable-blink-features=AutomationControlled` + 抹掉 `navigator.webdriver`）

### ✅ 内容生产（14 篇已成稿）

已发布过的类型：购买指南、教程、真实体验、观点、实用设置、数据解读。

源稿全部在 `articles/`，配图在 `assets/`。

### ✅ 配图生成

- [x] 封面生成（深色卡片风格，统一模板）
- [x] 数据表格转图（平台不支持表格）
- [x] **效果对比图**（设置开/关、改前/改后、缩放方式）
- [x] 数据可视化（涨星对比柱状图）
- [x] 示意图（两级标题、色深分层）
- [x] 真实游戏截图 + 效果模拟的组合

### ✅ 数据获取

- [x] Steam 官方 API：游戏详情、价格、评测统计、搜索
- [x] Steam 商店页渲染抓取（拿到「最近评测」「简中评测」「跑题评测」等分区数据）
- [x] GitHub 搜索 API + Trending 页解析
- [x] 小黑盒站内页面（已登录态下）

### ✅ 写作方法论沉淀

- [x] `写作规范.md`：标题六律、封面规则、正文结构、选题「需求缺口」方法、发布前自检清单
- [x] `~/.dsh/AGENTS.md`（**项目外部**）：去 AI 味规则 12 条、场景化力度分级、小黑盒发帖固定规矩（先列主题候选、先搜 GitHub 高星资源、开头不放 AI 声明等）

---

## 5. 未实现 / 待办

### ⚠️ 已知限制

- [ ] **关联话题基本没用起来。** 话题搜索框的关键词匹配很难命中，实测多次都放弃。
- [ ] **头条封面没有自动化。** 网页版文章编辑器**根本没有封面字段**，正文第一张图即封面，所以不需要设置——但手机端有独立封面，未处理。
- [ ] **正文不支持表格**，只能转图，流程上多一步。
- [ ] **`_archive/` 里 49 个脚本是早期探索产物**，功能已被 `publish.mjs` 吸收，可以删。
- [ ] **没有错误重试机制。** 填充过程中如果浏览器被关（用户手动关窗口），脚本直接抛异常退出。
- [ ] **没有批量发布。** 一次只能处理一篇文章。
- [ ] **图片后缀名要人工核对。** 生成脚本输出 `.jpg`，文章里如果写成 `.png` 会填到一半报 `ENOENT`。这个坑踩过两次。
- [ ] **Python 字体路径写死 Windows。** 换系统要改。
- [ ] **`scrape-prices.mjs` 的解析器不稳。** GitHub/Steam 的页面 class 名会变，改版就挂（GitHub trending 那次 `pr-4` → `tmp-pr-4` 就挂过一次）。
- [ ] **还没有建 git 仓库。** `.gitignore` 已就位，但 `git init` 未执行。

### 🚫 意图放弃的

- **走 App 接口的评论机器人**（AstrBot 插件那条线）：小黑盒服务端在评论接口上做了风控，不是配置问题，绕不过去。**已改走网页路线，见 §3.5，那条是通的。**

### ⚠️ 环境相关的坑（重要）

- **`import.meta.url` 的路径陷阱**：`new URL(import.meta.url).pathname` 返回百分号编码路径，中文目录名会被编码成 `%E6%A1%8C%E9%9D%A2`，导致建出错误目录。**必须用 `fileURLToPath`。** 这个坑害得浏览器 profile 一度建到了错名字的目录里。
- **file sandbox 与目录联接**：会话写入权限被限制在工作目录内时，目录联接（Junction）**只能读不能写** —— 沙箱会解析联接指向的真实路径再判定。
- **本地网络代理会影响 Node**：如果本机有 hosts 级的代理工具（如 Steamcommunity_302），Node 的 `fetch` 会报 `UNABLE_TO_VERIFY_LEAF_SIGNATURE`。绕过方式是 `$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"`，或把证书加进信任链。

---

## 6. 用过的 GitHub 项目

### 6.1 写作规则来源（直接影响了 `AGENTS.md` 的写法）

| 项目 | ★ | 用途 |
|---|---|---|
| [addyosmani/clarity](https://github.com/addyosmani/clarity) | 265 | 清晰写作理念 |
| [daniel-p-green/nbj-write-clearly](https://github.com/daniel-p-green/nbj-write-clearly) | 117 | 基于 Google 开发者文档风格指南 |
| [jsath/simplified-technical-english](https://github.com/jsath/simplified-technical-english) | 80 | **ASD-STE100 简化技术英语**（航空手册标准），句子硬性限长 |
| [MrGeDiao/shuorenhua](https://github.com/MrGeDiao/shuorenhua) | 1974 | 中文优先的去 AI 味改写 |
| [larashero3-dotcom/lieflat-less-ai-tone](https://github.com/larashero3-dotcom/lieflat-less-ai-tone) | 2275 | 基于 283 万字语料统计 |
| [Raymondhou0917/speak-human-tw](https://github.com/Raymondhou0917/speak-human-tw) | 1022 | 抓 38 种 AI 写作痕迹 |
| [hylarucoder/ai-flavor-remover](https://github.com/hylarucoder/ai-flavor-remover) | 1175 | ⚠️ **550 天未更新，无许可证** |
| [orange2ai/renwei-writing](https://github.com/orange2ai/renwei-writing) | 1086 | 保留原作者语气 |
| [OUBIGFA/De-AI-Prompt-Enhancer-Writer-Booster-SKILL](https://github.com/OUBIGFA/De-AI-Prompt-Enhancer-Writer-Booster-SKILL) | 846 | 提示词增强 |
| [robpalmer99/claude-code-copywriting-skills](https://github.com/robpalmer99/claude-code-copywriting-skills) | 39 | 直复营销文案（标题公式、好奇缺口） |
| [boraoztunc/skills](https://github.com/boraoztunc/skills) | 391 | 含奥美广告原则、Stop Slop |
| [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | 53445 | 营销技能库（英文向，参考为主） |
| [jamditis/claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism) | 415 | 新闻写作（倒金字塔） |
| [weijt606/anti-vibe-writing](https://github.com/weijt606/anti-vibe-writing) | 119 | 去 AI 味 |
| [hl897tech/xhs_content_agent](https://github.com/hl897tech/xhs_content_agent) | 312 | 小红书爆款内容 Agent |
| [zenstory-ai/oh-story-claudecode](https://github.com/zenstory-ai/oh-story-claudecode) | 7300 | 中文网文写作（扫榜、拆文方法可借鉴） |

### 6.2 同类工具（做对比，未采用）

| 项目 | ★ | 说明 |
|---|---|---|
| [evgo2017/xiaoheihe-editor](https://github.com/evgo2017/xiaoheihe-editor) | 9 | Markdown → 小黑盒转换工具，**功能与我们的 `md2xhh.mjs` 重叠**。后来才知道它存在。 |
| [wsmxd/XiaoheiheMcpServer](https://github.com/wsmxd/XiaoheiheMcpServer) | 16 | 小黑盒发帖 MCP 工具 |
| [k1m0206/better-XiaoHeiHe](https://github.com/k1m0206/better-XiaoHeiHe) | 89 | 网页版小黑盒社区插件 |
| [heygsc/xiaoheihe-literature](https://github.com/heygsc/xiaoheihe-literature) | 409 | 黑盒圣经合集（内容，非工具） |

**教训**：`evgo2017/xiaoheihe-editor` 和 `wsmxd/XiaoheiheMcpServer` 如果能早点搜到，可以少写不少代码。**这就是后来定下「先搜 GitHub 再动手」规矩的直接原因。**

### 6.3 评论机器人线（AstrBot）

| 项目 | 说明 |
|---|---|
| [AstrBotDevs/AstrBot](https://github.com/AstrBotDevs/AstrBot) | 机器人框架本体 |
| [Whereis-Alice/astrbot_plugin_xhhrobot](https://github.com/Whereis-Alice/astrbot_plugin_xhhrobot) | 小黑盒机器人插件（**主要调研对象**） |
| [advent259141/astrbot_plugin_xiaoheihe_adapter](https://github.com/advent259141/astrbot_plugin_xiaoheihe_adapter) | 小黑盒适配器 |
| [2646617098/heibox-comment-bot](https://github.com/2646617098/heibox-comment-bot) | 评论机器人 |
| [HadeonYu/heybox-bot](https://github.com/HadeonYu/heybox-bot) | 小黑盒机器人 |
| [Water-W/xiaoheihe-side-comments](https://github.com/Water-W/xiaoheihe-side-comments) | 小黑盒评论相关 |
| [SomeOvO/xhhRobot](https://github.com/SomeOvO/xhhRobot) | 小黑盒机器人 |
| [Www8881313/Openxhh](https://github.com/Www8881313/Openxhh) | 小黑盒开源项目 |
| [XiaHouSheng/heybox-core](https://github.com/XiaHouSheng/heybox-core) | 小黑盒核心库 |

### 6.4 文章内容引用过的

**模拟器**（模拟器那篇）：[Dolphin](https://github.com/dolphin-emu/dolphin)、[PCSX2](https://github.com/PCSX2/pcsx2)、[RPCS3](https://github.com/RPCS3/rpcs3)、[DuckStation](https://github.com/stenzek/duckstation)、[PPSSPP](https://github.com/hrydgard/ppsspp)、[Cemu](https://github.com/cemu-project/Cemu)、[melonDS](https://github.com/melonDS-emu/melonDS)、[Azahar](https://github.com/azahar-emu/azahar)、[Vita3K](https://github.com/Vita3K/Vita3K)、[shadPS4](https://github.com/shadps4-emu/shadPS4)、[xenia](https://github.com/xenia-project/xenia)、[xenia-canary](https://github.com/xenia-canary/xenia-canary)、[xemu](https://github.com/xemu-project/xemu)

**GitHub 周报**（第 1 期）：[Moonlight](https://github.com/moonlight-stream/moonlight-qt)、[Pumpkin](https://github.com/Pumpkin-MC/Pumpkin)、[Steamodded](https://github.com/Steammoded/smods)、[raddebugger](https://github.com/EpicGames/raddebugger)、[AnyPS5](https://github.com/boykopovar/AnyPS5)

**鼠标加速**：[Raw Accel](https://github.com/RawAccelOfficial/rawaccel)、[InterAccel](https://github.com/KovaaK/InterAccel)、[MouseTester](https://github.com/microe1/MouseTester)、[accelSwitch](https://github.com/jan-glx/accelSwitch)

### 6.5 工具链本身

| 项目 | 用途 |
|---|---|
| [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) | 本项目的运行环境（DSH），MIT |
| [awesome-dsh-plugin.com/plugins.json](https://awesome-dsh-plugin.com/plugins.json) | DSH 插件市场 registry（4412 个插件，非 GitHub） |

---

## 7. 怎么跑

### 首次准备

```powershell
cd 小黑盒
npm install                 # 恢复 node_modules（当前是联接，换机器要重装）
npx playwright install chromium
```

Python 配图环境（可选）：

```powershell
pip install Pillow numpy
```

### 日常流程

```powershell
# 1. 开常驻浏览器（会弹出窗口，首次需扫码登录小黑盒）
node session.mjs            # 保持这个窗口开着

# 2. 填文 + 截图（不发布）
node publish.mjs articles/xxx.md

# 3. 看截图确认无误后，真正发布
node publish.mjs articles/xxx.md --publish
```

**注意**：`session.mjs` 是个常驻进程，建议放在后台任务里跑，关掉浏览器窗口它会自动退出（这是刻意设计的，避免进程空转）。

### 文章的格式要求

`articles/*.md` 需要 frontmatter：

```markdown
---
title: 标题（超过 30 字会被截断）
community: 盒友杂谈
topics:
ai: true
---

![](assets/cover-xxx.png)

正文……
```

- `title` 必填
- `community` 是关联社区名，会做模糊匹配
- `topics` 留空即可（话题功能没跑通）
- **`ai: true`** 会触发自动勾选「其他声明 → 包含AI辅助创作」。注意代码里是**字符串比较**（`meta.ai === 'true'`），必须写小写 `true`
- 正文里的图片路径**要写对后缀名**（`.jpg` / `.png`），写错会填到一半报错

### 环境变量

如果本机有 hosts 级代理，Node 抓外网需要：

```powershell
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
```

---

## 8. 怎么导出

### 8.1 导出到本地其他位置

直接复制整个文件夹，**但先排除这三项**：

| 排除 | 原因 | 大小 |
|---|---|---|
| `profile/` | ⚠️ **含登录 Cookie，绝对不能带出去** | 86 MB |
| `node_modules/` | 目录联接，复制过去是死链接；用 `npm install` 重建 | 18 MB |
| `_archive/` | 49 个早期脚本，已无用 | 115 KB |

`shots/`（截图，20 MB）可以带，也可以删，纯历史记录。

**PowerShell 复制示例：**

```powershell
$src = "<项目所在路径>\小黑盒"
$dst = "D:\backup\小黑盒"
robocopy $src $dst /E /XD profile node_modules _archive shots
```

### 8.2 上传到 GitHub

**⚠️ 上传前必须先建 `.gitignore`，否则 Cookie 会被推上去。**

项目里现在**没有** `.gitignore`，建议新建一个，内容如下：

```gitignore
# ⚠️ 浏览器用户数据，含登录 Cookie，绝不能提交
profile/

# 依赖
node_modules/
package-lock.json

# 运行产物
shots/
data/

# 早期探索脚本
_archive/

# 系统
Thumbs.db
.DS_Store
desktop.ini

# 编辑器
.vscode/
.idea/
```

**上传步骤：**

```powershell
cd "<项目所在路径>\小黑盒"

# 1. 先建 .gitignore（务必在 git add 之前）
#    内容见上

# 2. 初始化
git init
git add .

# 3. ⚠️ 提交前务必检查：确认 profile/ 没被加进来
git status --short | Select-String "profile/"

# 4. 确认干净后再提交
git commit -m "小黑盒自动发帖工具链"

# 5. 推到远端
git remote add origin <你的仓库地址>
git branch -M main
git push -u origin main
```

**如果已经误提交了 `profile/`：**

`profile/` 里是加密过的 Cookie 文件，但仍然不该公开。清理方式：

```powershell
git rm -r --cached profile
git commit -m "remove profile"
git push
```

**但要注意：`git rm --cached` 只是从最新提交里移除，历史记录里还有。** 如果确实推上去了，最稳妥的做法是**删掉远端仓库重建**，或者用 `git filter-repo` 清理历史。

### 8.3 导出后要改的地方

接手的人从零开始，需要处理这几件事：

1. **重新登录**：`profile/` 没带过去，所以第一次跑 `session.mjs` 要**重新扫码登录小黑盒**
2. **重装依赖**：`npm install` + `npx playwright install chromium`
3. **改 Python 字体路径**：`tools/make_*.py` 里写死了 `C:\Windows\Fonts\msyhbd.ttc`
4. **写作规则不在项目里**：去 AI 味规则和发帖规矩存在 `~/.dsh/AGENTS.md`，**是项目外部文件**，需要单独交接
5. **改路径引用**：`publish.mjs` 和 `session.mjs` 都用 `import.meta.url` 自动定位项目根，**换目录不用改**

---

## 9. ⚠️ 安全须知

**这一节请务必读。**

### 不能外传的东西

| 内容 | 在哪 | 风险 |
|---|---|---|
| **小黑盒登录 Cookie** | `profile/Default/Network/Cookies` | 拿到就能以你的身份登录 |
| **浏览器保存的密码** | `profile/Default/Login Data` | 同上 |
| **加密密钥** | `profile/Local State` | 用于解密上面的 Cookie |
| AstrBot 面板密码 | 项目外部 | — |
| LLM API Key | 项目外部 | — |

### 规则

1. **永远不要把 `profile/` 目录提交到任何版本控制系统。**
2. **`.gitignore` 必须在第一次 `git add` 之前就位。**
3. 分享项目时，**只分享代码和文档**，`profile/`、`data/`、`shots/` 都可以不带。
4. 如果 `profile/` 已经泄露，**立刻去小黑盒改密码并退出所有设备**，这会让旧的 Cookie 失效。
5. 本文档**已经做了脱敏**：不含任何账号名、密码、Cookie 值、API Key、heybox_id。

### 代码本身的安全设计

- `session.mjs` 用的是**本机真实 Chromium**，不是无头浏览器，行为特征上更接近真人
- 关掉了自动化特征（`navigator.webdriver`、`--enable-automation`）
- **但请注意**：小黑盒服务端有风控，**脚本操作频繁会触发腾讯验证码**（实测出现过多次）。发帖频率别太高。

---

## 10. 平台技术限制备忘

这些是实测出来的小黑盒平台事实，**写代码前必须知道**：

| 事项 | 结论 |
|---|---|
| 编辑器类型 | ProseMirror 富文本，直接粘贴 Markdown 会被"降噪"掉格式 |
| 标题层级 | **一级标题 = `<h2>`，二级标题 = `<h3>`；`<h1>` 会被降级成普通段落** |
| 支持的标签 | `p` / `strong` / `blockquote` / `ul` / `ol` / `a` / `h2` / `h3` |
| 不支持的 | **表格、代码块、斜体、下划线、删除线、分隔线** —— 表格必须转成图片 |
| 封面 | **网页版文章编辑器没有封面字段**，正文第一张图即封面 |
| 关联社区 | 必填，上限 2 个 |
| 关联话题 | 上限 5 个（我们的搜索匹配没跑通） |
| AI 声明 | 在「**其他声明**」下拉里，不在「内容声明」；选项文案是「包含AI辅助创作」 |
| 标题长度 | 超 30 字会被截断 |
| 风控 | 服务端有腾讯验证码（`turing.captcha.gtimg.com`），脚本操作频繁会触发 |

**另一个坑**：正文的加粗里**不要放尖括号标签文本**（比如 `<h1>`），小黑盒的解析器会把整段吃掉。要写成「h2 标签，不是 h1」。

---

## 11. 相关文档索引

| 文档 | 位置 | 内容 |
|---|---|---|
| `NOTES.md` | 项目内 | **最重要的技术笔记**，15 节，所有踩坑记录和实测结论 |
| `写作规范.md` | 项目内 | 标题六律、封面规则、正文结构、选题方法、发布自检清单 |
| `去 AI 味规则` | `~/.dsh/AGENTS.md` | ⚠️ **项目外部**，12 条 AI 味特征 + 场景化力度分级 |
| `评论机器人调研` | `refs/评论机器人-调研.md` | 9 个相关项目对比 |
| `AstrBot 部署记录` | `refs/astrbot-部署记录.md` | 部署过程 + 完整风控排查 |
| 已发布文章 | 小黑盒站内 | 见 `articles/` 里的源稿 |

---

## 12. ⚠️ 交接时的在途状态（务必先看这节）

交接时间点上，**有一篇稿子的网页草稿和本地文件不一致**。这是最容易出问题的地方。

### 雾锁王国 1.0 那篇

| 项 | 状态 |
|---|---|
| 网页草稿 | [editor/edit/article/193949060](https://www.xiaoheihe.cn/creator/editor/edit/article/193949060)（需登录访问） |
| 草稿内容 | **停留在 10 月 15 日的版本，落后于本地文件** |
| 本地文件 | `articles/enshrouded-1-0-news.md` ← **这是当前版本** |
| 配图 | `assets/news-enshrouded-1.0/`（4 张官方图 + `SOURCES.md`），引用路径已核对全部有效 |

**本地比草稿多了两处改动：**

1. 上线时间改为**过去时**（「已在 10 月 15 日上线」）
2. 补入了官方 **1.0.0.1 热修复**消息（处理随机崩溃和室内亮度问题）

**所以：如果要继续这篇，必须以本地文件为准重新填充。** 直接去改网页草稿会丢掉这两处更新。

**另外请注意**：交接时用户已明确停止操作小黑盒，**不再点发布**。任何发布动作都需要先跟用户确认。

### 还没有发布的稿子

以下源稿已经填充验证过，但**没有发布**，都在 `articles/`：

| 文件 | 说明 |
|---|---|
| `display-settings.md` | 买了高刷显示器，先查这四个地方 |
| `dlss-fsr-guide.md` | DLSS、FSR、帧生成，到底该开哪个 |
| `github-weekly-1.md` | 本周 GitHub：5 个玩家能用的项目（栏目第 1 期） |
| `mouse-accel.md` | 你关的那个鼠标加速，可能根本没生效 |
| `emulator-guide.md` | 模拟器入门（用户看过，评价「不太行」，已撤） |

---

## 13. 一句话总结

**这套东西能用的部分**：从 Markdown 到发布的全自动链路、网页端的评论自动回复、一套配图生成工具。已经跑通了 7 篇以上的文章。

**不能用的部分**：走 App 接口的评论机器人（服务端风控绕不过去，已改走网页路线）、关联话题（匹配不准）。

**最需要注意的两件事**：

1. `profile/` 目录含登录凭证，**导出和上传前必须排除**
2. 雾锁王国那篇的**网页草稿落后于本地文件**，继续之前先看第 12 节
