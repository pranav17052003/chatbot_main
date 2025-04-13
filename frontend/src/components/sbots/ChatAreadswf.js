import React from "react";
import "../styles/ChatArea.css";
import Chatbot from "../chatbot";

function ChatAreadwsf() {
  return (
    <div className="bot-chat-area">
      <h1>What can I help with?</h1>
      <span>
        {" "}
        I am a specialized bot that could answer specific questions related to
        day wise sumary for a customer
      </span>
      <div className="bot-chat-box">
        <Chatbot route="dwsf" />
      </div>
    </div>
  );
}

export default ChatAreadwsf;
