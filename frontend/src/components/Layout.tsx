import { Bell, BookOpenCheck, Boxes, BriefcaseBusiness, ChevronRight, FileClock, Gauge, GitBranch, LayoutDashboard, LogOut, Plus, RefreshCw, Search, Settings2, ShieldCheck, UsersRound, X } from "lucide-react";
import type { ReactNode } from "react";
import type { ProjectState } from "../types";

export type View = "overview" | "signals" | "actions" | "memory" | "stakeholders" | "impact";

const nav = [
  { id: "overview", label: "Command Center", icon: LayoutDashboard },
  { id: "signals", label: "Coordination Signals", icon: Boxes },
  { id: "actions", label: "Action Queue", icon: BriefcaseBusiness },
  { id: "memory", label: "Project Memory", icon: FileClock },
  { id: "stakeholders", label: "Stakeholders", icon: UsersRound },
  { id: "impact", label: "Impact Graph", icon: GitBranch },
] as const;

export function AppShell({ state, view, setView, onRefresh, onCapture, children, search, setSearch, notice, onDismissNotice, providerReady }: {
  state: ProjectState;
  view: View;
  setView: (v: View) => void;
  onRefresh: () => void;
  onCapture: () => void;
  children: ReactNode;
  search: string;
  setSearch: (v: string) => void;
  notice?: string;
  onDismissNotice: () => void;
  providerReady: boolean;
}) {
  const openActions = state.actions.filter((a) => a.status !== "DONE").length;
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark"><span>TP</span></div>
          <div><div className="brand-name">ThreadPilot</div><div className="brand-sub">Coordination Intelligence</div></div>
        </div>
        <div className="project-card">
          <div className="project-icon"><Gauge size={17}/></div>
          <div className="project-info"><span>ACTIVE PROJECT</span><strong>{state.project.name}</strong><small>{state.project.code} · {state.project.channels} channels</small></div>
          <ChevronRight size={16}/>
        </div>
        <nav className="nav-list" aria-label="Primary navigation">
          <div className="nav-caption">WORKSPACE</div>
          {nav.map(({ id, label, icon: Icon }) => (
            <button key={id} className={`nav-item ${view === id ? "active" : ""}`} onClick={() => setView(id)}>
              <Icon size={18}/><span>{label}</span>
              {id === "actions" && <em>{openActions}</em>}
            </button>
          ))}
        </nav>
        <div className="sidebar-spacer" />
        <div className="provider-card">
          <div className={`provider-dot ${providerReady ? "live" : "fallback"}`} />
          <div><strong>{providerReady ? "AI provider configured" : "Local safety engine"}</strong><span>{providerReady ? "API-first extraction enabled" : "Provider not configured"}</span></div>
        </div>
        <div className="profile-mini"><div className="avatar">AK</div><div><strong>Project workspace</strong><span>Human review enabled</span></div><Settings2 size={16}/></div>
      </aside>

      <main className="main-shell">
        <header className="topbar">
          <div className="mobile-brand"><div className="brand-mark small"><span>TP</span></div><strong>ThreadPilot</strong></div>
          <div className="search-shell"><Search size={17}/><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search project memory, signals, owners…" /></div>
          <div className="top-actions">
            <button className="icon-button" aria-label="Refresh intelligence" title="Refresh intelligence" onClick={onRefresh}><RefreshCw size={17}/></button>
            <button className="icon-button" aria-label="Notifications" title="Notifications"><Bell size={17}/>{state.alerts.length > 0 && <i />}</button>
            <button className="primary-button compact" onClick={onCapture}><Plus size={17}/> Capture update</button>
          </div>
        </header>
        {notice && <div className="notice"><ShieldCheck size={17}/><span>{notice}</span><button aria-label="Dismiss" onClick={onDismissNotice}><X size={15}/></button></div>}
        <div className="content-wrap">{children}</div>
      </main>
    </div>
  );
}
