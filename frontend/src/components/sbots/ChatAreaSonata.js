import React from "react";
import "../styles/ChatArea.css";
import ChatbotSonata from "../chatbotsonata";

function ChatAreaSonata() {
  return (
    <div className="bot-chat-area">
          <h1>What can I help with?</h1>
          <span> I am a specialized bot that could answer specific questions related to sonata</span>
      <div className="bot-chat-box">
        <ChatbotSonata route="sonata"/>
      </div>
    </div>
  );
}

export default ChatAreaSonata;
