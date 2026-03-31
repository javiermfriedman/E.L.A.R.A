const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ─── Token helpers ───────────────────────────────────────────
export function getToken() {
  return localStorage.getItem("elara_token");
}

export function setToken(token) {
  localStorage.setItem("elara_token", token);
}

export function removeToken() {
  localStorage.removeItem("elara_token");
}

export function isAuthenticated() {
  return !!getToken();
}

// ─── Base fetch wrapper ───────────────────────────────────────
async function request(path, options = {}) {
  const token = getToken();

  const headers = {
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || "Request failed");
  }

  // 204 No Content
  if (res.status === 204) return null;

  return res.json();
}

// ─── Auth ─────────────────────────────────────────────────────

// Register — POST /auth/  (JSON body)
export async function register(username, password) {
  return request("/auth/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
}

// Login — POST /auth/token  (form data — OAuth2 requirement)
export async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch(`${BASE_URL}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || "Login failed");
  }

  const data = await res.json();
  setToken(data.access_token);
  return data;
}

// ─── Future endpoints (ready to fill in) ─────────────────────
// Agents

// Calls
export async function getRecordings() {
  return request("/recordings/");
}
// Contacts
export async function getContacts() {
  return request("/contacts/");
}

export async function createContact(formData) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}/contacts/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || "Failed to create contact");
  }

  return res.json();
}

export async function getAgents() {
  return request("/agents/");
}

export async function createAgent(formData) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}/agents/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      // DO NOT set Content-Type — browser sets it with boundary for multipart
    },
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || "Failed to create agent");
  }

  return res.json();
}
// Calls
export async function initiateCall(agent_id, target_name, to_number) {
  return request("/dialout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ agent_id, target_name, to_number }),
  });
}

export async function getCallStatus(call_sid) {
  return request(`/call/status?call_sid=${call_sid}`);
}

export async function cancelCall(call_sid) {
  return request(`/call/cancel?call_sid=${call_sid}`, {
    method: "POST",
  });
}

export async function getRecordingAudio(recordingId) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}/recordings/${recordingId}/audio`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch audio");
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export async function deleteContacts() {
  return request("/contacts/", { method: "DELETE" });
}

export async function deleteRecordings() {
  return request("/recordings/", { method: "DELETE" });
}

export async function deleteAgents() {
  return request("/agents/", { method: "DELETE" });
}

export async function deleteRecording(recordingId) {
  return request(`/recordings/${recordingId}`, { method: "DELETE" });
}

export async function deleteAgent(agentId) {
  return request(`/agents/${agentId}`, { method: "DELETE" });
}