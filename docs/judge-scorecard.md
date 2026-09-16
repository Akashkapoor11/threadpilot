# Judge scorecard alignment

This is a factual demo map, not a claim about judge scoring.

## Problem understanding

AS-01 describes the coordination black hole: information is spread across people and channels, while the relationship between a change and the people responsible for acting on it remains unclear.

ThreadPilot answers that with a single visible consequence chain:

`change -> affected people -> dependency -> approval -> blocker -> action -> memory`

## User-product sense

The project manager / coordinator is the control-plane user. The system keeps discipline-specific ownership visible for architect, MEP, interior, contractor, client and supplier roles so the coordinator can route decisions instead of reconstructing the project manually.

## Technical execution

- React + TypeScript frontend with componentized work surfaces.
- FastAPI + Pydantic typed API layer.
- PostgreSQL + SQLAlchemy + Alembic persistence.
- API-first LLM extraction with transparent provider/fallback status.
- Generic deterministic extraction and consistency checks for revisions, RFIs, submittals, holds, clashes, supply exceptions and actions.
- Live signal/action creation from newly captured messages.
- Graph generated from current coordination signals instead of a fixed SVG scenario only.
- Docker and Render deployment assets.
- Automated backend tests and evaluation harness.

## Strongest proof points during a live demo

1. Open a critical signal and inspect the exact source messages behind it.
2. Show the impact chain and owner/action relationship.
3. Show the live graph, then capture a new unseen project note and watch new nodes appear.
4. Confirm a P0 action and show the audit entry.
5. Route an alert and show its persistent routing state.
6. Edit a stakeholder responsibility and show the updated ownership.

## Hard question: “Is the impact graph hardcoded?”

Answer:

“The Riverside Residence messages are seeded so the official AS-01 scenario is reproducible. The deeper graph is generated from live coordination signals: each signal contributes an evidence node, owner, downstream dependency and/or approval gate and next action. A new capture adds its inferred signal and action nodes to the graph. The next production step is a persisted editable project knowledge graph with richer relationship extraction.”

## Hard question: “Is the AI hardcoded?”

Answer:

“No. The runtime is provider-first. With an LLM API key and base URL configured, captured text is sent to the provider first and parsed into a strict coordination schema. The local engine is the reliability fallback. The UI labels whether a result came from the primary provider or fallback so the behavior is transparent.”

## Hard question: “What happens when the LLM fails?”

Answer:

“The request falls back to the deterministic evidence engine. We prefer a slightly less rich but explainable answer over a broken coordination workflow.”

## Hard question: “Does ThreadPilot autonomously change project state?”

Answer:

“No. Detection, recommendation and execution are separate. Signals require confirmation or dismissal, actions require explicit confirmation, and those decisions are written to the audit trail.”

## Live demo quality checklist

- Public deployment URL opens from a fresh browser.
- Database reports connected at `/api/health`.
- LLM API secret is configured for the primary path.
- One seeded scenario demonstrates the official AS-01 case.
- One novel scenario demonstrates generalization.
- Evidence, consequence, action and memory are shown in one uninterrupted flow.
