import React from "react";
import { FaRobot } from "react-icons/fa";
import { BsGear } from "react-icons/bs";
import "./styles/Sidebar.css";
import SidebarMiddle from "./sidebarmiddle";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
// import { faMessage } from "@fortawesome/free-regular-svg-icons";
import { faCompass } from "@fortawesome/free-solid-svg-icons";
import { faMessage } from "@fortawesome/free-solid-svg-icons";
import { faHistory } from "@fortawesome/free-solid-svg-icons";
import { useNavigate } from "react-router-dom";
import ChatHistory from "./ChatHistory";
import { useState } from "react";


function Sidebar({ setActiveView , setshowPopUp}) {
  
  const navigate = useNavigate();

  const navItems = [
    { view: "chat", icon: faMessage, label: "SBOT", route: "/chat" },
    { view: "explore", icon: faCompass, label: "Explore SBOTs", route: "/explore" },
    { view: "chat_history", icon: faHistory, label: "History", route: "/chat_history" },
  ];

  const handleNavigation = (view, path) => {
    if (view === "chat_history") {
      setshowPopUp((prev) => !prev);
    }
    setActiveView(view);
    navigate(path);
  }


  return (
    <div className="sidebar">
      <div className="sidebar-1">
        <div className="logo">
          <FaRobot size={24} />
          <h2>SONATABOT</h2>
          <br></br>
          {/* <div>powered by Markytics</div> */}
        </div>
        <div className="nav">
          {navItems.map(({ view, icon, label, route }) => (
            <p onClick={() =>handleNavigation(view, route)}>
              <span key={view} className="new-chat">
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
          <BsGear size={18} />{" "}
          <h5
            onClick={() =>handleNavigation("settings", "/settings")}
            style={{ cursor: "pointer" }}
          >
            Settings
          </h5>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
