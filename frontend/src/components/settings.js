import React from "react";
import "./styles/ChatArea.css";
import "./styles/Explore.css";
import Chatbot from "./chatbot";
import ExploreModels from "./ExploreModels";
import "./styles/Settings.css"

function Settings({ setActiveView }) {
  // State to manage settings
  const [theme, setTheme] = React.useState("dark"); // Default theme
  const [notifications, setNotifications] = React.useState(true); // Default notifications on
  const [language, setLanguage] = React.useState("english"); // Default language

  // Handler to save settings (placeholder for now)
  const handleSave = () => {
    console.log("Settings saved:", { theme, notifications, language });
    // Add logic to persist settings (e.g., localStorage or API call)
  };

  return (
    <div className="explore-box">
      <h1>SETTINGS</h1>
      <div className="your-models">
        <span>
          {/* Theme Customization */}
          <div className="setting-item">
            <label>Theme:</label>
            <select value={theme} onChange={(e) => setTheme(e.target.value)}>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="custom">Custom</option>
            </select>
          </div>

          {/* Notification Settings */}
          <div className="setting-item">
            <label>Enable Notifications:</label>
            <input
              type="checkbox"
              checked={notifications}
              onChange={(e) => setNotifications(e.target.checked)}
            />
          </div>

          {/* Language Preferences */}
          <div className="setting-item">
            <label>Language:</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="english">English</option>
              <option value="spanish">Spanish</option>
              <option value="hindi">Hindi</option>
            </select>
          </div>

          {/* Save Button */}
          <button onClick={handleSave}>Save Settings</button>
        </span>
        {/* <ExploreModels setActiveView={setActiveView} /> */}
      </div>
    </div>
  );
}

export default Settings;
