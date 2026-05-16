"use client";

import { TooltipProvider } from "@/components/ui/tooltip";
import { McpSidebar } from "@/components/McpSidebar";
import { ChatPanel } from "@/components/ChatPanel";
import { useUserId } from "@/lib/useUserId";

export default function Home() {
  const userId = useUserId();

  if (!userId) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#12121f]">
        <div className="w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <TooltipProvider>
      <div className="flex h-screen overflow-hidden bg-[#12121f]">
        <McpSidebar userId={userId} />
        <ChatPanel userId={userId} />
      </div>
    </TooltipProvider>
  );
}
