"use client";

import { useState } from "react";
import "./page.css";

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  async function sendMessage() {
    if (!input.trim()) return;

    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: input,
      },
    ]);

    try {
      const response = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: input,
        }),
      });

      const data = await response.json();

      // Add bot response
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: 
          "Dosha " + data.dosha +
          "\n\nRecommmended Foods: " +
          data.recommended_food.join(", ") +
          "\n\nFoods to avoid:" +
          data.avoid_food.join(", ")
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: "Error connecting to backend.",
        },
      ]);
    }

    setInput("");
  }

  return (
    <div className="container">
      <h1 className="heading">🪔 Ayurvedic Chatbot</h1>

      <div className="chatBox">
        {messages.map((msg, index) => (
          <div key={index} className="message">
            <b className={msg.role === "user" ? "user" : "bot"}>
              {msg.role}:
            </b>{" "}
            {msg.content}
          </div>
        ))}
      </div>

      <div className="inputSection">
        <input
          className="inputBox"
          type="text"
          placeholder="Enter your symptoms..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />

        <button className="button" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}