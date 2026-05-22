
<div align="center">

  <h1>AgentWatch</h1>

  <p><strong>Your AI agent is lying to you.<br/>AgentWatch catches it — before it deletes your database.</strong></p>

  <p>
    <img src="https://img.shields.io/badge/built_with-Python-blue?style=flat-square&logo=python" />
    <img src="https://img.shields.io/badge/status-live-brightgreen?style=flat-square" />
    <img src="https://img.shields.io/badge/license-Apache_2.0-blue?style=flat-square" />
    <img src="https://img.shields.io/badge/tests-47_passing-brightgreen?style=flat-square" />
    <img src="https://img.shields.io/github/stars/sreerevanth/AgentWatch?style=flat-square&color=gold" />
  </p>

</div>

---

## What is AgentWatch?

Every AI agent today makes the same quiet bet: that you won't notice when it fails.

It returns a confident response. It says the task is complete. And three hours later you find out it wrote to the wrong database, deleted the wrong folder, or hallucinated a result so convincingly that nobody caught it.

AgentWatch is the layer that was missing.

It sits between your agent and the world. It watches every action, scores every reasoning step, blocks dangerous commands before they run, and gives you a full replay of exactly what happened — and why.

No more silent failures.

---

## What It Does

| | |
|---|---|
| 🛡️ **Safety Engine** | Blocks dangerous commands before they execute |
| 🧠 **Reasoning Auditor** | Scores every reasoning step — not just the final output |
| 📊 **Live Dashboard** | Real-time trace of every action your agent takes |
| ⏪ **One-Click Rollback** | Git-backed checkpoints at every step |
| 💾 **Persistent Memory** | Your agent remembers context across sessions |
| 💰 **Cost Tracker** | Per-session token budget with live spend alerts |
| 🔔 **Alerting** | Slack + PagerDuty when confidence drops or actions are blocked |
| 📋 **Compliance** | GDPR/HIPAA audit exports, full RBAC governance |
| 🔌 **Universal** | Claude Code, LangChain, AutoGPT, OpenClaw — no rewrites |

---

## Quick Start

```bash
pip install agentwatch
docker compose up -d
```

Dashboard → http://localhost:3000
API → http://localhost:8000/docs

---

## Supported Agents

AgentWatch wraps your existing agent. You change nothing.

### Claude Code
```bash
agentwatch watch "Build me a REST API"
```

### LangChain
```python
from agentwatch.adapters.langchain import AgentWatchCallbackHandler

handler = AgentWatchCallbackHandler()
agent = AgentExecutor(agent=..., callbacks=[handler])
```

### AutoGPT
```python
from agentwatch.adapters.autogpt import AutoGPTAdapter

adapter = AutoGPTAdapter(session_id="session-1")
await adapter.on_action(action)
```

### OpenClaw
```python
from agentwatch.adapters.openclaw import OpenClawAdapter

adapter = OpenClawAdapter(session_id="session-1")
await adapter.on_skill_execution(skill_name, payload)
```

---

## The Reasoning Auditor

This is the part nobody else has.

Every AI agent scores its own work. And it almost always thinks it did well — even when it didn't. AgentWatch uses an independent model to score every reasoning step before the next action fires.

```python
from agentwatch.reasoning.auditor import ReasoningAuditor

auditor = ReasoningAuditor()
result = await auditor.score_step(step)

print(result.confidence)          # 0.0 – 1.0
print(result.hallucination_risk)  # low / medium / high
print(result.goal_drift)          # True if agent is off-task
```

When confidence drops below your threshold, AgentWatch fires an alert and holds the next action — before it causes damage.

---

## Safety Engine

```python
from agentwatch.core.safety import SafetyEngine

engine = SafetyEngine()
result = await engine.check_event(event)

if result.is_blocked:
    print(f"Blocked: {result.safety.reasons}")
    print(f"Risk level: {result.safety.risk_level.value}")
```

Blocked by default: `rm -rf /`, `curl | bash`, disk formatting,
credential exfiltration, and 40+ other critical patterns.

---

## Rollback

```bash
agentwatch rollback <session-id> --to-step 12
```

Or just click rollback in the dashboard. Every checkpoint is a full
filesystem snapshot backed by git. Irreversible actions become reversible.

---

## REST API

```
GET  /api/v1/sessions
GET  /api/v1/sessions/{id}/replay
GET  /api/v1/sessions/{id}/confidence
GET  /api/v1/sessions/{id}/checkpoints
POST /api/v1/sessions/{id}/rollback
GET  /api/v1/safety/blocked
GET  /api/v1/dashboard/summary
WS   /ws/events
```

---

## Stack

- **Backend** — FastAPI, PostgreSQL, Redis, Celery
- **Frontend** — Next.js, Tailwind, Recharts, WebSockets
- **Infra** — Docker Compose, GitHub Actions CI
- **Telemetry** — OpenTelemetry compatible

---

## Verified

```
✅ 47/47 tests passing
✅ docker compose up — zero errors  
✅ API live at localhost:8000
✅ Dashboard live at localhost:3000
✅ Claude Code, LangChain, AutoGPT, OpenClaw adapters working
```

---

## License

Apache 2.0

---

<div align="center">
  <sub>Built by <a href="https://github.com/sreerevanth">sreerevanth</a> · Issues → open one · Questions → open one</sub>
</div>
```


