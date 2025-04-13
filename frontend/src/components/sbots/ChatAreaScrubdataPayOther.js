import React from "react";
import "../styles/ChatArea.css";
import Chatbot from "../chatbot";

function ChatAreaScrubdataPayOther() {
  return (
    <div className="bot-chat-area">
      <h1>What can I help with?</h1>
      <span>
        {" "}
        I am a specialized bot that could answer specific questions related to
              customers paying to other banks but not sonata.
      </span>
      <div className="bot-chat-box">
        <Chatbot route="scrubdataOther" />
      </div>
    </div>
  );
}

export default ChatAreaScrubdataPayOther;
