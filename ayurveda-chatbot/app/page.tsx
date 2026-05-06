"use client";

import { useState } from "react";

type Message = {
  role: "user" | "bot";
  content: string;
};

export default function Home() {
  const [input, setInput] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);

  const sendMessage = async () => {
    if (!input) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const res = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: input })
      });

      const data = await res.json();

      const botMessage: Message = {
        role: "bot",
        content: `
Dosha: ${data.dosha}

Recommended:
${data.recommended_food.join(", ")}

Avoid:
${data.avoid_food.join(", ")}
`
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error:", error);
    }

    setInput("");
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>🧘 Ayurvedic Chatbot</h1>

      <div style={{ marginBottom: 20 }}>
        {messages.map((msg, i) => (
          <div key={i}>
            <b>{msg.role}:</b> {msg.content}
          </div>
        ))}
      </div>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter your symptoms..."
        style={{ width: "300px", marginRight: "10px" }}
      />

      <button onClick={sendMessage}>Send</button>
    </div>
  );
}