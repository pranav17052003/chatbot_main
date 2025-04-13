import React from "react";
import "../styles/ChatArea.css";
import Chatbot from "../chatbot";

function ChatAreaScrubdataPayNeither() {
  return (
    <div className="bot-chat-area">
      <h1>What can I help with?</h1>
      <span>
        {" "}
        I am a specialized bot that could answer specific questions related to
        customers paying to Neither of the banks.
      </span>
      <div className="bot-chat-box">
        <Chatbot route="scrubdataNeither" />
      </div>
    </div>
  );
}

export default ChatAreaScrubdataPayNeither;
