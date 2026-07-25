# DEEP 营任务状态巡检工具 — deep_patrol

> 痛点：每次想看任务状态/成绩/活动区进展，都要手动打开网页→等加载→逐个看。本周至少重复了 5 次。

## 一句话

自动抓取 DEEP 营考核平台的成绩 API，生成终端状态面板 + Markdown 报告。

## 为什么选它

| 选择 | 为什么 |
|------|--------|
| Python CLI | 单文件，≤200 行，`--help` 即上手 |
| requests 库 | 标准库替代，只依赖一个 pip 包 |
| DEEP 营真实 API | 不爬页面 DOM，直接调 `/api/grades`，稳定可靠 |
| 终端 + Markdown 双输出 | 终端快速扫一眼，Markdown 存档可对比历史 |

## 用法

```bash
# 安装依赖
pip install requests

# 获取 Cookie（只做一次）
# 1. 浏览器打开 https://www.mangoleaningos.top 并登录
# 2. F12 → Application → Cookies → 找到 __Secure-authjs.session-token
# 3. 保存到 cookies.txt

# 终端巡检
python deep_patrol.py --cookie "$(cat cookies.txt)"

# 生成 Markdown 报告
python deep_patrol.py --cookie "$(cat cookies.txt)" --output patrol_$(date +%Y%m%d).md

# JSON 输出（可管道给其他工具）
python deep_patrol.py --cookie "$(cat cookies.txt)" --json
```

## 输出示例

```
╔══════════════════════════════════════════════════════╗
║        🔍 DEEP 营任务状态巡检                        ║
╠══════════════════════════════════════════════════════╣
║  日常均分: 88.6  │  期末: 0.0  │  动量: 58.3   ║
║  活动分:   76.0  │  质量: 0.93  │  结营: 未完成  ║
╠══════════════════════════════════════════════════════╣
║  DEEP前置期（必做）   均分 90.9  │ 3/3已评  ██████████░░ ║
║  第一期           均分 85.7  │ 7/7已评  ██████████░░ ║
║  第二期           均分    —  │ 0/6已评  ░░░░░░░░░░░░ ║
╚══════════════════════════════════════════════════════╝
```

## 工具是什么

- **输入：** DEEP 营会话 Cookie
- **输出：** 终端彩色面板 + Markdown 报告文件
- **不会做的事：** 不会提交任务、不会修改数据、不会自动刷新（你可以自己加 cron）
- **适用场景：** 每天打开电脑想看一眼进度的时候，跑一条命令就行

## 技术实现

```
deep_patrol.py (180 lines)
├── fetch_json()     → GET /api/grades  + /api/activity/submissions
├── generate_report() → 结构化 JSON 报告（按期分组、告警生成）
├── terminal_report() → ASCII 表格 + 进度条输出
└── markdown_report() → 完整 Markdown 文件
```

---

*Built with Claude Code — 2026-07-25*
