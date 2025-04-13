import React from "react";
import "./styles/ChatArea.css";
import Chatbot from "./chatbot";

function ChatArea() {
  return (
    <div className="bot-chat-area">
      <h1>What can I help with?</h1>
      <div className="bot-chat-box">
        <Chatbot route="ask" />
      </div>
    </div>
  );
}

export default ChatArea;
