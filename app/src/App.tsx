import React, { useState, useEffect } from 'react';

function App() {
  // Use a ref for the websocket instance to persist across renders
  const ws = React.useRef<WebSocket | null>(null);
  const [messages, setMessages] = useState<String[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    // Initialize websocket connection once when the component is mounted
    ws.current = new WebSocket('ws://localhost:8080');

    ws.current.onmessage = async(event) => {
      const newMessage = typeof event.data === 'string' ? event.data : await event.data.text();
      setMessages(prevMessages => [...prevMessages, newMessage]);
    };

    // Clean up the websocket connection when the component is unmounted
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const handleSubmit = (e: { preventDefault: () => void; }) => {
    e.preventDefault();
    if (message !== "") {
      ws.current?.send(message);
      setMessage("");
    }
  }

  return (
    <div className="App">
      <h1>React WebSocket Example</h1>
      <form onSubmit={handleSubmit}>
        <input
          type='text'
          value={message.toString()}
          onChange={e => setMessage(e.target.value)} />
        <button type="submit">Send</button>
      </form>
      <div>
        {messages.map((msg, index) => (
          <div key={index}>{msg}</div>
        ))}
      </div>
    </div>
  );
}

export default App;
