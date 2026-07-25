# 复用合约 — deep_patrol

## 一行命令

```bash
python deep_patrol.py --cookie "$(cat cookies.txt)" --output patrol_report.md
```

## 依赖安装

```bash
pip install requests
```

以上是唯一依赖。Python 版本要求 ≥3.9。

## 环境变量配置（可选）

```bash
export DEEP_COOKIE="__Secure-authjs.session-token=xxx; __Host-authjs.csrf-token=yyy"
alias patrol="python ~/deep_patrol.py --cookie \"$DEEP_COOKIE\""
```

之后只需 `patrol` 一条命令即可巡检。

## 已知边界

- **不处理 Cookie 过期：** Cookie 过期需手动从浏览器重新获取。不内置登录逻辑（DEEP 营无公开 OAuth API）
- **不做自动提交：** 只读，不写。不会帮你提交任务或修改数据
- **不支持多账号：** 一个 Cookie 对应一个 DEEP 营账号
- **不处理网络故障：** DNS/代理/VPN 问题需自行排查
- **时间依赖 UTC：** 报告时间为 CST (UTC+8)，依赖系统时区
- **不支持离线模式：** 每次运行都实时请求 API，不缓存

## 扩展方向

如果其他人想基于这个工具扩展：

1. 加上 cron 定时任务 → 自动生成日报
2. 接入飞书/钉钉/微信 Webhook → 推送状态变更通知
3. 用 SQLite 存历史 → 画成绩趋势图
4. 多账号管理 → 支持 profiles.yaml

以上都不在本工具范围内，但代码结构留有扩展空间（`generate_report()` 返回结构化 JSON）。
