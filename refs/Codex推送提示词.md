# 给 Codex 的推送提示词

> 直接整段复制给 Codex 即可。

---

这个项目已经配好 GitHub 推送，你不需要做任何认证配置，直接 `git push` 就能工作。

## 项目信息

- 本地路径：`C:\Users\86153\OneDrive\桌面\DSH\自媒体\小黑盒`
- 远端：`git@github.com:leozhang886/xiaoheihe-publish.git`
- 分支：`main`
- 提交作者：`雷张 / 103171726@qq.com`（用户已知晓会公开，不要改）

## 推送已经配好，别再折腾认证

`.git/config` 里有：

```
core.sshCommand = ssh -i C:/Users/86153/OneDrive/桌面/DSH/自媒体/小黑盒/_id886 -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new
```

所以**直接在项目目录执行 `git push` 就行**。

**不要做这些事：**

- 不要改 `core.sshCommand`
- 不要动 `~/.ssh`（**这个目录没有写权限**，尝试写入会失败）
- 不要试图新建 SSH key 或改 `~/.ssh/config`
- 不要改 git 用户名/邮箱

私钥在项目根目录的 `_id886`，已经在 `.gitignore` 里，**绝对不要提交它，也不要打印它的内容**。

## 提交前必须检查

```powershell
git status --porcelain
```

**以下路径绝不能被提交**（`.gitignore` 已挡住，但改动 `.gitignore` 时要小心别删掉这些规则）：

| 路径 | 原因 |
|---|---|
| `profile/` | 浏览器用户数据，**含小黑盒登录 Cookie** |
| `_id886` / `_id886.pub` | SSH 私钥 |
| `_xhh-cookie*.json` / `*.txt` | 导出的登录态 |
| `node_modules/` | 目录联接 |
| `shots/` | 调试截图 |
| `data/` | 运行产物 |

**如果 `git status` 里出现了上表任何一项，先停下来告诉用户，不要提交。**

## 提交信息怎么写

用中文，说清楚改了什么、为什么。参考已有提交：

```
封面自动化打通 + 技能化
gitignore: 忽略本机 SSH 私钥 _id886*
新增 8 篇稿子 + 排版质检工具链
```

不要写 `update`、`fix bug` 这种没有信息量的。

## 提交流程

```powershell
# 1. 看一眼改了什么
git status --porcelain

# 2. 确认没有敏感文件（对照上面的表）

# 3. 提交
git add -A
git commit -m "中文说明：改了什么，为什么"

# 4. 推送
git push
```

## 推送后验证

```powershell
git status -sb
```

应该看到 `## main...origin/main`，没有 `[ahead N]`。

## 如果推送失败

**先看报错原文，不要猜。** 常见情况：

| 报错 | 含义 | 处理 |
|---|---|---|
| `Permission denied (publickey)` | 私钥没被用上 | 检查 `git config core.sshCommand` 是否还在 |
| `Permission to ... denied to leozhang878` | 用错账号了 | 说明 `-i _id886` 没生效 |
| `Everything up-to-date` | 没东西要推 | 正常，不是失败 |
| `Connection timed out` | 网络 | 本机有代理，重试一次 |

**遇到解决不了的，把完整报错贴给用户，不要自己改认证配置。**

---

## 附：这个项目在做什么（供理解上下文）

小黑盒（xiaoheihe.cn）自动发稿工具链：

- `articles/*.md` —— 文章源稿（带 frontmatter）
- `tools/cover-publish.mjs` —— 自包含发布脚本：起浏览器 → 勾创作计划 → 选文章计划 → 上传内容封面 → 发布
- `tools/check-readability.mjs` —— 排版验收，要求 `合计问题: 0`
- `tools/make_cover_v2.py` —— 封面生成
- `refs/` —— 写作规则、封面规则、创作激励规则、标题公式库、封面问题排查记录

**发布是真实操作，会发到公开平台。没有用户明确指示，不要执行 `--publish`。**
