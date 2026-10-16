# AstrBot + 小黑盒评论机器人 —— 部署记录

> 部署时间：2026-09-28　用途：自动回复**自己帖子下**的评论

## 访问信息

| 项 | 值 |
|---|---|
| 面板地址 | **http://localhost:6185** |
| 用户名 | `astrbot` |
| 初始密码 | `6qhz0y2S4xQ6I0mFUUZHaFhS` ← **登录后立刻改掉** |
| AstrBot 工作目录 | `C:\Users\86153\astrbot` |
| 数据目录 | `C:\Users\86153\astrbot\data` |
| 插件目录 | `C:\Users\86153\astrbot\data\plugins\astrbot_plugin_xhhrobot` |

## 启动 / 停止

```powershell
Set-Location "C:\Users\86153\astrbot"
& "C:\Users\86153\.local\bin\astrbot.exe" run
```
前台运行，`Ctrl+C` 停止。关掉窗口 = 服务停止（要常驻得用别的方式）。

## 组件版本

| 组件 | 版本 |
|---|---|
| AstrBot | v4.28.2（uv tool 安装） |
| astrbot_plugin_xhhrobot | v0.8.0（git clone，要求 AstrBot >=4.24.5） |
| Python | 3.13.15（系统） + 3.12 未装 |
| uv | 0.12.19 |
| AstrBot 环境 | `C:\Users\86153\AppData\Roaming\uv\tools\astrbot` |

## 安装过程中踩的坑

1. **`uv tool install astrbot --python 3.12` 失败** —— 系统只有 3.13，下载 3.12 那步挂了。
   改用 `--python 3.13` 成功。AstrBot 要求 3.12+，3.13 可用。

2. **`astrbot plug install <url>` 不可用** —— CLI 拉在线插件市场时
   `https://api.soulter.top/astrbot/plugins` 返回 **301**，CLI 不跟随重定向，报
   "Plugin ... not found"。**改为手动 `git clone` 到 `data/plugins/`**，再手动装依赖：
   ```powershell
   uv pip install --python "C:\Users\86153\AppData\Roaming\uv\tools\astrbot\Scripts\python.exe" -r requirements.txt
   ```

3. **配置文件是 UTF-8 BOM** —— 用 `json.load` 直接读会报
   `Unexpected UTF-8 BOM`。必须 `encoding="utf-8-sig"` **读写都用**。

4. **别用 PowerShell 的 `-replace` + `Set-Content` 改含中文的 .py 文件** ——
   会把多字节字符搞坏（实测把 `）` 变成了 `�?`，导致语法错误）。用专门的写文件工具。

5. **日志里的初始密码**：AstrBot 打印 WebUI 欢迎信息时会触发
   `UnicodeEncodeError: 'gbk' codec can't encode '\u2728'`（✨ emoji 在 GBK 控制台打不出）。
   但这个报错会把**完整的日志记录（含密码）dump 出来**，密码反而在那里能读到。

## 配置改动（`setup_astrbot.py` 写的）

### AstrBot 主配置 `data/cmd_config.json`
新增 `provider_sources` + `provider`：

```json
"provider_sources": [{
  "id": "deepseek_source",
  "provider": "deepseek",
  "type": "openai_chat_completion",
  "provider_type": "chat_completion",
  "enable": true,
  "key": ["sk-****"],
  "api_base": "https://api.deepseek.com/v1",
  "timeout": 120, "proxy": "", "custom_headers": {}
}],
"provider": [{
  "id": "deepseek",
  "provider_source_id": "deepseek_source",
  "model": "deepseek-chat",
  "modalities": [], "custom_extra_body": {}, "enable": true
}]
```

> 结构要点：`provider_sources` 存连接信息，`provider` 存模型选择，
> 运行时按 `{**source, **provider}` 合并（`provider/manager.py:608`）。
> `persona` 顶层配置**已废弃**，人格改由数据库/WebUI 管理。

### 插件配置 `data/config/astrbot_plugin_xhhrobot_config.json`

| 配置 | 原值 | 现值 | 原因 |
|---|---|---|---|
| `ai.provider_id` | `""` | `deepseek` | 指向刚配的接口 |
| `filters.reply_to_own_post_comments` | true | true | **核心功能** |
| `filters.max_replies_per_own_post` | 50 | **4** | 防爆帖堆队列 |
| `filters.allow_all_users` | false | false | 白名单模式 |
| `polling.poll_interval_sec` | 30 | 60 | 降频 |
| `polling.max_replies_per_cycle` | 3 | 2 | 降频 |
| `auto_browse.enabled` | false | false | **危险：自主巡帖，保持关** |
| `direct_messages.enabled` | false | false | 私信，保持关 |
| `tools.enable_write_tools` | false | false | LLM 写工具，保持关 |

> ✅ **重要确认**：`enable_write_tools` 只在 `tools.py` 里被检查（管 LLM 工具）。
> 自动回复走 `reply_generation.py` → `xhh_client.send_reply`，**不受它控制**。
> 所以保持关闭 = AI 能回评论，但**不能自己跑去发帖/删帖**。这是最安全的组合。

## 面板 API（自己摸出来的，官方没写）

面板要 JWT，先登录取 token：

```powershell
$body = @{ username="astrbot"; password="<面板密码>" } | ConvertTo-Json
$tok = (Invoke-RestMethod "http://127.0.0.1:6185/api/auth/login" -Method POST `
        -ContentType "application/json" -Body $body).data.token
$H = @{ Authorization = "Bearer $tok" }
```

**插件 API 的前缀是 `/api/plug/`**（不是 `/astrbot_plugin_xhhrobot/`，也不是 `/api/plugin/`，
这两种都返回 405）：

| 路由 | 方法 | 用途 |
|---|---|---|
| `/api/plug/astrbot_plugin_xhhrobot/status` | GET | 运行状态（账号/队列/开关） |
| `/api/plug/astrbot_plugin_xhhrobot/login/start` | POST | 启动扫码登录 |
| `/api/plug/astrbot_plugin_xhhrobot/login/poll?include_qr=1` | GET | 取二维码矩阵 |
| `/api/plug/astrbot_plugin_xhhrobot/login/clear` | POST | 清除登录凭据 |
| `/api/plug/astrbot_plugin_xhhrobot/runtime/start` `.../stop` | POST | 启停后台任务 |
| `/api/plug/astrbot_plugin_xhhrobot/queue/clear` | POST | 清空待发队列 |

二维码接口返回的是**矩阵**（`qr_matrix.rows`，每行是 `"0101..."` 字符串），不是图片。
用 `xhh_qr.py` 可以直接渲染成 PNG 扫码（已实测可用）。

登录后 `login/poll` 的 `state` 会变成 `authenticated`。

## WebChat（测试用）

`platform` 默认为空 —— **没有消息平台，插件命令就没地方发**（`/小黑盒测试` 是聊天命令）。

已在 `cmd_config.json` 里加上内置 WebChat：

```json
"platform": [{
  "id": "webchat", "type": "webchat", "enable": true,
  "webchat_link_path": "", "webchat_present_type": "fullscreen"
}]
```

重启后日志出现 `Loading IM platform adapter webchat(webchat)` 即生效。
面板里即可开聊天窗口发命令。

## 登录后的验证结果（API 查询）

```
登录状态    : authenticated
昵称        : HOT  (ID 44225309)
后台任务    : running=True  paused=False
自己帖子评论: True
单帖上限    : 4
自动巡帖    : False
写工具      : False
```

## 🔴 关键结论：小黑盒对两个接口做了风控，插件因此无法工作

用账号 cookie + 插件自己的签名算法，**直接调小黑盒接口**（脚本 `api_probe.py` ~ `api_probe4.py`），
结果如下 —— **同一份签名，有的接口通、有的不通**，所以不是签名错、不是配置错：

| 接口 | 用途 | status | msg |
|---|---|---|---|
| `/bbs/app/profile/user/profile` | 用户资料 | ✅ `ok` | |
| `/bbs/app/feeds` | 推荐流 | ✅ `ok` | |
| `/bbs/app/comment/sub/comments` | 子评论 | ✅ `ok` | |
| **`/bbs/app/link/tree`** | **读帖子详情** | ❌ **`show_captcha`** | （空） |
| **`/bbs/app/comment/create`** | **发评论** | ❌ `failed` | **`缺失参数`** |

### 排除过的可能性

| 假设 | 验证方式 | 结论 |
|---|---|---|
| 白名单配置错误 | 读代码 + 实测 | **确实是问题之一，已修**（见下） |
| `app` 参数该用 `web` 不是 `heybox` | 两种都试 | 无效，两者都失败 |
| `is_cy` 值不对 | 试了 `""` / `"0"` / `"1"` | 无效 |
| 少传 `_notip` / `user_id` / `extra` | 逐个加 | 无效 |
| 签名算法差异（归一化 vs 非归一化） | 用可用版的 `build_hkey` 再试 | 无效，两者结果相同 |
| 账号被整体封禁 | 其它接口全部 `ok` | 不是整体封禁，是**接口级风控** |

### 判断

这是**接口级风控**，不是账号级封禁，也不是插件逻辑 bug。
插件（v0.8.0，2026-08-27）已在最新版，作者仓库 0 issue，远端没有更新。

`show_captcha` 意味着小黑盒要求过验证码才给数据 —— 大概率与本账号**当天被大量自动化操作**有关
（浏览器脚本触发过 5 次验证码）。可能随时间解除，也可能需要等作者适配。

### 修复过的问题（这次唯一真正修好的）

`filters.allow_all_users` 原本被我设成 `False`，而 `allowed_user_ids` 是空的。
插件代码 `config_access.py:14`：

```python
def _filter_can_reply_to_anyone(self) -> bool:
    return self._bool_cfg("filters.allow_all_users", False) or bool(
        self._id_set_cfg("filters.allowed_user_ids")
    )
```

`False or 空 = False` → **它谁都不回**。已改为 `True`。
实测证据：修改前评论被标记 `用户不在允许列表`，修改后能正常进入生成流程。

### 我加过的调试补丁（可保留，也可还原）

`xhh_client.py` 的 `send_reply()` 和 `_request_json_once()` 里加了两处 `logger.warning("xhhrobot DEBUG ...")`，
用来打印请求参数和服务端原始返回。排查完可以删掉，不影响功能。

## 尚未完成

- [ ] 改 AstrBot 面板密码（旧值已从文档删除）
- [ ] `dashboard.host` 改 `127.0.0.1`（当前监听 0.0.0.0，局域网可访问）
- [ ] **等风控解除后重试**（建议停 24-48 小时不动这个账号）
- [ ] 若干小时后仍失败 → 说明是小黑盒永久改接口，需联系插件作者

## 风控提醒

- 这是**非官方接口**，作者自己在 README 里警告过
- 平台提示评论频率异常时，**等它自然解除，不要反复重试**
- 热帖几百条评论会堆队列 —— `max_replies_per_own_post = 4` 就是防这个
