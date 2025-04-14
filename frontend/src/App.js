import "./App.css";
import "./components/styles/main.css";
import Sidebar from "./components/Sidebar";
import ChatArea from "./components/ChatArea";
import { useState, useEffect } from "react";
import Explore from "./components/Explore";
import ChatAreaSonata from "./components/sbots/ChatAreaSonata";
import ChatAreaScrubdata from "./components/sbots/ChatAreaScrubdata";
import ChatAreaScrubdataPaySonata from "./components/sbots/ChatAreaScrubdataPaySonata";
import ChatAreaScrubdataPayOther from "./components/sbots/ChatAreaScrubdataPayOther";
import ChatAreaScrubdataPayNeither from "./components/sbots/ChatAreaScrubdataPayNeither";
import ChatAreadwsf from "./components/sbots/ChatAreadswf";
import ChatAreadwsf_websocket from "./components/sbots/ChatAreadwsf_websocket";
import Settings from "./components/settings";
import ChatHistory from "./components/ChatHistory";
import { BrowserRouter as Router } from "react-router-dom";
import Login from "./components/Login"; // We'll create this component next

function App() {
  const [activeView, setActiveView] = useState("chat");
  const [showPopUp, setshowPopUp] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Check authentication status on app load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch("http://localhost:8000/auth/check-auth/", {
          credentials: "include",
        });
        const data = await response.json();
        setIsAuthenticated(data.authenticated);
      } catch (error) {
        console.error("Auth check failed:", error);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  const viewComponents = {
    chat: <ChatArea />,
    explore: <Explore setActiveView={setActiveView} />,
    sonata: <ChatAreaSonata />,
    scrubdata: <ChatAreaScrubdata />,
    scrubdataSonata: <ChatAreaScrubdataPaySonata />,
    scrubdataOther: <ChatAreaScrubdataPayOther />,
    scrubdataNeither: <ChatAreaScrubdataPayNeither />,
    dswf: <ChatAreadwsf />,
    dwsf_websocket: <ChatAreadwsf_websocket />,
    settings: <Settings />,
    chat_history: <ChatHistory popup={showPopUp} />,
  };

  if (loading) {
    return <div className="app-loading">Loading...</div>;
  }

  if (!isAuthenticated) {
    return (
      <Router>
        <div className="App">
          <Login setIsAuthenticated={setIsAuthenticated} />
        </div>
      </Router>
    );
  }

  return (
    <Router>
      <div className="App">
        <Sidebar
          setActiveView={setActiveView}
          setshowPopUp={setshowPopUp}
          setIsAuthenticated={setIsAuthenticated}
        />
        <div className="left-area">{viewComponents[activeView]}</div>
      </div>
    </Router>
  );
}

export default App;
