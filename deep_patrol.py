#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deep_patrol.py — DEEP营任务状态巡检工具

自动抓取 DEEP 营考核平台的任务、成绩、活动区数据，
生成终端状态面板 + Markdown 报告，省去每次手动打开网页的重复操作。

Usage:
  python deep_patrol.py --cookie "<session-cookie>"           # 终端巡检
  python deep_patrol.py --cookie "<cookie>" --output report.md  # 生成报告
  python deep_patrol.py --cookie "<cookie>" --json              # JSON输出
  python deep_patrol.py --help                                  # 查看帮助
"""

import sys
import json
import time
import argparse
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))

# Fix Windows GBK encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    print("❌ 缺少 requests 库。运行: pip install requests")
    sys.exit(1)

BASE_URL = "https://www.mangoleaningos.top"
API_GRADES = f"{BASE_URL}/api/grades"
API_ACTIVITY = f"{BASE_URL}/api/activity/submissions"

# ── Data Fetching ──────────────────────────────────────────────────────

def fetch_json(session, url, label="data"):
    """Fetch JSON from API with error handling."""
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code == 401:
            print(f"❌ 认证失败：Cookie 已过期，请重新获取")
            return None
        if not resp.ok:
            print(f"⚠️  {label} 接口返回 {resp.status_code}")
            return None
        return resp.json()
    except requests.RequestException as e:
        print(f"⚠️  网络错误 ({label}): {e}")
        return None


def fetch_all(session):
    """Fetch all relevant DEEP营 data."""
    print("🔍 正在抓取 DEEP 营数据...")
    grades = fetch_json(session, API_GRADES, "成绩")
    # Activity submissions
    activity = fetch_json(session, API_ACTIVITY, "活动区")
    return grades, activity


# ── Report Generation ──────────────────────────────────────────────────

def generate_report(grades, activity):
    """Generate structured report from API data."""
    report = {
        "generated_at": datetime.now(CST).isoformat(),
        "summary": {},
        "phases": [],
        "activity": {},
        "warnings": []
    }

    if not grades:
        report["warnings"].append("无法获取成绩数据，Cookie 可能已过期")
        return report

    # ── Overall metrics ──
    daily = grades.get("dailyAverage", 0)
    final_avg = grades.get("finalAverage", 0)
    activity_score = grades.get("activityTotal", 100)
    effective_activity = grades.get("effectiveActivity", 0)
    quality = grades.get("qualityCoefficient", 0)
    momentum = grades.get("momentum", 0)
    scoring = grades.get("scoring", {})
    dimensions = scoring.get("dimensions", {})
    completion = grades.get("completion", {})

    report["summary"] = {
        "日常均分": daily,
        "期末均分": final_avg,
        "活动总分": activity_score,
        "有效活动分": effective_activity,
        "质量系数": quality,
        "动量分": momentum,
        "结营状态": "已完成" if completion.get("completed") else "未完成",
        "结营Track": completion.get("track", "none"),
    }

    if completion.get("reasons"):
        report["summary"]["未完成原因"] = completion["reasons"]

    # ── Per-phase breakdown ──
    for phase in grades.get("phases", []):
        phase_name = phase.get("phaseName", "Unknown")
        phase_avg = phase.get("phaseAverage")
        tasks = phase.get("tasks", [])

        phase_data = {
            "name": phase_name,
            "average": phase_avg,
            "task_count": len(tasks),
            "graded_count": sum(1 for t in tasks if t.get("status") == "GRADED"),
            "submitted_count": sum(1 for t in tasks if t.get("status") in ("GRADED", "SUBMITTED")),
            "tasks": []
        }

        for t in tasks:
            task_info = {
                "title": t.get("taskTitle", ""),
                "status": t.get("status") or "未提交",
                "final_score": t.get("finalScore"),
                "ai_score": t.get("aiScore"),
            }
            phase_data["tasks"].append(task_info)

            # Warn on low scores or missing submissions
            score = t.get("finalScore")
            status = t.get("status")
            if status == "GRADED" and score is not None and score < 75:
                report["warnings"].append(
                    f"{t.get('taskTitle','')} 得分 {score} < 75（卓越门槛）"
                )
            if not status:
                report["warnings"].append(
                    f"{t.get('taskTitle','')} 尚未提交"
                )

        report["phases"].append(phase_data)

    # ── Activity completion ──
    act_comp = grades.get("activityCompletion", {})
    report["activity"] = {
        "passed": act_comp.get("passed", False),
        "missing_categories": grades.get("missingCategories", 0),
        "details": act_comp.get("details", [])
    }

    # ── Tier gates ──
    gates = grades.get("tierGates", {})
    report["gates"] = gates

    # ── Stats summary ──
    total_tasks = sum(len(p.get("tasks", [])) for p in grades.get("phases", []))
    graded = sum(1 for p in grades.get("phases", [])
                 for t in p.get("tasks", []) if t.get("status") == "GRADED")
    report["summary"]["总任务数"] = total_tasks
    report["summary"]["已评分"] = graded
    report["summary"]["评分率"] = f"{graded}/{total_tasks}"

    return report


# ── Terminal Output ────────────────────────────────────────────────────

def terminal_report(report):
    """Print a formatted terminal report."""
    s = report.get("summary", {})

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║        🔍 DEEP 营任务状态巡检                        ║")
    print(f"║        {report.get('generated_at','')[:19]}                     ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║  日常均分: {s.get('日常均分',0):.1f}  │  期末: {s.get('期末均分',0):.1f}  │  动量: {s.get('动量分',0):.1f}   ║")
    print(f"║  活动分:   {s.get('有效活动分',0):.1f}  │  质量: {s.get('质量系数',0):.2f}  │  结营: {s.get('结营状态','?')}  ║")
    print("╠══════════════════════════════════════════════════════╣")

    # Per phase
    for phase in report.get("phases", []):
        avg_str = f"{phase['average']:.1f}" if phase['average'] else "—"
        bar = _score_bar(phase['average'] or 0)
        print(f"║  {phase['name']:<12s}  均分 {avg_str:>4s}  │ {phase['graded_count']}/{phase['task_count']}已评  {bar} ║")

    print("╠══════════════════════════════════════════════════════╣")

    # Activity
    act = report.get("activity", {})
    cat_strs = []
    for d in act.get("details", []):
        icon = "✅" if d.get("met") else "❌"
        cat_strs.append(f"{d.get('label','')} {d.get('current','?')}/{d.get('required','?')}{icon}")
    print(f"║  活动区: {' │ '.join(cat_strs)} ║")

    print("╠══════════════════════════════════════════════════════╣")

    # Warnings
    warnings = report.get("warnings", [])
    if warnings:
        for w in warnings[:8]:
            safe_w = w[:55]
            print(f"║  ⚠️  {safe_w}{' '*(max(0,53-len(safe_w)))}║")
    else:
        print("║  ✅ 无告警                                                ║")

    print("╚══════════════════════════════════════════════════════╝")
    print()


def _score_bar(score, width=12):
    """Tiny ASCII score bar."""
    filled = min(int(score / 100 * width), width)
    return "█" * filled + "░" * (width - filled)


# ── Markdown Output ────────────────────────────────────────────────────

def markdown_report(report, filepath):
    """Generate a Markdown report file."""
    s = report.get("summary", {})

    lines = []
    lines.append(f"# 🔍 DEEP 营任务状态巡检报告")
    lines.append(f"")
    lines.append(f"**生成时间：** {report.get('generated_at','')[:19]}")
    lines.append(f"")

    lines.append(f"## 📊 总览")
    lines.append(f"")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| 日常均分 | **{s.get('日常均分',0):.1f}** |")
    lines.append(f"| 期末均分 | {s.get('期末均分',0):.1f} |")
    lines.append(f"| 有效活动分 | {s.get('有效活动分',0):.1f} |")
    lines.append(f"| 质量系数 | {s.get('质量系数',0):.2f} |")
    lines.append(f"| 动量分 | {s.get('动量分',0):.1f} |")
    lines.append(f"| 结营状态 | {s.get('结营状态','?')} |")
    lines.append(f"| 已评分/总任务 | {s.get('评分率','?')} |")
    lines.append(f"")

    # Unmet conditions
    reasons = s.get("未完成原因", [])
    if reasons:
        lines.append(f"### ⚠️ 未满足的结营条件")
        for r in reasons:
            lines.append(f"- {r}")
        lines.append(f"")

    # Per phase
    lines.append(f"## 📋 各期详情")
    lines.append(f"")
    for phase in report.get("phases", []):
        avg_str = f"**{phase['average']:.1f}**" if phase['average'] else "—"
        lines.append(f"### {phase['name']}（均分 {avg_str}，{phase['graded_count']}/{phase['task_count']} 已评）")
        lines.append(f"")
        lines.append(f"| 任务 | 状态 | 得分 |")
        lines.append(f"|------|------|------|")
        for t in phase["tasks"]:
            status_icon = {"GRADED": "✅", "SUBMITTED": "📤"}.get(t["status"], "⬜")
            score_str = f"{t['final_score']:.1f}" if t.get('final_score') else "—"
            lines.append(f"| {t['title'][:40]} | {status_icon} {t['status']} | {score_str} |")
        lines.append(f"")

    # Activity
    act = report.get("activity", {})
    lines.append(f"## 🎯 活动区")
    lines.append(f"")
    for d in act.get("details", []):
        icon = "✅" if d.get("met") else "❌"
        lines.append(f"- {icon} {d.get('label','')}: {d.get('current','?')}/{d.get('required','?')}")
    lines.append(f"")
    lines.append(f"**活动区通过：** {'✅ 是' if act.get('passed') else '❌ 否（缺少 ' + str(report.get('activity',{}).get('missing_categories',0)) + ' 类）'}")
    lines.append(f"")

    # Warnings
    warnings = report.get("warnings", [])
    if warnings:
        lines.append(f"## ⚠️ 告警")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append(f"")

    lines.append(f"---")
    lines.append(f"*Generated by deep_patrol.py — DEEP营任务状态巡检工具*")

    content = "\n".join(lines)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 报告已保存: {filepath}")


# ── CLI Entry ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="deep_patrol.py — DEEP营任务状态巡检工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python deep_patrol.py --cookie "session=xxx; token=yyy"
  python deep_patrol.py --cookie "..." --output patrol_report.md
  python deep_patrol.py --cookie "..." --json
        """
    )
    parser.add_argument("--cookie", "-c", required=True,
                        help="浏览器 Cookie 字符串（从 DevTools > Network > Request Headers 复制）")
    parser.add_argument("--output", "-o",
                        help="输出 Markdown 报告文件路径")
    parser.add_argument("--json", "-j", action="store_true",
                        help="以 JSON 格式输出原始数据")

    args = parser.parse_args()

    session = requests.Session()
    session.headers.update({
        "Cookie": args.cookie,
        "User-Agent": "DeepPatrol/1.0 (DEEP营巡检工具)",
        "Accept": "application/json",
    })

    print("🚀 DEEP 营任务状态巡检工具 v1.0")
    start = time.time()

    grades, activity = fetch_all(session)
    elapsed = time.time() - start

    if not grades:
        print("\n💡 提示: 请从浏览器 DevTools 获取有效 Cookie:")
        print("   1. 打开 https://www.mangoleaningos.top 并登录")
        print("   2. F12 > Application > Cookies > 复制所有 cookie")
        print("   3. 或用 --cookie-file 从文件读取")
        sys.exit(1)

    report = generate_report(grades, activity)
    print(f"✅ 数据抓取完成 ({elapsed:.1f}s)")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        terminal_report(report)

    if args.output:
        markdown_report(report, args.output)


if __name__ == "__main__":
    main()
