"use client";

import { useState } from "react";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Pencil, Trash2, Plug, AlertCircle } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { CatalogEntry, UserMcpConfig, updateConfig, deleteConfig } from "@/lib/api";

interface McpCardProps {
  item: CatalogEntry | UserMcpConfig;
  type: "catalog" | "custom";
  onEdit: () => void;
  onDeleted: () => void;
  onToggled: () => void;
  onNeedsToken: () => void;
}

export function McpCard({
  item,
  type,
  onEdit,
  onDeleted,
  onToggled,
  onNeedsToken,
}: McpCardProps) {
  const [toggling, setToggling] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const isCatalog = type === "catalog";
  const entry = item as CatalogEntry;
  const config = item as UserMcpConfig;

  const isActive = isCatalog ? entry.is_active : config.is_active;
  const hasToken = isCatalog ? entry.has_token : config.has_token;
  const requiresAuth = isCatalog ? entry.requires_auth : false;
  const configId = isCatalog ? entry.user_config_id : config.id;
  const name = item.name;

  async function handleToggle(checked: boolean) {
    // If activating a catalog entry that needs auth but has no config yet
    if (checked && isCatalog && !configId) {
      if (requiresAuth && !hasToken) {
        onNeedsToken();
        return;
      }
    }

    if (!configId) {
      onNeedsToken(); // No config yet — open modal
      return;
    }

    setToggling(true);
    try {
      await updateConfig(configId, { is_active: checked });
      onToggled();
    } catch (e) {
      console.error(e);
    } finally {
      setToggling(false);
    }
  }

  async function handleDelete() {
    if (!configId) return;
    if (!confirm(`Permanently delete "${name}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await deleteConfig(configId);
      onDeleted();
    } catch (e) {
      console.error(e);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div
      className={`group flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 
        ${isActive ? "bg-violet-500/10 border border-violet-500/20" : "hover:bg-white/5 border border-transparent"}`}
    >
      {/* Icon */}
      <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0 overflow-hidden">
        {isCatalog && entry.icon_url ? (
          <img src={entry.icon_url} alt={name} className="w-5 h-5 object-contain" />
        ) : (
          <Plug className="w-4 h-4 text-white/40" />
        )}
      </div>

      {/* Name + status */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white truncate">{name}</p>
        {isActive && (
          <p className="text-xs text-violet-400">Connected</p>
        )}
        {isCatalog && entry.requires_auth && !hasToken && !isActive && (
          <p className="text-xs text-yellow-500/70 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" /> Token required
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1.5">
        {/* Edit button */}
        {configId && (
          <Tooltip>
            <TooltipTrigger>
              <button
                onClick={onEdit}
                className="w-6 h-6 rounded-md flex items-center justify-center opacity-0 group-hover:opacity-100 transition text-white/40 hover:text-white hover:bg-white/10"
              >
                <Pencil className="w-3.5 h-3.5" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Edit</TooltipContent>
          </Tooltip>
        )}

        {/* Delete — only for custom */}
        {type === "custom" && configId && (
          <Tooltip>
            <TooltipTrigger>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="w-6 h-6 rounded-md flex items-center justify-center opacity-0 group-hover:opacity-100 transition text-red-400/60 hover:text-red-400 hover:bg-red-400/10"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Delete</TooltipContent>
          </Tooltip>
        )}

        {/* Toggle */}
        <Switch
          checked={isActive}
          onCheckedChange={handleToggle}
          disabled={toggling}
          className="data-[state=checked]:bg-violet-500"
        />
      </div>
    </div>
  );
}
