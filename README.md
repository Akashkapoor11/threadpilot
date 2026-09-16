# ThreadPilot - AS-01 Coordination Intelligence

> **From “something changed” to “who is affected, what depends on it, what approval is required, what is blocked, and what happens next.”**

ThreadPilot is a focused coordination-intelligence layer for architecture, interior design and construction projects. It ingests unstructured project updates and turns them into evidence-backed signals, owners, dependencies, approvals, actions and audit history.

## Why this is an AS-01 fit

ArchScale AS-01 asks for a system that connects stakeholders, responsibilities, activities, changes, dependencies, approvals and actions. ThreadPilot deliberately solves that one painful intervention rather than becoming a generic construction ERP.

| AS-01 capability | ThreadPilot proof |
|---|---|
| Stakeholder & role management | Live role/focus/status management for project stakeholders |
| Activity & change tracking | Persistent multi-channel project memory |
| Impact identification | Evidence-linked signals + impact chain |
| Dependency management | Graph generated from live signals and consequence metadata |
| Action tracking | P0/P1 action queue with owner, due state and confirmation |
| Approval management | Explicit approval signals and human decision gates |
| Coordination alerts | Recipient/channel routing with audit trail |
| Project memory | PostgreSQL source history + append-only-style event audit |

## Intelligence architecture: API first, fallback second

The runtime order is intentionally:

```text
New project update
       |
       v
OpenAI-compatible intelligence API
       |
       +---- valid structured result ----> PostgreSQL -> React UI
       |
       +---- unavailable / invalid ------> local evidence engine
                                             |
                                             v
                                     PostgreSQL -> React UI
```

When `LLM_API_KEY` and `LLM_BASE_URL` are configured, the provider is the **primary** path. The response must follow a strict JSON contract covering intent, entities, signal types, owner, dependencies, approvals, blockers, next actions and confidence.

The deterministic local engine is the safety floor. It is intentionally explainable and broad enough to handle common construction vocabulary including revisions, scope changes, RFIs, submittals, approvals, holds, clashes, material/procurement exceptions and downstream dependencies.

The UI explicitly labels whether the result came from the **LLM API** or the **local fallback**.

## Product surfaces

- **Command Center** - live project readiness, critical issues, decision brief and pulse.
- **Coordination Signals** - evidence-backed signals with filters, confidence and ownership.
- **Action Queue** - release-critical P0/P1 work with owner, due state and confirmation.
- **Project Memory** - original messages plus system/human audit trail.
- **Stakeholders** - editable role, responsibility focus and status.
- **Impact Graph** - live relationship canvas generated from current coordination signals.
- **Capture Update** - API-first intelligence preview with novel example shortcuts.

## Professional stack

- **Frontend:** React 19.3, TypeScript, Vite 8.2, custom responsive design system, Lucide icons, PWA manifest
- **Backend:** FastAPI, Python 3.12, typed Pydantic contracts
- **Database:** PostgreSQL 16, SQLAlchemy 2.0, Alembic
- **AI:** OpenAI-compatible API first + explainable deterministic fallback
- **Delivery:** Docker multi-stage build, Docker Compose, Render Blueprint
- **Quality:** pytest API tests + generic-intelligence tests + deterministic evaluation harness

## Local run

### With Docker

```bash
docker compose up --build
```

Open `http://localhost:8080`.

### Configure API-first intelligence

Copy `.env.example` to `.env` and provide an OpenAI-compatible key. The default base URL is `https://api.openai.com/v1` and the model is configurable.

FastAPI OpenAPI docs: `http://localhost:8080/docs`.

## Public deployment

`render.yaml` provisions a Docker web service and PostgreSQL database. Add `LLM_API_KEY` as a secret in Render. After deployment:

1. Verify `/api/health` reports a connected database and `provider_configured: true`.
2. Open the public URL in a fresh browser.
3. Capture a novel message and verify the signal/action persists.
4. Use that public URL in the ArchScale submission form.

## Submission assets

- `DOCUMENTATION.md` - explicit problem, decisions, AI assistance and next steps
- `docs/architecture.md` - runtime and data architecture
- `docs/demo-script.md` - detailed 3-5 minute presentation sequence
- `ThreadPilot_Concept_Note.pdf` - concise concept note
- `SUBMISSION.md` - final submission checklist
