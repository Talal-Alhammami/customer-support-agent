import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hello! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  // Scroll to the newest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(event) {
    event.preventDefault();

    const text = input.trim();
    if (!text || loading) return;

    // Last 2 customer messages, taken BEFORE the new message is added
    const history = messages
      .filter((m) => m.role === "user")
      .slice(-2)
      .map((m) => m.text);

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history }),
      });

      if (!response.ok) {
        throw new Error(`Server error ${response.status}`);
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          sourceType: data.source_type,
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Sorry, something went wrong. Is the backend running?",
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat">
      <header className="chat-header">🤖 AI Customer Support</header>

      <main className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className={`bubble ${message.isError ? "error" : ""}`}>
              {message.text}
            </div>
            {message.sourceType && (
              <span className="badge">{message.sourceType}</span>
            )}
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="bubble typing">Thinking…</div>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      <form className="chat-input" onSubmit={sendMessage}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default App;