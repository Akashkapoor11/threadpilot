import { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { AlertTriangle, CheckCircle2, LoaderCircle, SearchX, ShieldCheck } from "lucide-react";
import { api } from "./lib/api";
import type { Intelligence, ProjectState, Signal } from "./types";
import { AppShell, type View } from "./components/Layout";
import { Overview } from "./components/Overview";
import { Signals, SignalDrawer } from "./components/Signals";
import { Actions } from "./components/Actions";
import { Memory } from "./components/Memory";
import { Stakeholders } from "./components/Stakeholders";
import { ImpactGraph } from "./components/ImpactGraph";
import { CaptureModal } from "./components/CaptureModal";
import "./styles.css";

function App() {
  const [state, setState] = useState<ProjectState | null>(null);
  const [view, setView] = useState<View>("overview");
  const [search, setSearch] = useState("");
  const [selectedSignal, setSelectedSignal] = useState<Signal | null>(null);
  const [impact, setImpact] = useState<any>(null);
  const [captureOpen, setCaptureOpen] = useState(false);
  const [preview, setPreview] = useState<Intelligence | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [providerReady, setProviderReady] = useState(false);
  const [error, setError] = useState("");

  const loadState = useCallback(async () => {
    try {
      const data = await api.project();
      setState(data);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to connect to ThreadPilot backend.");
    }
  }, []);

  useEffect(() => { void loadState(); void api.health().then((health) => setProviderReady(Boolean(health.provider_configured))).catch(() => undefined); }, [loadState]);
  useEffect(() => { const timer = window.setInterval(() => { void loadState(); }, 30000); return () => window.clearInterval(timer); }, [loadState]);
  useEffect(() => { if (!selectedSignal) { setImpact(null); return; } void api.impact(selectedSignal.id).then(setImpact).catch(() => setImpact(null)); }, [selectedSignal]);
  useEffect(() => { if (!notice) return; const t = window.setTimeout(() => setNotice(""), 4500); return () => window.clearTimeout(t); }, [notice]);

  const filteredState = useMemo(() => {
    if (!state || !search.trim()) return state;
    const q = search.toLowerCase();
    const signalIds = new Set(state.signals.filter((s) => `${s.title} ${s.detail} ${s.owner} ${s.type}`.toLowerCase().includes(q)).map((s) => s.id));
    const messageIds = new Set(state.messages.filter((m) => `${m.sender} ${m.channel} ${m.text} ${m.tag}`.toLowerCase().includes(q)).map((m) => m.id));
    return { ...state, signals: state.signals.filter((s) => signalIds.has(s.id) || s.source_ids.split(",").some((id) => messageIds.has(id))), actions: state.actions.filter((a) => `${a.title} ${a.owner} ${a.reason}`.toLowerCase().includes(q)), messages: state.messages.filter((m) => messageIds.has(m.id) || m.text.toLowerCase().includes(q)) };
  }, [state, search]);

  if (error && !state) return <ErrorScreen message={error} onRetry={loadState} />;
  if (!filteredState) return <LoadingScreen />;

  async function mutate(operation: () => Promise<ProjectState>) { setBusy(true); try { const next = await operation(); setState(next); } catch (err) { setNotice(err instanceof Error ? err.message : "Action failed."); } finally { setBusy(false); } }
  async function handlePreview(text: string, channel: string, sender: string) { setBusy(true); try { setPreview(await api.preview({ text, channel, sender })); } catch (err) { setNotice(err instanceof Error ? err.message : "Preview failed."); } finally { setBusy(false); } }
  async function handleSave(text: string, channel: string, sender: string) { setBusy(true); try { const result = await api.capture({ text, channel, sender }); setState(result.project); setPreview(result.intelligence); setNotice(`${result.intelligence.signals.length} coordination signal${result.intelligence.signals.length === 1 ? "" : "s"} created. Review the new action queue.`); setCaptureOpen(false); setView("signals"); } catch (err) { setNotice(err instanceof Error ? err.message : "Capture failed."); } finally { setBusy(false); } }
  async function handleSignal(signal: Signal) { setSelectedSignal(signal); }
  async function handleDecision(id: string, decision: "confirm" | "dismiss") { await mutate(() => api.signalDecision(id, decision)); setNotice(`Signal ${decision === "confirm" ? "confirmed" : "dismissed"}.`); setSelectedSignal(null); }
  async function handleRoute(id: string, recipient: string, channel: string) { await mutate(() => api.routeSignal(id, { recipient, channel })); }

  return <>
    <AppShell state={filteredState} view={view} setView={setView} onRefresh={() => mutate(api.refresh)} onCapture={() => { setPreview(null); setCaptureOpen(true); }} search={search} setSearch={setSearch} notice={notice} onDismissNotice={() => setNotice("")} providerReady={providerReady}>
      {view === "overview" && <Overview state={filteredState} onSignal={handleSignal} onView={setView} />}
      {view === "signals" && <Signals state={filteredState} onSignal={handleSignal} />}
      {view === "actions" && <Actions actions={filteredState.actions} onConfirm={(id) => mutate(() => api.confirmAction(id)).then(() => setNotice("Action marked complete."))} />}
      {view === "memory" && <Memory state={filteredState} />}
      {view === "stakeholders" && <Stakeholders people={filteredState.people} onSave={(id, body) => mutate(() => api.updateStakeholder(id, body))} />}
      {view === "impact" && <ImpactGraph state={filteredState} onSignal={handleSignal} />}
      {filteredState.signals.length === 0 && search && <div className="search-empty"><SearchX size={22}/><strong>No project evidence matches “{search}”</strong><span>Try a stakeholder, revision, blocker, channel or action.</span></div>}
    </AppShell>
    {selectedSignal && <SignalDrawer signal={selectedSignal} state={filteredState} impact={impact} onClose={() => setSelectedSignal(null)} onDecision={handleDecision} onRoute={handleRoute} onNotice={setNotice} />}
    {captureOpen && <CaptureModal preview={preview} busy={busy} onPreview={handlePreview} onSave={handleSave} onClose={() => setCaptureOpen(false)} />}
  </>;
}

function LoadingScreen() { return <div className="center-screen"><div className="loading-brand"><div className="brand-mark"><span>TP</span></div><div><strong>ThreadPilot</strong><span>Loading coordination intelligence…</span></div></div><LoaderCircle className="spin" size={26}/></div>; }
function ErrorScreen({ message, onRetry }: { message: string; onRetry: () => void }) { return <div className="center-screen"><div className="error-card"><div className="error-icon"><AlertTriangle/></div><h1>ThreadPilot is not connected</h1><p>{message}</p><button className="primary-button" onClick={onRetry}><ShieldCheck size={16}/> Retry connection</button><div className="hint"><CheckCircle2 size={14}/> Start the API with Docker Compose or your deployed FastAPI service.</div></div></div>; }

createRoot(document.getElementById("root")!).render(<App />);
