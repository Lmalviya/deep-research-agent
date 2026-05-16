"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { CatalogEntry, UserMcpConfig, createConfig, updateConfig } from "@/lib/api";

type Mode = "add-custom" | "auth-required" | "edit";

interface McpModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  userId: string;

  // For "auth-required" mode: the catalog entry that needs a token
  catalogEntry?: CatalogEntry;

  // For "edit" mode: the config being edited
  editTarget?: UserMcpConfig;
}

export function McpModal({
  open,
  onClose,
  onSuccess,
  userId,
  catalogEntry,
  editTarget,
}: McpModalProps) {
  const mode: Mode = editTarget
    ? "edit"
    : catalogEntry
    ? "auth-required"
    : "add-custom";

  const [name, setName] = useState(editTarget?.name ?? catalogEntry?.name ?? "");
  const [transport, setTransport] = useState(
    editTarget?.transport ?? catalogEntry?.transport ?? "SSE"
  );
  const [endpoint, setEndpoint] = useState(
    editTarget?.endpoint ?? catalogEntry?.endpoint ?? ""
  );
  const [authToken, setAuthToken] = useState("");
  const [updateToken, setUpdateToken] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const title =
    mode === "edit"
      ? `Edit — ${editTarget?.name}`
      : mode === "auth-required"
      ? `Connect to ${catalogEntry?.name}`
      : "Add Custom MCP Server";

  const description =
    mode === "auth-required"
      ? catalogEntry?.auth_hint ?? "This server requires an authentication token."
      : mode === "edit"
      ? "Update the server details below."
      : "Enter the details for your custom MCP server.";

  async function handleSubmit() {
    setLoading(true);
    setError(null);

    try {
      if (mode === "edit" && editTarget) {
        await updateConfig(editTarget.id, {
          name: name || undefined,
          endpoint: endpoint || undefined,
          auth_token: updateToken && authToken ? authToken : undefined,
        });
      } else if (mode === "auth-required" && catalogEntry) {
        await createConfig({
          user_id: userId,
          catalog_id: catalogEntry.id,
          name: catalogEntry.name,
          transport: catalogEntry.transport,
          endpoint: catalogEntry.endpoint,
          auth_token: authToken || undefined,
          is_custom: false,
        });
      } else {
        // add-custom
        await createConfig({
          user_id: userId,
          name,
          transport,
          endpoint,
          auth_token: authToken || undefined,
          is_custom: true,
        });
      }
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const e = err as { detail?: string | { message?: string } };
      if (typeof e?.detail === "string") setError(e.detail);
      else if (typeof e?.detail === "object") setError(e.detail?.message ?? "An error occurred");
      else setError("An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="bg-[#1a1a2e] border-white/10 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold">{title}</DialogTitle>
          <DialogDescription className="text-white/50 text-sm">{description}</DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* Name — shown for custom and edit */}
          {(mode === "add-custom" || mode === "edit") && (
            <Field label="Name">
              <input
                className={INPUT}
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="My MCP Server"
              />
            </Field>
          )}

          {/* Transport — only for custom */}
          {mode === "add-custom" && (
            <Field label="Transport">
              <select
                className={INPUT}
                value={transport}
                onChange={(e) => setTransport(e.target.value)}
              >
                <option value="SSE">SSE (Remote)</option>
                <option value="Stdio">Stdio (Local)</option>
              </select>
            </Field>
          )}

          {/* Endpoint — shown for custom and edit (not for auth-required which is pre-filled) */}
          {(mode === "add-custom" || mode === "edit") && (
            <Field label="Endpoint URL">
              <input
                className={INPUT}
                value={endpoint}
                onChange={(e) => setEndpoint(e.target.value)}
                placeholder="https://your-mcp-server.com/mcp"
              />
            </Field>
          )}

          {/* Auth token — always shown for auth-required, optional for custom/edit */}
          {mode === "auth-required" && (
            <Field label="Auth Token">
              <input
                className={INPUT}
                type="password"
                value={authToken}
                onChange={(e) => setAuthToken(e.target.value)}
                placeholder={catalogEntry?.auth_hint ?? "Paste your token here"}
              />
            </Field>
          )}

          {mode === "add-custom" && (
            <Field label="Auth Token (optional)">
              <input
                className={INPUT}
                type="password"
                value={authToken}
                onChange={(e) => setAuthToken(e.target.value)}
                placeholder="Leave blank if not required"
              />
            </Field>
          )}

          {mode === "edit" && (
            <Field label="">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={updateToken}
                  onChange={(e) => setUpdateToken(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-white/70">Update auth token</span>
              </label>
              {updateToken && (
                <input
                  className={`${INPUT} mt-2`}
                  type="password"
                  value={authToken}
                  onChange={(e) => setAuthToken(e.target.value)}
                  placeholder="Enter new token"
                />
              )}
            </Field>
          )}

          {error && (
            <p className="text-red-400 text-sm bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="ghost"
            onClick={onClose}
            className="text-white/50 hover:text-white hover:bg-white/5"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={loading}
            className="bg-violet-600 hover:bg-violet-500 text-white"
          >
            {loading ? "Saving..." : mode === "edit" ? "Save Changes" : "Connect"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      {label && (
        <label className="block text-xs font-medium text-white/60 mb-1.5">{label}</label>
      )}
      {children}
    </div>
  );
}

const INPUT =
  "w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-white/30 focus:outline-none focus:ring-1 focus:ring-violet-500 focus:border-violet-500 transition";
