import React from "react";
import "./styles/ChatArea.css";
import "./styles/Explore.css"
import Chatbot from "./chatbot";
import ExploreModels from "./ExploreModels";


function ChatArea({setActiveView}) {
  return (
    <div className="explore-box">
      <h1>SBOTS</h1>
      <div className="your-models">
        <span>
          Discover and create custom versions of SBOT that combine
          instructions, extra knowledge, and any combination of skills.
        </span>
        <ExploreModels setActiveView={setActiveView} />
      </div>
    </div>
  );
}

export default ChatArea;
