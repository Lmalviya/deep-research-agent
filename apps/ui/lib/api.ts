export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type CatalogEntry = {
  id: string;
  name: string;
  transport: string;
  endpoint: string;
  requires_auth: boolean;
  auth_hint: string | null;
  icon_url: string | null;
  description: string | null;
  user_config_id: string | null;
  is_active: boolean;
  has_token: boolean;
};

export type UserMcpConfig = {
  id: string;
  user_id: string;
  catalog_id: string | null;
  name: string;
  transport: string;
  endpoint: string;
  has_token: boolean;
  is_active: boolean;
  is_custom: boolean;
  created_at: string;
  updated_at: string;
};

export async function getCatalog(userId: string): Promise<CatalogEntry[]> {
  const res = await fetch(`${API_URL}/mcp/catalog?user_id=${userId}`);
  if (!res.ok) throw new Error("Failed to fetch catalog");
  return res.json();
}

export async function getUserConfigs(userId: string): Promise<UserMcpConfig[]> {
  const res = await fetch(`${API_URL}/mcp/configs?user_id=${userId}`);
  if (!res.ok) throw new Error("Failed to fetch configs");
  return res.json();
}

export async function createConfig(payload: {
  user_id: string;
  catalog_id?: string;
  name: string;
  transport: string;
  endpoint: string;
  auth_token?: string;
  is_custom: boolean;
}): Promise<UserMcpConfig> {
  const res = await fetch(`${API_URL}/mcp/configs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw err;
  }
  return res.json();
}

export async function updateConfig(
  configId: string,
  payload: {
    name?: string;
    endpoint?: string;
    auth_token?: string;
    is_active?: boolean;
  }
): Promise<UserMcpConfig> {
  const res = await fetch(`${API_URL}/mcp/configs/${configId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw err;
  }
  return res.json();
}

export async function deleteConfig(configId: string): Promise<void> {
  const res = await fetch(`${API_URL}/mcp/configs/${configId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const err = await res.json();
    throw err;
  }
}

export async function* streamChat(
  userId: string,
  query: string
): AsyncGenerator<{ type: string; content?: string; tools?: string[]; error?: string }> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, query }),
  });

  if (!res.ok) {
    const err = await res.json();
    yield { type: "error", content: err.detail || "Unknown error" };
    return;
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          yield JSON.parse(line.slice(6));
        } catch {
          // ignore malformed chunks
        }
      }
    }
  }
}
