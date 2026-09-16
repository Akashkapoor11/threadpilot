export type Signal = {
  id: string;
  type: string;
  severity: string;
  title: string;
  detail: string;
  source_ids: string;
  owner: string;
  confidence: number;
  status: string;
  impact: string;
  why: string;
  action: string;
  created_at: string;
};

export type Message = {
  id: string;
  channel: string;
  sender: string;
  time_label: string;
  text: string;
  tag: string;
  created_at?: string;
};

export type ActionItem = {
  id: string;
  priority: string;
  title: string;
  owner: string;
  due: string;
  status: string;
  reason: string;
  source_ids: string;
};

export type Person = {
  id: string;
  name: string;
  role: string;
  focus: string;
  initials: string;
  status: string;
};

export type Alert = {
  id: string;
  signal_id: string;
  recipient: string;
  channel: string;
  status: string;
  created_at: string;
};

export type AuditEntry = {
  id: string;
  event: string;
  entity: string;
  entity_id: string;
  detail: string;
  ts: string;
};

export type IntelligenceSignal = {
  type: string;
  severity: string;
  title: string;
  reason: string;
};

export type Intelligence = {
  engine: string;
  intent: string;
  summary: string;
  entities: string[];
  signals: IntelligenceSignal[];
  confidence: number;
  owner_hint: string;
  dependencies: string[];
  approvals: string[];
  blockers: string[];
  next_actions: string[];
  provider_used: boolean;
};

export type GraphNode = { id: string; label: string; kind: string };
export type Graph = { nodes: GraphNode[]; edges: string[][] };

export type ProjectState = {
  project: {
    name: string;
    code: string;
    health: string;
    readiness: number;
    risk: number;
    channels: number;
    last_ingested: string;
    demo_mode: boolean;
  };
  people: Person[];
  messages: Message[];
  signals: Signal[];
  actions: ActionItem[];
  alerts: Alert[];
  audit: AuditEntry[];
  conflicts: { id: string; kind: string; severity: string; title: string; detail: string; source_ids: string; recommendation: string }[];
  graph: Graph;
  metrics: Record<string, string | number>;
  brief: { headline: string; items: string[]; recommendation: string };
};
