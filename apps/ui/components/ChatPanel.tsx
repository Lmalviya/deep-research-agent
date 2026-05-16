"use client";

import { useRef, useState } from "react";
import { Send, Bot, User, Wrench, AlertCircle } from "lucide-react";
import { streamChat } from "@/lib/api";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Message {
  role: "user" | "assistant";
  content: string;
  tools?: string[];
  isStreaming?: boolean;
  isError?: boolean;
}

interface ChatPanelProps {
  userId: string;
}

export function ChatPanel({ userId }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  async function handleSend() {
    if (!input.trim() || loading || !userId) return;
    const query = input.trim();
    setInput("");
    setLoading(true);

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: query }]);

    // Add streaming assistant message placeholder
    const assistantIndex = messages.length + 1;
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", isStreaming: true },
    ]);

    try {
      let toolsInfo: string[] = [];

      for await (const chunk of streamChat(userId, query)) {
        if (chunk.type === "tool_info" && chunk.tools) {
          toolsInfo = chunk.tools;
          setMessages((prev) =>
            prev.map((m, i) =>
              i === assistantIndex ? { ...m, tools: toolsInfo } : m
            )
          );
        } else if (chunk.type === "token" && chunk.content) {
          setMessages((prev) =>
            prev.map((m, i) =>
              i === assistantIndex
                ? { ...m, content: m.content + chunk.content }
                : m
            )
          );
          bottomRef.current?.scrollIntoView({ behavior: "smooth" });
        } else if (chunk.type === "error") {
          setMessages((prev) =>
            prev.map((m, i) =>
              i === assistantIndex
                ? { ...m, content: chunk.content ?? "Error occurred", isStreaming: false, isError: true }
                : m
            )
          );
        } else if (chunk.type === "done") {
          setMessages((prev) =>
            prev.map((m, i) =>
              i === assistantIndex ? { ...m, isStreaming: false } : m
            )
          );
        }
      }
    } catch (e: unknown) {
      const err = e as { detail?: string };
      setMessages((prev) =>
        prev.map((m, i) =>
          i === assistantIndex
            ? { ...m, content: err?.detail ?? "Network error", isStreaming: false, isError: true }
            : m
        )
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#12121f]">
      {/* Messages */}
      <ScrollArea className="flex-1 px-6 py-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-24">
            <div className="w-14 h-14 rounded-2xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mb-4">
              <Bot className="w-7 h-7 text-violet-400" />
            </div>
            <h3 className="text-lg font-semibold text-white/80 mb-2">
              MCP Research Assistant
            </h3>
            <p className="text-sm text-white/40 max-w-xs">
              Activate MCP servers in the sidebar, then ask anything. The agent
              will use the connected tools to answer your query.
            </p>
          </div>
        )}

        <div className="space-y-6 max-w-3xl mx-auto">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="w-4 h-4 text-violet-400" />
                </div>
              )}

              <div className={`max-w-[75%] ${msg.role === "user" ? "items-end" : "items-start"} flex flex-col gap-2`}>
                {/* Tool badges */}
                {msg.tools && msg.tools.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {msg.tools.map((t) => (
                      <span
                        key={t}
                        className="flex items-center gap-1 text-xs bg-violet-500/10 text-violet-300 border border-violet-500/20 rounded-full px-2 py-0.5"
                      >
                        <Wrench className="w-2.5 h-2.5" />
                        {t}
                      </span>
                    ))}
                  </div>
                )}

                {/* Message bubble */}
                <div
                  className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
                    ${msg.role === "user"
                      ? "bg-violet-600 text-white rounded-tr-sm"
                      : msg.isError
                      ? "bg-red-500/10 border border-red-500/20 text-red-300"
                      : "bg-white/5 border border-white/8 text-white/90 rounded-tl-sm"
                    }`}
                >
                  {msg.isError && (
                    <AlertCircle className="w-3.5 h-3.5 inline mr-1.5 mb-0.5" />
                  )}
                  {msg.content || (msg.isStreaming ? "" : "...")}
                  {msg.isStreaming && (
                    <span className="inline-block w-1.5 h-4 bg-violet-400 ml-0.5 animate-pulse rounded-sm" />
                  )}
                </div>
              </div>

              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <User className="w-4 h-4 text-white/50" />
                </div>
              )}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="px-6 pb-6 pt-3 border-t border-white/5">
        <div className="max-w-3xl mx-auto">
          <div className="relative flex items-end gap-3 bg-white/5 border border-white/10 rounded-2xl px-4 py-3 focus-within:border-violet-500/50 transition">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask anything... (Shift+Enter for new line)"
              disabled={loading}
              rows={1}
              className="flex-1 bg-transparent text-sm text-white placeholder-white/30 resize-none outline-none max-h-32 overflow-y-auto"
              style={{ fieldSizing: "content" } as React.CSSProperties}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="w-8 h-8 flex items-center justify-center rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-30 disabled:cursor-not-allowed transition flex-shrink-0"
            >
              <Send className="w-4 h-4 text-white" />
            </button>
          </div>
          <p className="text-xs text-white/20 text-center mt-2">
            Responses are generated by the connected MCP tools.
          </p>
        </div>
      </div>
    </div>
  );
}
