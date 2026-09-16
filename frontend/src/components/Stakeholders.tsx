import { Pencil, ShieldCheck, UserRound } from "lucide-react";
import { useState } from "react";
import type { Person } from "../types";
import { Badge, Card, Modal, SectionHeader } from "./ui";

export function Stakeholders({ people, onSave }: { people: Person[]; onSave: (id: string, body: { role: string; focus: string; status: string }) => Promise<void> }) {
  const [editing, setEditing] = useState<Person | null>(null);
  return <div className="page-stack"><div className="page-intro"><div><div className="eyebrow">STAKEHOLDER GRAPH</div><h1>Make ownership explicit.</h1><p>Roles, responsibilities and availability stay visible so every coordination signal has a clear destination.</p></div></div><Card><SectionHeader eyebrow="Project team" title="Stakeholders & responsibilities" description="Edit the role and responsibility focus used by the coordination layer." /><div className="people-grid">{people.map((person) => <article className="person-card" key={person.id}><div className="person-head"><div className="avatar large">{person.initials}</div><div><strong>{person.name}</strong><span>{person.role}</span></div><Badge tone={person.status === "ACTIVE" ? "success" : "neutral"}>{person.status}</Badge></div><div className="person-focus"><small>RESPONSIBILITY FOCUS</small><p>{person.focus}</p></div><div className="person-footer"><span><ShieldCheck size={13}/> Routed ownership</span><button className="text-button" onClick={() => setEditing(person)}><Pencil size={14}/> Manage</button></div></article>)}</div></Card>{editing && <StakeholderEditor person={editing} onClose={() => setEditing(null)} onSave={async (body) => { await onSave(editing.id, body); setEditing(null); }} />}</div>;
}

function StakeholderEditor({ person, onClose, onSave }: { person: Person; onClose: () => void; onSave: (body: { role: string; focus: string; status: string }) => Promise<void> }) {
  const [role, setRole] = useState(person.role);
  const [focus, setFocus] = useState(person.focus);
  const [status, setStatus] = useState(person.status);
  const [saving, setSaving] = useState(false);
  return <Modal onClose={onClose}><div className="modal-title"><div className="icon-tile"><UserRound/></div><div><div className="eyebrow">STAKEHOLDER MANAGEMENT</div><h2>Manage {person.name}</h2><p>Keep ownership accurate so coordination routing remains useful.</p></div></div><div className="form-grid"><label>Role<input value={role} onChange={(e) => setRole(e.target.value)} /></label><label>Status<select value={status} onChange={(e) => setStatus(e.target.value)}><option>ACTIVE</option><option>INACTIVE</option></select></label></div><label>Responsibility focus<textarea value={focus} onChange={(e) => setFocus(e.target.value)} /></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>Cancel</button><button className="primary-button" disabled={saving} onClick={async () => { setSaving(true); try { await onSave({ role, focus, status }); } finally { setSaving(false); } }}>Save changes</button></div></Modal>;
}
