# ThreadPilot architecture

## Runtime flow

`unstructured source -> capture API -> provider LLM -> structured coordination result -> PostgreSQL -> React UI -> human decision -> audit`

Fallback:

`provider unavailable / invalid -> local evidence engine -> structured coordination result -> PostgreSQL`

The AS-01 seed scenario is data used to make judging reproducible. It is not the only inference path.

## Frontend

React + TypeScript + Vite. The interface is split into maintainable modules:

- `Layout.tsx` - navigation, project shell, search and global actions
- `Overview.tsx` - command center and decision brief
- `Signals.tsx` - signal desk and evidence drawer
- `Actions.tsx` - accountable execution queue
- `Memory.tsx` - source history and audit trail
- `Stakeholders.tsx` - role/focus/status management
- `ImpactGraph.tsx` - graph visualization
- `CaptureModal.tsx` - live intelligence intake
- `ui.tsx` - shared card, badge, modal and section primitives

## Backend

FastAPI on Python 3.12 with Pydantic request/response models. The API provides project state, intelligence preview, message capture, signal decisions, action confirmation, coordination alert routing, stakeholder management, refresh, reset and health.

## Persistence

PostgreSQL 16 via SQLAlchemy 2. Alembic migrations are included for deployment workflows.

Tables:

- `project_meta` - project identity
- `stakeholders` - role, responsibility focus and status
- `messages` - original evidence
- `signals` - extracted coordination intelligence
- `actions` - owner, priority, due state and review status
- `alerts` - coordination routing history
- `audit` - human/system decisions and important events

## Intelligence contract

The provider prompt returns a strict object containing:

- intent and summary
- entities
- signal type/severity/title/reason
- owner hint
- dependencies
- approvals
- blockers
- next actions
- confidence

The local engine implements the same semantic result shape. Its detectors cover revisions, scope changes, RFIs, submittals, approvals, sign-off, blockers, holds, clashes, downstream dependencies, material/supply exceptions, procurement and explicit actions.

## Generic consistency checks

The consistency layer scans current project memory for multiple revisions of the same drawing/document and for material availability/substitution exceptions. These checks are not tied to specific revision numbers or material shade IDs.

## Graph generation

The impact graph is derived from live signals. Each signal creates an evidence node, owner node and next-action node. CHANGE/IMPACT signals can create dependency nodes; APPROVAL signals create a gate. This graph can grow as new evidence is captured.

## Responsible product behavior

Detection -> recommendation -> human review -> state change.

The system never treats an inferred signal as an irreversible project action. Confirmed actions are explicitly recorded in the audit trail. Alert delivery is adapter-ready: in-app routing is implemented; email/WhatsApp choices are persisted as queued integration events for the prototype.
