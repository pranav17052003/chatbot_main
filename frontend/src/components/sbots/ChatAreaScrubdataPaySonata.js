import React from "react";
import "../styles/ChatArea.css";
import Chatbot from "../chatbot";

function ChatAreaScrubdataPaySonata() {
  return (
    <div className="bot-chat-area">
      <h1>What can I help with?</h1>
      <span>
        {" "}
        I am a specialized bot that could answer specific questions related to
              customers paying to sonata but not other banks.
      </span>
      <div className="bot-chat-box">
        <Chatbot route="scrubdataSonata" />
      </div>
    </div>
  );
}

export default ChatAreaScrubdataPaySonata;
