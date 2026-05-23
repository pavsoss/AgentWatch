#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# Force UTF-8 output on Windows so special characters render correctly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Make agentwatch importable from repo root in development
sys.path.insert(0, str(Path(__file__).parent))

import httpx

API_BASE = "http://localhost:8000"

# ─────────────────────────────────────────────
# Color helpers
# ─────────────────────────────────────────────

def green(s: str) -> str: return f"\033[92m{s}\033[0m"
def red(s: str) -> str: return f"\033[91m{s}\033[0m"
def yellow(s: str) -> str: return f"\033[93m{s}\033[0m"
def blue(s: str) -> str: return f"\033[94m{s}\033[0m"
def bold(s: str) -> str: return f"\033[1m{s}\033[0m"
def dim(s: str) -> str: return f"\033[2m{s}\033[0m"
def cyan(s: str) -> str: return f"\033[96m{s}\033[0m"


def section(title: str) -> None:
    print(f"\n{bold('-' * 64)}")
    print(f"{bold(blue('  ' + title))}")
    print(bold('-' * 64))


def bar(score: float, width: int = 20) -> str:
    filled = int(score * width)
    empty = width - filled
    b = "█" * filled + "░" * empty
    if score >= 0.7:
        return green(b)
    elif score >= 0.4:
        return yellow(b)
    return red(b)


# ─────────────────────────────────────────────
# HTTP helpers
# ─────────────────────────────────────────────

async def post(client: httpx.AsyncClient, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
    resp = await client.post(f"{API_BASE}{path}", json=body, timeout=10)
    resp.raise_for_status()
    return resp.json()


async def get(client: httpx.AsyncClient, path: str) -> Dict[str, Any]:
    resp = await client.get(f"{API_BASE}{path}", timeout=10)
    resp.raise_for_status()
    return resp.json()


# ─────────────────────────────────────────────
# Build a synthetic agent session
# ─────────────────────────────────────────────

SESSION_ID = f"live-demo-{int(time.time())}"
AGENT_ID   = "agentwatch-demo"
GOAL       = "Audit disk usage and safely clear stale log files"

SESSION_PAYLOAD = {
    "session_id":       SESSION_ID,
    "agent_id":         AGENT_ID,
    "agent_name":       "AgentWatch Demo",
    "framework":        "claude_code",
    "goal":             GOAL,
    "status":           "running",
    "total_tokens":     0,
    "estimated_cost_usd": 0.0,
}

EVENTS = [
    {
        "event_type":           "session.start",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "agent_name":           "AgentWatch Demo",
        "framework":            "claude_code",
        "goal":                 GOAL,
        "step_number":          0,
        "token_usage":          {"prompt_tokens": 512, "completion_tokens": 0, "total_tokens": 512, "estimated_cost_usd": 0.0041},
    },
    {
        "event_type":           "planner.output",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          1,
        "planner_output_preview": (
            "I will audit disk usage: first list the /var/log directory, then identify "
            "files older than 30 days, and truncate them safely without deleting system files."
        ),
        "token_usage":          {"prompt_tokens": 612, "completion_tokens": 88, "total_tokens": 700, "estimated_cost_usd": 0.006},
    },
    {
        "event_type":           "tool.call",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          2,
        "tool_call": {
            "tool_name":    "bash",
            "raw_command":  "df -h /var/log",
            "arguments":    {"command": "df -h /var/log"},
        },
    },
    {
        "event_type":           "tool.result",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          3,
        "status":               "success",
        "tool_result": {
            "tool_name": "bash",
            "output":    "Filesystem      Size  Used Avail Use%\n/dev/sda1        40G   38G  2.0G  95%\n",
        },
    },
    {
        "event_type":           "tool.call",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          4,
        "tool_call": {
            "tool_name":    "bash",
            "raw_command":  "find /var/log -name '*.log' -mtime +30 -size +10M",
            "arguments":    {"command": "find /var/log -name '*.log' -mtime +30 -size +10M"},
        },
        "token_usage":          {"prompt_tokens": 700, "completion_tokens": 55, "total_tokens": 755, "estimated_cost_usd": 0.0065},
    },
    {
        "event_type":           "tool.result",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          5,
        "status":               "success",
        "tool_result": {
            "tool_name": "bash",
            "output":    "/var/log/auth.log.3\n/var/log/syslog.4\n/var/log/kern.log.2",
        },
    },
    # ← This gets BLOCKED by the safety engine
    {
        "event_type":           "tool.call",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          6,
        "status":               "blocked",
        "tool_call": {
            "tool_name":           "bash",
            "raw_command":         "rm -rf /var/log/*",
            "arguments":           {"command": "rm -rf /var/log/*"},
            "affected_resources":  ["/var/log"],
        },
        "safety": {
            "risk_level":      "critical",
            "risk_score":      1.0,
            "blocked":         True,
            "reasons":         ["Recursive deletion of critical system filesystem path /var/log"],
            "matched_policies": ["FS_DELETE_CRITICAL"],
        },
        "is_blocked": True,
    },
    # Agent adapts — uses safe truncate instead
    {
        "event_type":           "planner.output",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          7,
        "planner_output_preview": (
            "rm -rf was blocked. Switching to safe alternative: truncate each old log file "
            "to zero bytes, preserving the file descriptor for running processes."
        ),
        "token_usage":          {"prompt_tokens": 820, "completion_tokens": 72, "total_tokens": 892, "estimated_cost_usd": 0.0078},
    },
    {
        "event_type":           "tool.call",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          8,
        "tool_call": {
            "tool_name":   "bash",
            "raw_command": "truncate -s 0 /var/log/auth.log.3 /var/log/syslog.4 /var/log/kern.log.2",
            "arguments":   {"command": "truncate -s 0 /var/log/auth.log.3 /var/log/syslog.4 /var/log/kern.log.2"},
        },
    },
    {
        "event_type":           "tool.result",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          9,
        "status":               "success",
        "tool_result": {
            "tool_name": "bash",
            "output":    "",
        },
    },
    {
        "event_type":           "tool.call",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          10,
        "tool_call": {
            "tool_name":   "bash",
            "raw_command": "df -h /var/log",
            "arguments":   {"command": "df -h /var/log"},
        },
        "token_usage":          {"prompt_tokens": 920, "completion_tokens": 28, "total_tokens": 948, "estimated_cost_usd": 0.0083},
    },
    {
        "event_type":           "tool.result",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          11,
        "status":               "success",
        "tool_result": {
            "tool_name": "bash",
            "output":    "Filesystem      Size  Used Avail Use%\n/dev/sda1        40G   26G   14G  65%\n",
        },
    },
    {
        "event_type":           "session.end",
        "session_id":           SESSION_ID,
        "agent_id":             AGENT_ID,
        "framework":            "claude_code",
        "step_number":          12,
        "status":               "success",
        "metadata":             {"final_result": "Freed ~12 GB by truncating stale log files. Disk now at 65%."},
        "token_usage":          {"prompt_tokens": 948, "completion_tokens": 60, "total_tokens": 1008, "estimated_cost_usd": 0.009},
    },
]


# ─────────────────────────────────────────────
# WebSocket monitor (background task)
# ─────────────────────────────────────────────

async def ws_monitor(received: list) -> None:
    """Collect events from WebSocket — confirms broadcast is live."""
    try:
        import websockets  # type: ignore[import]
        async with websockets.connect(f"ws://localhost:8000/ws/events") as ws:
            async for raw in ws:
                received.append(raw)
    except Exception:
        pass  # websockets not installed or already closed — that's fine


# ─────────────────────────────────────────────
# Main demo
# ─────────────────────────────────────────────

async def main() -> None:
    print(bold("""
+--------------------------------------------------------------+
|   AgentWatch -- Real-Time Pipeline Demo                       |
|   Events flow: script -> HTTP -> event_bus -> WebSocket -> UI |
|   Dashboard: http://localhost:3000                            |
+--------------------------------------------------------------+
"""))

    # ── Check API health ──────────────────────────────────────────
    section("Verifying API connectivity")
    async with httpx.AsyncClient() as client:
        try:
            health = await get(client, "/health")
            print(f"  {green('✓')} API is live — version {health.get('version', '?')}")
        except Exception as exc:
            print(f"  {red('✗')} Cannot reach {API_BASE}: {exc}")
            print(f"    Run {bold('docker compose up -d')} first.")
            sys.exit(1)

    # ── Start WebSocket listener in background ────────────────────
    ws_received: list = []
    ws_task = asyncio.create_task(ws_monitor(ws_received))

    async with httpx.AsyncClient() as client:

        # ── Register session ──────────────────────────────────────
        section("Registering agent session")
        resp = await post(client, "/api/v1/sessions", SESSION_PAYLOAD)
        print(f"  {green('✓')} Session registered: {cyan(SESSION_ID)}")
        print(f"  Goal: {dim(GOAL)}")

        # ── Stream events one by one ──────────────────────────────
        section("Streaming live events (0.6 s apart)")
        print(f"  Open {bold('http://localhost:3000')} to watch in real time\n")

        for idx, event_body in enumerate(EVENTS):
            resp = await post(client, "/api/v1/events", event_body)
            etype = event_body["event_type"]
            is_blocked = event_body.get("is_blocked") or (
                event_body.get("safety", {}).get("blocked", False)
            )
            step = event_body.get("step_number", idx)

            if is_blocked:
                icon = red("🚫 BLOCKED")
            elif "tool.call" in etype:
                icon = yellow("🔧 TOOL   ")
            elif "planner" in etype:
                icon = cyan("🧠 PLANNER")
            elif "session.start" in etype:
                icon = green("▶  START  ")
            elif "session.end" in etype:
                icon = green("■  END    ")
            else:
                icon = blue("•  RESULT ")

            cmd = ""
            if tc := event_body.get("tool_call"):
                cmd = f"  {dim(repr(tc.get('raw_command', '')[:48]))}"
            if pp := event_body.get("planner_output_preview"):
                cmd = f"  {dim(pp[:60])}…"

            tok = ""
            if tu := event_body.get("token_usage"):
                t_total = tu["total_tokens"]
                t_cost = tu["estimated_cost_usd"]
                tok = f"  {dim(f'[{t_total} tok / ${t_cost:.4f}]')}"

            safety_note = ""
            if is_blocked:
                reasons = event_body.get("safety", {}).get("reasons", [])
                safety_note = f"\n     {red('↳ ' + reasons[0])}" if reasons else ""

            print(f"  [{step:02d}] {icon}{cmd}{tok}{safety_note}")
            await asyncio.sleep(0.6)

        # ── Dashboard summary ─────────────────────────────────────
        section("Dashboard summary (live from API)")
        summary = await get(client, "/api/v1/dashboard/summary")
        print(f"  Total sessions:   {bold(str(summary['total_sessions']))}")
        print(f"  Active sessions:  {summary['active_sessions']}")
        print(f"  Failed sessions:  {red(str(summary['failed_sessions']))}")
        print(f"  Total tokens:     {summary['total_tokens']:,}")
        print(f"  Estimated cost:   ${summary['estimated_cost_usd']:.4f}")
        sstat = summary.get("safety_stats", {})
        print(f"  Safety checked:   {sstat.get('checked', 0)}")
        print(f"  Safety blocked:   {red(str(sstat.get('blocked', 0)))}")
        print(f"  Safety approved:  {green(str(sstat.get('approved', 0)))}")

        # ── Confidence score ──────────────────────────────────────
        section("Confidence score for this session")
        try:
            conf = await get(client, f"/api/v1/sessions/{SESSION_ID}/confidence")
            print(f"  Overall score:    {bar(conf['overall_score'])} {bold(str(round(conf['overall_score'], 3)))}")
            print(f"  Goal alignment:   {bar(conf['goal_alignment'])} {round(conf['goal_alignment'], 3)}")
            print(f"  Consistency:      {bar(conf['consistency_score'])} {round(conf['consistency_score'], 3)}")
            if conf["anomaly_flags"]:
                print(f"\n  {yellow('⚠  Anomalies detected:')}")
                for flag in conf["anomaly_flags"]:
                    print(f"     {yellow('•')} {flag}")
            if conf["component_scores"]:
                print(f"\n  {bold('Component scores:')}")
                for k, v in conf["component_scores"].items():
                    print(f"     {k:<28} {bar(v, 14)} {v:.3f}")
        except Exception as exc:
            print(f"  {yellow('!')} Confidence endpoint: {exc}")

        # ── Safety blocked events ─────────────────────────────────
        section("Safety — blocked events")
        blocked = await get(client, "/api/v1/safety/blocked")
        total_blocked = blocked["total"]
        print(f"  Total blocked in last 24 h: {red(str(total_blocked))}")
        for be in blocked["blocked_events"][:3]:
            tc = be.get("tool_call") or {}
            cmd_str = tc.get("raw_command", "")
            safety = be.get("safety") or {}
            risk = safety.get("risk_level", "?").upper()
            print(f"  {red('🚫')} [{risk}] {dim(cmd_str[:60])}")

        # ── Cost tracking ─────────────────────────────────────────
        section("Cost tracker for this session")
        try:
            cost = await get(client, f"/api/v1/sessions/{SESSION_ID}/cost")
            print(f"  Total tokens:     {cost.get('total_tokens', 0):,}")
            print(f"  Total cost:       ${cost.get('total_cost_usd', 0.0):.6f}")
            if limit := cost.get("budget_limit_usd"):
                used_pct = cost.get("total_cost_usd", 0) / limit * 100
                print(f"  Budget limit:     ${limit:.4f}  ({used_pct:.1f}% used)")
        except Exception as exc:
            print(f"  {yellow('!')} Cost endpoint: {exc}")

        # ── Reasoning audit ───────────────────────────────────────
        section("Reasoning audit for this session")
        try:
            audit = await get(client, f"/api/v1/sessions/{SESSION_ID}/reasoning")
            avg = audit.get("average_score", 0)
            print(f"  Average reasoning score:   {bar(avg)} {bold(str(round(avg, 3)))}")
            print(f"  Weakest step:  {yellow(str(audit.get('weakest_step', 'N/A')))}")
            print(f"  Strongest step: {green(str(audit.get('strongest_step', 'N/A')))}")
            audits = audit.get("audits", [])
            print(f"\n  {bold('Step verdicts:')}")
            for a in audits[:6]:
                verdict_color = green if a["verdict"] == "sound" else yellow if a["verdict"] == "acceptable" else red
                print(f"     [{a['step_index']:02d}] {bar(a['score'], 10)} {a['score']:.3f}  {verdict_color(a['verdict'])}")
        except Exception as exc:
            print(f"  {yellow('!')} Reasoning audit: {exc}")

        # ── WebSocket confirmation ────────────────────────────────
        section("WebSocket broadcast confirmation")
        ws_task.cancel()
        await asyncio.sleep(0.1)
        print(f"  Events received via WebSocket: {bold(str(len(ws_received)))}")
        if ws_received:
            print(f"  {green('✓')} WebSocket broadcast confirmed — dashboard receives live events")
        else:
            print(f"  {yellow('!')} WebSocket confirmation requires the 'websockets' package: pip install websockets")

    # ── All sessions ──────────────────────────────────────────────
    section("All sessions visible to dashboard")
    async with httpx.AsyncClient() as client:
        slist = await get(client, "/api/v1/sessions")
        for s in slist["sessions"][:5]:
            status_color = green if s["status"] == "success" else red if s["status"] == "failure" else yellow
            print(f"  {status_color('•')} {s['session_id'][:40]:<42} {status_color(s['status']):<10} "
                  f"{s.get('total_tokens', 0):>6} tok")

    print(f"\n{bold(green('✓ Pipeline demo complete'))}")
    print(f"\n  {bold('Verify in the dashboard:')}")
    print(f"    {cyan('http://localhost:3000')}  — live event feed, safety blocks, cost tracker")
    print(f"    {cyan('http://localhost:8000/docs')}  — full API docs\n")


if __name__ == "__main__":
    asyncio.run(main())
