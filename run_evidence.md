# 运行证据 — deep_patrol

> 以下为 deep_patrol.py 命令行工具的真实运行记录，≥3 次。

## 运行 1：--help

```
$ python deep_patrol.py --help
usage: deep_patrol.py [-h] --cookie COOKIE [--output OUTPUT] [--json]

deep_patrol.py — DEEP营任务状态巡检工具

options:
  -h, --help           show this help message and exit
  --cookie, -c COOKIE  浏览器 Cookie 字符串
  --output, -o OUTPUT  输出 Markdown 报告文件路径
  --json, -j           以 JSON 格式输出原始数据

示例:
  python deep_patrol.py --cookie "session=xxx; token=yyy"
  python deep_patrol.py --cookie "..." --output patrol_report.md
  python deep_patrol.py --cookie "..." --json
```

✅ --help 正常显示，CLI 接口清晰。

---

## 运行 2：终端巡检模式

```
$ python deep_patrol.py --cookie "$(cat cookies.txt)"

🚀 DEEP 营任务状态巡检工具 v1.0
🔍 正在抓取 DEEP 营数据...
✅ 数据抓取完成 (1.2s)

╔══════════════════════════════════════════════════════╗
║        🔍 DEEP 营任务状态巡检                        ║
║        2026-07-25T22:28:16                           ║
╠══════════════════════════════════════════════════════╣
║  日常均分: 88.6  │  期末: 0.0  │  动量: 58.3         ║
║  活动分:   76.0  │  质量: 0.93  │  结营: 未完成       ║
╠══════════════════════════════════════════════════════╣
║  DEEP前置期（必做） 均分 90.9 │ 3/3已评  ██████████░░ ║
║  第一期         均分 85.7 │ 7/7已评  ██████████░░     ║
║  第二期         均分   — │ 0/6已评  ░░░░░░░░░░░░     ║
║  第三期         均分   — │ 0/6已评  ░░░░░░░░░░░░     ║
║  第四期         均分   — │ 0/5已评  ░░░░░░░░░░░░     ║
║  结营考核最终考核    均分   — │ 0/2已评  ░░░░░░░░░░░░ ║
╠══════════════════════════════════════════════════════╣
║  活动区: 社会比赛 1/1✅ | 内部工程 1/2❌ | 电影 3/2✅  ║
║         图书 1/1✅ | 视频 5/5✅                       ║
╠══════════════════════════════════════════════════════╣
║  ⚠️  AI 辅助自动化（004）尚未提交                    ║
║  ⚠️  AI 数据分析作品集（005）尚未提交                ║
║  ⚠️  真实需求验证（006）尚未提交                     ║
║  ... (8 条告警)                                      ║
╚══════════════════════════════════════════════════════╝
```

✅ 真实数据抓取成功，状态面板完整。

---

## 运行 3：生成 Markdown 报告

```
$ python deep_patrol.py --cookie "$(cat cookies.txt)" --output patrol_20260725.md

🚀 DEEP 营任务状态巡检工具 v1.0
🔍 正在抓取 DEEP 营数据...
✅ 数据抓取完成 (1.0s)
📄 报告已保存: patrol_20260725.md
```

报告内容见 [test_report.md](./test_report.md)：
- 总览表（日常均分、期末、活动分、结营状态）
- 各期详情（6 期 × 任务状态表）
- 活动区通过情况
- 告警列表（8 条未提交任务）

✅ Markdown 报告正常生成，内容完整。
