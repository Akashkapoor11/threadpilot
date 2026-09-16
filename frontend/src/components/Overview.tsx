import type { CSSProperties, ReactNode } from "react";
import { ArrowUpRight, CheckCircle2, CircleAlert, Clock3, FileText, Gauge, GitBranch, MessageSquareText, ShieldAlert, Sparkles, UsersRound } from "lucide-react";
import type { ProjectState, Signal } from "../types";
import { Badge, Card, SectionHeader } from "./ui";

const severityTone: Record<string, string> = { CRITICAL: "critical", HIGH: "high", MEDIUM: "medium", LOW: "neutral" };

export function Overview({ state, onSignal, onView }: { state: ProjectState; onSignal: (s: Signal) => void; onView: (v: "signals" | "actions" | "memory" | "stakeholders" | "impact") => void }) {
  const recent = [...state.signals].reverse().filter((s) => s.status !== "DISMISSED").slice(0, 4);
  const completed = state.actions.filter((a) => a.status === "DONE").length;
  return (
    <div className="page-stack">
      <section className="hero-row">
        <div>
          <div className="eyebrow">AS-01 · COORDINATION INTELLIGENCE</div>
          <h1>From project noise to coordinated action.</h1>
          <p className="hero-copy">ThreadPilot connects fragmented updates to the people, dependencies, approvals and actions that actually move a project forward.</p>
        </div>
        <div className="health-panel">
          <div className="health-ring" style={{ "--progress": `${state.project.readiness * 3.6}deg` } as CSSProperties}><div>{state.project.readiness}<small>%</small></div></div>
          <div><span>PROJECT READINESS</span><strong>{state.project.health}</strong><small>Risk exposure {state.project.risk}%</small></div>
        </div>
      </section>

      <div className="metric-grid">
        <Metric icon={<CircleAlert/>} label="Critical signals" value={String(state.metrics.critical)} detail="Need human review" onClick={() => onView("signals")} tone="critical" />
        <Metric icon={<Clock3/>} label="Open blockers" value={String(state.metrics.open_blockers)} detail="Work may be waiting" onClick={() => onView("signals")} tone="warning" />
        <Metric icon={<ShieldAlert/>} label="Approval gates" value={String(state.metrics.approval_gates)} detail="Require explicit decision" onClick={() => onView("actions")} tone="info" />
        <Metric icon={<UsersRound/>} label="Active stakeholders" value={String(state.people.filter((p) => p.status === "ACTIVE").length)} detail="Roles with ownership" onClick={() => onView("stakeholders")} tone="success" />
      </div>

      <div className="grid-2-1">
        <Card>
          <SectionHeader eyebrow="Decision brief" title="What needs attention now" description="A live summary derived from current project memory and unresolved coordination signals." action={<Badge tone={state.project.health === "AT RISK" ? "critical" : "success"}>{state.project.health}</Badge>} />
          <div className="brief-hero"><div className="brief-icon"><Sparkles size={19}/></div><div><strong>{state.brief.headline}</strong><p>{state.brief.recommendation}</p></div></div>
          <div className="brief-list">{state.brief.items.map((item) => <div className="brief-item" key={item}><CheckCircle2 size={17}/><span>{item}</span></div>)}</div>
        </Card>
        <Card>
          <SectionHeader eyebrow="Execution" title="Next actions" action={<button className="text-button" onClick={() => onView("actions")}>View all <ArrowUpRight size={15}/></button>} />
          <div className="action-preview">{state.actions.filter((a) => a.status !== "DONE").slice(0, 4).map((a) => <div className="mini-action" key={a.id}><Badge tone={a.priority === "P0" ? "critical" : "medium"}>{a.priority}</Badge><div><strong>{a.title}</strong><span>{a.owner} · {a.due}</span></div></div>)}</div>
          <div className="progress-foot"><div><span>{completed}/{state.actions.length} actions resolved</span><b>{Math.round((completed / Math.max(1, state.actions.length)) * 100)}%</b></div><div className="progress-bar"><span style={{ width: `${(completed / Math.max(1, state.actions.length)) * 100}%` }}/></div></div>
        </Card>
      </div>

      <div className="grid-2-1">
        <Card>
          <SectionHeader eyebrow="Live intelligence" title="Latest coordination signals" action={<button className="text-button" onClick={() => onView("signals")}>Open signal desk <ArrowUpRight size={15}/></button>} />
          <div className="signal-list">{recent.map((signal) => <button className="signal-row" key={signal.id} onClick={() => onSignal(signal)}><div className={`signal-marker ${severityTone[signal.severity]}`}><CircleAlert size={16}/></div><div className="signal-content"><div className="signal-row-top"><strong>{signal.title}</strong><Badge tone={severityTone[signal.severity]}>{signal.severity}</Badge></div><p>{signal.detail}</p><span>{signal.owner} · {signal.confidence}% confidence</span></div><ArrowUpRight size={16}/></button>)}</div>
        </Card>
        <Card>
          <SectionHeader eyebrow="Traceability" title="Project pulse" />
          <div className="pulse-grid">
            <Pulse icon={<MessageSquareText/>} label="Source updates" value={String(state.messages.length)} /><Pulse icon={<GitBranch/>} label="Impact nodes" value={String(state.graph.nodes.length)} /><Pulse icon={<FileText/>} label="Audit entries" value={String(state.audit.length)} /><Pulse icon={<Gauge/>} label="Channels" value={String(state.project.channels)} />
          </div>
          <div className="source-note"><ShieldAlert size={17}/><div><strong>Evidence coverage</strong><span>Every seeded signal links back to source messages. Captured signals retain their origin for review.</span></div><b>{state.metrics.source_coverage}</b></div>
        </Card>
      </div>
    </div>
  );
}

function Metric({ icon, label, value, detail, onClick, tone }: { icon: ReactNode; label: string; value: string; detail: string; onClick: () => void; tone: string }) {
  return <button className="metric-card" onClick={onClick}><div className={`metric-icon ${tone}`}>{icon}</div><div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div><ArrowUpRight size={16}/></button>;
}

function Pulse({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return <div className="pulse-item"><div>{icon}</div><span>{label}</span><strong>{value}</strong></div>;
}
