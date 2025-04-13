import React from "react";
import "../styles/ChatArea.css";
import Chatbot1 from "../chatbot1";

function ChatAreadwsf_websocket() {
  return (
    <div className="bot-chat-area">
      <h1>What can I help with?</h1>
      <span>
        {" "}
        I am a specialized bot that could answer specific questions related to
        sonata
      </span>
      <div className="bot-chat-box">
        <Chatbot1 />
      </div>
    </div>
  );
}

export default ChatAreadwsf_websocket;
