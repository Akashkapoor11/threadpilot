# ArchScale Guild - AS-01 Submission

## Product
**ThreadPilot - Project Impact Intelligence**

## One-line pitch
**ThreadPilot turns fragmented project updates into an evidence-backed consequence chain: change -> affected people -> dependencies -> approval -> blocker -> action -> alert -> memory.**

## AS-01 coverage

All eight target capabilities are represented in the prototype:

1. Stakeholder & Role Management
2. Project Activity & Change Tracking
3. Impact Identification
4. Dependency Management
5. Action Tracking
6. Approval Management
7. Coordination Alerts
8. Project Memory

## Primary proof

- Multi-stakeholder Riverside Residence project scenario.
- Persistent project activity across multiple channels.
- API-first intelligence extraction when configured.
- Explainable local fallback when the provider is unavailable.
- Generic revision/material consistency checks.
- Live unseen-message capture and signal/action generation.
- Evidence-linked signal drawer.
- Live consequence graph generated from coordination signals.
- P0/P1 actions with human confirmation.
- Alert routing with audit history.
- Stakeholder role/focus/status management.
- PostgreSQL persistence.

## Submission requirements

**GitHub:** add the final public repository URL.

**Deployed URL:** add the final public URL. ArchScale states deployment is strongly preferred and weighted positively.

**Walkthrough:** submit a 3-5 minute recording of the prototype working.

**Documentation:** include `DOCUMENTATION.md`, architecture/demo docs and the concept note.

## Technical positioning

The LLM/API is the primary intelligence path when credentials are configured. A deterministic local evidence engine is the reliability fallback. The official AS-01 seed is demo data used to reproduce the judging scenario; it is not the only intelligence path.

## Before submitting

- [ ] Public GitHub repository works from a clean clone.
- [ ] Public deployment opens without localhost dependencies.
- [ ] `/api/health` shows database connected.
- [ ] LLM provider secret is configured for API-first demo behavior.
- [ ] Capture a novel message live during the recording.
- [ ] Show signal evidence and the impact graph.
- [ ] Show action confirmation and audit memory.
- [ ] Video is between 3 and 5 minutes.
- [ ] Documentation explains problem, decisions, AI help and next steps.
