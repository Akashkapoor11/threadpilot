/// <reference types="vite/client" />
import type { Intelligence, ProjectState } from "../types";

const API = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ?? "";

type JsonBody = Record<string, unknown>;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      // Keep the useful HTTP fallback.
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export const api = {
  project: () => request<ProjectState>("/api/project"),
  health: () => request<{ ok: boolean; database: string; engine: string; version: string; provider_configured: boolean }>("/api/health"),
  preview: (body: JsonBody) => request<Intelligence>("/api/intelligence/preview", { method: "POST", body: JSON.stringify(body) }),
  capture: (body: JsonBody) => request<{ message_id: string; intelligence: Intelligence; project: ProjectState }>("/api/messages", { method: "POST", body: JSON.stringify(body) }),
  impact: (id: string) => request<{ signal: ProjectState["signals"][number]; sources: ProjectState["messages"]; stages: { step: number; label: string; value: string; state: string }[] }>(`/api/impact/${id}`),
  signalDecision: (id: string, decision: "confirm" | "dismiss") => request<ProjectState>(`/api/signals/${id}/decision/${decision}`, { method: "POST" }),
  confirmAction: (id: string) => request<ProjectState>(`/api/actions/${id}/confirm`, { method: "POST" }),
  routeSignal: (id: string, body: JsonBody) => request<ProjectState>(`/api/signals/${id}/route`, { method: "POST", body: JSON.stringify(body) }),
  updateStakeholder: (id: string, body: JsonBody) => request<ProjectState>(`/api/stakeholders/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  refresh: () => request<ProjectState>("/api/intelligence/refresh", { method: "POST" }),
  reset: () => request<ProjectState>("/api/demo/reset", { method: "POST" }),
};
