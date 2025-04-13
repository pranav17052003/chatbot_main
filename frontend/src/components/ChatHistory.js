import React, { useState } from "react";
import "./styles/ChatHistory.css";

const ChatHistory = ({ popup }) => {
    const [isPopupOpen, setIsPopupOpen] = useState(false);

    const togglePopup = () => {
        setIsPopupOpen(!popup);
    };

  // Sample chat history data
  const chatHistory = [
    {
      id: 1,
      title: "React Chat History Popup Design",
      time: "41 minutes ago",
      category: "Today",
    },
    {
      id: 2,
      title: "DIVRAY --> CHAT HISTORY IN CHATBOT",
      time: "46 minutes ago",
      category: "Today",
    },
    {
      id: 3,
      title: "Code Refactoring: Import Organization",
      time: "54 minutes ago",
      category: "Today",
    },
    {
      id: 4,
      title: "React Router Implementation for App Compo...",
      time: "19 hours ago",
      category: "Yesterday",
    },
    {
      id: 5,
      title: "Software Development Terminology Explained",
      time: "19 hours ago",
      category: "Yesterday",
    },
    {
      id: 6,
      title: "React Component: Conditional Robot Icon Ren...",
      time: "2 days ago",
      category: "Last 7 Days",
    },
    {
      id: 7,
      title: "React App for SBOTs and Data Management",
      time: "2 days ago",
      category: "Last 7 Days",
    },
  ];

  // Group chats by category
  const groupedChats = chatHistory.reduce((acc, chat) => {
    if (!acc[chat.category]) {
      acc[chat.category] = [];
    }
    acc[chat.category].push(chat);
    return acc;
  }, {});

  return (
    <>
      {/* Background content that will be blurred */}
      <div className={`background-content ${popup ? "blurred" : ""}`}>
        {/* <button onClick={togglePopup} className="open-popup-button">
          Open Chat History
        </button> */}
        {/* Your other page content would go here */}
      </div>

      {/* Popup - not part of the blurred content */}
      {popup && (
        <div className="popup-overlay" onClick={togglePopup}>
          <div className="popup-content" onClick={(e) => e.stopPropagation()}>
            <div className="popup-header">
              <h3>Chat History</h3>
              <button onClick={togglePopup} className="close-button">
                &times;
              </button>
            </div>
            <div className="search-bar">
              <input type="text" placeholder="Search..." />
            </div>
            <div className="chat-history-list">
              {Object.entries(groupedChats).map(([category, chats]) => (
                <div key={category} className="category-section">
                  <div className="category-title">{category}</div>
                  {chats.map((chat) => (
                    <div key={chat.id} className="chat-item">
                      <div className="chat-title">{chat.title}</div>
                      <div className="chat-time">{chat.time}</div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
            <div className="popup-footer">
              <button className="create-new-chat-button">
                Create New Chat
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatHistory;
