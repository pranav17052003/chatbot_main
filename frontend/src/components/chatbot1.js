import React, { useState, useRef, useEffect } from "react";
import "./styles/Chatbot.css";

const Chatbot1 = (props) => {
  const { route } = props;
  const [query, setQuery] = useState("");
  const [responses, setResponses] = useState([
    { type: "bot", text: "Hi! I am SONATABOT. How can I help you today?" },
  ]);
  const [loading, setLoading] = useState(false);
  const [lastFailedQuery, setLastFailedQuery] = useState(null);
  const messagesContainerRef = useRef(null);
  const wsRef = useRef(null);
  const username = "testUser";
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const [csvShow, setcsvShow] = useState(false)

  const connectWebSocket = () => {
    if (
      wsRef.current &&
      (wsRef.current.readyState === WebSocket.OPEN ||
        wsRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    setTimeout(() => {
      const websocket = new WebSocket(`ws://localhost:8000/ws/chat/`);
      wsRef.current = websocket;

      websocket.onopen = () => {
        console.log("WebSocket connection established");
        reconnectAttempts.current = 0;
        setLoading(false);
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          console.log("Received data:", data);
          if (data.type === "csv_download") {
            // Handle CSV download
            const blob = new Blob([data.csv_data], { type: "text/csv" });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = data.filename || "chat_data.csv";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
          } else if (data.ai_response) {
            setResponses((prev) => [
              ...prev,
              { type: "bot", text: data.ai_response },
            ]);
            setLoading(false);
            setcsvShow(true);
          } else {
            console.warn("No ai_response in message:", data);
            setResponses((prev) => [
              ...prev,
              { type: "bot", text: "Unexpected response format from server." },
            ]);
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
          setResponses((prev) => [
            ...prev,
            { type: "bot", text: "Error processing server response." },
          ]);
          
          setLoading(false);
          
        }
      };

      websocket.onclose = (event) => {
        console.log("WebSocket connection closed:", event.code, event.reason);
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current += 1;
          console.log(
            `Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts})...`
          );
          setTimeout(connectWebSocket, 2000 * reconnectAttempts.current);
        } else {
          alert(
            "Failed to establish connection after maximum retries. Please refresh the page and try again."
          );
        }
        setLoading(false);
      };

      websocket.onerror = (error) => {
        console.error("WebSocket error:", error);
        setLastFailedQuery(query);
        setLoading(false);
      };
    }, 2000);
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleQuerySubmit = (e, retryQuery = null) => {
    setcsvShow(false);
    e.preventDefault();
    const question = retryQuery || query;

    if (
      !question.trim() ||
      !wsRef.current ||
      wsRef.current.readyState !== WebSocket.OPEN
    ) {
      setResponses((prev) => [
        ...prev,
        {
          type: "bot",
          text: "Connection not available. Please wait or refresh the page.",
        },
      ]);
      
      return;
    }
    
    setResponses((prev) => [...prev, { type: "user", text: question }]);
    setQuery("");
    setLoading(true);
    setLastFailedQuery(null);

    const messageData = {
      message: question,
      username: username,
    };
    wsRef.current.send(JSON.stringify(messageData));
    
  };

  const handleCancelRequest = () => {
    if (wsRef.current) {
      wsRef.current.close();
      setLoading(false);
      setResponses((prev) => [
        ...prev,
        { type: "bot", text: "Request canceled by the user." },
      ]);
    }
  };

  // New function to handle CSV download
  const handleDownloadCSV = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      setResponses((prev) => [
        ...prev,
        {
          type: "bot",
          text: "Connection not available. Please wait or refresh the page.",
        },
      ]);
      return;
    }

    
    const messageData = {
      message: "download_csv",
      username: username,
    };
    wsRef.current.send(JSON.stringify(messageData));
  };

  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTo({
        top: messagesContainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [responses, loading]);

  return (
    <div className="chatbot-container">
      <div
        className="chatbot-messages"
        ref={messagesContainerRef}
        tabIndex={0} /* Make the container focusable */
      >
        {responses.map((msg, index) => (
          <div key={index} className={`chatbot-message ${msg.type}`}>
            {msg.type === "bot" ? (
              <div>
                <div dangerouslySetInnerHTML={{ __html: msg.text }} />
              </div>
            ) : (
              msg.text
            )}
            {msg.text ===
              "Connection not available. Please wait or refresh the page." &&
              lastFailedQuery && (
                <button
                  className="retry-button"
                  onClick={(e) => handleQuerySubmit(e, lastFailedQuery)}
                >
                  Retry
                </button>
              )}
          </div>
        ))}
        <div>
          {csvShow && (
            <button
              onClick={handleDownloadCSV}
              // disabled={loading}
              className="download-button"
            >
              <img src="/downloads.png" height={"12px"} width={"12px"} />
            </button>
          )}
        </div>
        {loading && (
          <div className="chatbot-message bot loading">
            <span className="loading-dots">SONATABOT is working...</span>
          </div>
        )}
      </div>
      <form className="chatbot-input" onSubmit={handleQuerySubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Message SONATABOT"
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Loading..." : "Send"}
        </button>
        {loading && (
          <button
            type="button"
            onClick={handleCancelRequest}
            className="cancel-button"
          >
            Cancel
          </button>
        )}
      </form>
      {/* Add Download CSV Button */}
    </div>
  );
};

export default Chatbot1;
