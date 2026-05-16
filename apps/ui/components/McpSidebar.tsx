"use client";

import { useCallback, useEffect, useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Plus, RefreshCw } from "lucide-react";
import { getCatalog, getUserConfigs, CatalogEntry, UserMcpConfig } from "@/lib/api";
import { McpCard } from "./McpCard";
import { McpModal } from "./McpModal";

interface McpSidebarProps {
  userId: string;
}

type ModalState =
  | { open: false }
  | { open: true; mode: "add-custom" }
  | { open: true; mode: "auth-required"; catalogEntry: CatalogEntry }
  | { open: true; mode: "edit-catalog"; catalogEntry: CatalogEntry; userConfig: UserMcpConfig }
  | { open: true; mode: "edit-custom"; userConfig: UserMcpConfig };

export function McpSidebar({ userId }: McpSidebarProps) {
  const [catalog, setCatalog] = useState<CatalogEntry[]>([]);
  const [customConfigs, setCustomConfigs] = useState<UserMcpConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState<ModalState>({ open: false });

  const refresh = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const [cat, custom] = await Promise.all([
        getCatalog(userId),
        getUserConfigs(userId).then((configs) => configs.filter((c) => c.is_custom)),
      ]);
      setCatalog(cat);
      setCustomConfigs(custom);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function closeModal() {
    setModal({ open: false });
  }

  return (
    <aside className="w-72 flex-shrink-0 bg-[#0f0f1a] border-r border-white/5 flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-4 border-b border-white/5">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white/80 tracking-wide uppercase">
            MCP Servers
          </h2>
          <button
            onClick={refresh}
            disabled={loading}
            className="w-6 h-6 flex items-center justify-center rounded-md text-white/30 hover:text-white hover:bg-white/5 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      <ScrollArea className="flex-1 px-2 py-3">
        {/* Built-in catalog */}
        <p className="text-xs font-medium text-white/30 px-2 mb-2 uppercase tracking-wider">
          Available
        </p>
        <div className="space-y-0.5">
          {catalog.map((entry) => (
            <McpCard
              key={entry.id}
              item={entry}
              type="catalog"
              onEdit={() => {
                if (entry.user_config_id) {
                  // find matching UserMcpConfig
                  const uc = { id: entry.user_config_id } as UserMcpConfig;
                  setModal({ open: true, mode: "edit-catalog", catalogEntry: entry, userConfig: uc });
                }
              }}
              onDeleted={refresh}
              onToggled={refresh}
              onNeedsToken={() =>
                setModal({ open: true, mode: "auth-required", catalogEntry: entry })
              }
            />
          ))}
        </div>

        {/* Custom configs */}
        {customConfigs.length > 0 && (
          <>
            <Separator className="my-3 bg-white/5" />
            <p className="text-xs font-medium text-white/30 px-2 mb-2 uppercase tracking-wider">
              Custom
            </p>
            <div className="space-y-0.5">
              {customConfigs.map((config) => (
                <McpCard
                  key={config.id}
                  item={config}
                  type="custom"
                  onEdit={() =>
                    setModal({ open: true, mode: "edit-custom", userConfig: config })
                  }
                  onDeleted={refresh}
                  onToggled={refresh}
                  onNeedsToken={() => {}}
                />
              ))}
            </div>
          </>
        )}
      </ScrollArea>

      {/* Add Custom Button */}
      <div className="p-3 border-t border-white/5">
        <button
          onClick={() => setModal({ open: true, mode: "add-custom" })}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-sm text-white/50 hover:text-white hover:bg-white/5 border border-dashed border-white/10 hover:border-white/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          Add Custom Server
        </button>
      </div>

      {/* Modal */}
      {modal.open && modal.mode === "add-custom" && (
        <McpModal
          open
          onClose={closeModal}
          onSuccess={refresh}
          userId={userId}
        />
      )}
      {modal.open && modal.mode === "auth-required" && (
        <McpModal
          open
          onClose={closeModal}
          onSuccess={refresh}
          userId={userId}
          catalogEntry={modal.catalogEntry}
        />
      )}
      {modal.open && modal.mode === "edit-catalog" && (
        <McpModal
          open
          onClose={closeModal}
          onSuccess={refresh}
          userId={userId}
          catalogEntry={modal.catalogEntry}
          editTarget={modal.userConfig}
        />
      )}
      {modal.open && modal.mode === "edit-custom" && (
        <McpModal
          open
          onClose={closeModal}
          onSuccess={refresh}
          userId={userId}
          editTarget={modal.userConfig}
        />
      )}
    </aside>
  );
}
