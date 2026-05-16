"use client";

import { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";

export function useUserId() {
  const [userId, setUserId] = useState<string>("");

  useEffect(() => {
    let id = localStorage.getItem("mcp_user_id");
    if (!id) {
      id = uuidv4();
      localStorage.setItem("mcp_user_id", id);
    }
    setUserId(id);
  }, []);

  return userId;
}
