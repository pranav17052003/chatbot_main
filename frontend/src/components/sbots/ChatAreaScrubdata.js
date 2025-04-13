import React from "react";
import "../styles/ChatArea.css";
import Chatbot from "../chatbot";

function ChatAreaScrubdata() {
  return (
    <div className="bot-chat-area">
      <h1>What can I help with?</h1>
      <span>
        {" "}
        I am a specialized bot that could answer specific questions related to
        scrub data.
      </span>
      <div className="bot-chat-box">
        <Chatbot route="scrub-data" />
      </div>
    </div>
  );
}

export default ChatAreaScrubdata;
