# ThreadPilot - ArchScale Guild AS-01

## 1. The problem

AS-01 describes a coordination black hole: project information exists across people and channels, but the relationship between a change and the people responsible for acting on it is unclear. A single revision, site issue, material exception or approval decision can cascade into multiple disciplines and downstream work.

ThreadPilot focuses on one intervention: convert unstructured project updates into an evidence-backed coordination state that makes the consequence chain visible:

`Change -> Impact -> Dependency -> Approval -> Blocker -> Action -> Alert -> Memory`

The product is designed for the project manager / coordinator as the control-plane user, while preserving explicit ownership for architect, consultant, designer, contractor, client and supplier roles.

## 2. Decisions and why

### API-first intelligence

The primary intelligence path uses an OpenAI-compatible Chat Completions API with a strict structured JSON contract. This is the intended production path because natural-language project notes vary widely across projects and disciplines.

### Explainable fallback

The local evidence engine is the secondary path. It uses broad construction vocabulary, revision/material consistency checks, entity extraction and deterministic signal rules. It keeps the prototype usable when the external provider is unavailable and gives judges a reproducible fallback.

### Evidence before automation

Every signal retains source-message IDs, confidence and a human decision state. Signals can be confirmed or dismissed, and actions require explicit confirmation. This avoids presenting a hackathon prototype as an autonomous construction agent that silently changes project state.

### PostgreSQL instead of a file database

Coordination memory is project state. PostgreSQL gives durable multi-user persistence, typed relations through SQLAlchemy, migrations through Alembic and a direct deployment path for managed hosting.

### React + TypeScript instead of a static page

The product has multiple connected work surfaces - command center, signal desk, action queue, project memory, stakeholder management and impact graph. React provides maintainable component boundaries and predictable state updates while TypeScript makes the API contract visible in the frontend.

### Dynamic graph, seeded demo data

The Riverside Residence seed exists so the official AS-01 scenario is reproducible during judging. The graph itself is generated from live signals, owners, actions and dependency/approval metadata, and newly captured signals are added to it. This separates scenario data from the intelligence pipeline.

### Human review before consequential state changes

Detection and recommendation are not the same as execution. The product intentionally stops at a reviewable decision point and writes confirmation/dismissal to the audit trail.

## 3. What AI helped with

AI-assisted development was used for iteration, code review, UX exploration, debugging, test design, documentation refinement and architecture comparison. The submitted implementation was manually inspected and the final system behavior is intentionally explainable.

The runtime AI path is explicit: when `LLM_API_KEY` and `LLM_BASE_URL` are present, ThreadPilot sends the captured project update to the configured provider first. If the provider is unavailable, parsing fails, or the response is invalid, the deterministic local engine takes over. The application labels which engine produced the result so the demo remains transparent.

## 4. What we would build next

1. Persist a first-class project knowledge graph so dependencies are editable, versioned and reusable across projects instead of being reconstructed from signals.
2. Add real WhatsApp Business / email adapters so coordination alerts can move from queued in-app events to actual delivery.
3. Add project authentication, role-based access control and tenant isolation for production deployments.
4. Add document/drawing ingestion so revisions, RFIs, submittals and PDFs become first-class evidence rather than only message text.
5. Add richer evaluation across unseen construction scenarios and human-reviewed benchmark sets.

## AS-01 coverage

| Requirement | ThreadPilot implementation |
|---|---|
| Stakeholder & Role Management | Live stakeholder role/focus/status management |
| Activity & Change Tracking | Persistent multi-channel project memory |
| Impact Identification | Evidence-linked signals + impact chain |
| Dependency Management | Live graph built from signals and downstream consequence metadata |
| Action Tracking | P0/P1 actions with owners and confirmation |
| Approval Management | Approval signals and explicit decision gates |
| Coordination Alerts | Alert routing with recipient/channel and audit trail |
| Project Memory | PostgreSQL source history + audit trail |

## Submission assets

- GitHub repository: add the final public repository URL before submission.
- Deployed URL: add the live public URL before submission. ArchScale states deployment is strongly preferred and weighted positively.
- Walkthrough: 3-5 minute working demonstration.
- Documentation: this file + architecture/demo docs + concept note.
