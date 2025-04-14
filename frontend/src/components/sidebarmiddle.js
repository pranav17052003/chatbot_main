import React, { useState, useEffect } from "react";
// import "./styles/sweetalert2.css";
import "./styles/main.css";
import { faCopy } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faWandMagicSparkles } from "@fortawesome/free-solid-svg-icons";

const SidebarMiddle = () => {
  const [copiedId, setCopiedId] = useState(null);
  const [topQuestions, setTopQuestions] = useState([]); // State for top 5 questions
  const [ws, setWs] = useState(null); // WebSocket state

  const examples = [
    {
      id: 1,
      example: "count loan application id where credit grantor is sonata",
      icon: faCopy,
    },
    {
      id: 2,
      example:
        "count loan application id where credit grantor is sonata and overdue amount is greater than 0",
      icon: faCopy,
    },
  ];

  // WebSocket setup
  useEffect(() => {
    const websocket = new WebSocket("ws://localhost:8000/ws/chat/"); // Adjust URL to your backend WebSocket endpoint
    setWs(websocket);

    websocket.onopen = () => {
      console.log("WebSocket connected");
      websocket.send(
        JSON.stringify({
          message: "show top questions",
          username: "user", // Replace with actual username if needed
        }));
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "top_questions") {
        // Parse the top_questions string into an array of lines
        const questions = data.top_questions
          .split("\n")
          .filter((line) => line.startsWith("- ") | line.startsWith("* "))
          .map((line) => line.replace("- ", "").trim() );
        setTopQuestions(questions);
      }
    };

    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    websocket.onclose = () => {
      console.log("WebSocket disconnected");
    };

    // Cleanup on unmount
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 1500); // Reset after 1.5s
    });
  };

  // Function to send "show top questions" command
  const refreshTopQuestions = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(
        JSON.stringify({
          message: "show top questions",
          username: "user", // Replace with actual username if needed
        })
      );
    }
  };

  return (
    <div className="sidebar-middle">
      {/* Example Prompts Section */}
      <div className="sidebar-example">
        {/* <span>Example Prompts</span> */}
        {/* <div className="sidebar-example-list">
          {examples.map(({ id, example, icon }) => (
            <p key={id}>
              <span
                onClick={() => handleCopy(example, id)}
                style={{
                  cursor: "pointer",
                  color: copiedId === id ? "green" : "white",
                }}
              >
                <FontAwesomeIcon icon={icon} />
                {copiedId === id && (
                  <span style={{ color: "green" }}> Copied!</span>
                )}
              </span>
              <span>{example}</span>
            </p>
          ))}
        </div> */}
      </div>

      {/* Top 5 Frequently Asked Questions Section */}
      <div className="sidebar-example" style={{ marginTop: "20px" }}>
        <span>
          AI Example Questions{" "}
          <button
            onClick={refreshTopQuestions}
            style={{
              marginLeft: "0px",
              padding: "0px 0px",
              background: "transparent",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            <img src="/refresh.png" height={"15px"} width={"15px"} />
          </button>
        </span>
        <div className="sidebar-example-list">
          {topQuestions.length > 0 ? (
            <ul>
              {topQuestions.map((question, index) => (
                <li
                  key={index}
                  style={{
                    marginBottom: "10px",
                    fontSize: "13px",
                  }}
                >
                  <span
                    onClick={() => handleCopy(question, `top-${index}`)}
                    style={{
                      cursor: "pointer",
                      color: copiedId === `top-${index}` ? "green" : "white",
                      marginRight: "10px",
                    }}
                  >
                    <FontAwesomeIcon icon={faCopy} />
                    {copiedId === `top-${index}` && (
                      <span style={{ color: "green" }}> Copied!</span>
                    )}
                  </span>
                  {question}
                </li>
              ))}
            </ul>
          ) : (
            <div className="sidebar-example-list">
              <ul>
                {examples.map((example) => (
                  <li
                    key={example.id} // Use example.id for unique key
                    style={{
                      marginBottom: "10px",
                      fontSize: "13px",
                    }}
                  >
                    <span
                      onClick={() => handleCopy(example.example, `top-${example.id}`)} // Pass example.example to handleCopy
                      style={{
                        cursor: "pointer",
                        color: copiedId === `top-${example.id}` ? "green" : "white",
                        marginRight: "10px",
                      }}
                    >
                      <FontAwesomeIcon icon={example.icon} />
                      {copiedId === `top-${example.id}` && (
                        <span style={{ color: "green" }}> Copied!</span>
                      )}
                    </span>
                    {example.example} {/* Render the example string, not the object */}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SidebarMiddle;
