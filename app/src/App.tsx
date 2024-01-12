import React, { useState, useEffect } from 'react';
import './App.css'; // Ensure you have this CSS file

function App() {
  const ws = React.useRef<WebSocket | null>(null);
  const [messages, setMessages] = useState<{ sender: string, content: string }[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8080');

    ws.current.onmessage = async (event) => {
      const newMessage = typeof event.data === 'string' ? event.data : await event.data.text();
      setMessages(prevMessages => [...prevMessages, { sender: 'ai', content: newMessage }]);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const handleSubmit = (e: { preventDefault: () => void; }) => {
    e.preventDefault();
    if (message !== "") {
      setMessages(prevMessages => [...prevMessages, { sender: 'user', content: message }]);
      ws.current?.send(message);
      setMessage("");
    }
  }

  return (
    <div className="App">
      <h1>Coding Chat</h1>
      <p> Ask Your Coding DSA question and get your answer</p>
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <span className="sender">{msg.sender.toUpperCase()}: </span>
            {msg.sender === 'ai'
              ? <pre>{msg.content}</pre>
              : msg.content
            }
          </div>
        ))}
      </div>
      <div className="chat-input-container">
        <form onSubmit={handleSubmit}>
          <input
            type='text'
            value={message}
            onChange={e => setMessage(e.target.value)} />
          <button type="submit">Send</button>
        </form>
      </div>
    </div>

  );
}

export default App;
