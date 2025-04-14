import React from "react";
import { FaRobot } from "react-icons/fa";
import { BsGear } from "react-icons/bs";
import "./styles/Sidebar.css";
import SidebarMiddle from "./sidebarmiddle";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCompass } from "@fortawesome/free-solid-svg-icons";
import { faMessage } from "@fortawesome/free-solid-svg-icons";
import { faHistory } from "@fortawesome/free-solid-svg-icons";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

function Sidebar({ setActiveView, setshowPopUp, setIsAuthenticated }) {
  // Add setIsAuthenticated here
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const navItems = [
    { view: "chat", icon: faMessage, label: "SBOT", route: "/chat" },
    {
      view: "explore",
      icon: faCompass,
      label: "Explore SBOTs",
      route: "/explore",
    },
    {
      view: "chat_history",
      icon: faHistory,
      label: "History",
      route: "/chat_history",
    },
  ];

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      const response = await fetch("http://localhost:8000/auth/logout/", {
        method: "POST",
        credentials: "include",
      });

      if (response.ok) {
        setIsAuthenticated(false);
        navigate("/login"); // Redirect to login page after logout
      }
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const handleNavigation = (view, path) => {
    if (view === "chat_history") {
      setshowPopUp((prev) => !prev);
    }
    setActiveView(view);
    navigate(path);
  };

  return (
    <div className="sidebar">
      <div className="sidebar-1">
        <div className="logo">
          <FaRobot size={24} />
          <h2>SONATABOT</h2>
          <br></br>
        </div>
        <div className="nav">
          {navItems.map(({ view, icon, label, route }) => (
            <p key={view} onClick={() => handleNavigation(view, route)}>
              <span className="new-chat">
                <FontAwesomeIcon icon={icon} size="md" />
                <br></br>
                <span>{label}</span>
              </span>
            </p>
          ))}
        </div>
      </div>
      <SidebarMiddle />
      <div>
        <div className="sidebar-2">
          <BsGear size={18} />
          <h5
            onClick={() => handleNavigation("settings", "/settings")}
            style={{ cursor: "pointer" }}
          >
            Settings
          </h5>
          <button
            onClick={handleLogout}
            className="logout-button"
            disabled={isLoggingOut}
          >
            {isLoggingOut ? "Logging out..." : "Logout"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
