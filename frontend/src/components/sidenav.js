import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTachometerAlt,
  // faUsers,
  // faMagic,
  // faCog,
} from "@fortawesome/free-solid-svg-icons";
import "./styles/sidenav.css"

const SideNav = () => {
  return (
    <div className="left-section-1">
      <div className="nav-item">
        <div>
          <a
            className="bg-body-tertiary"
            href="https://www.markytics.com/"
          >
            <img
              src="/markytics-logo.png"
              height={"40px"}
              width={"40px"}
              alt="logo"
            />
          </a>
        </div>
      </div>
      <div className="nav-item">
        <a href="/"><FontAwesomeIcon icon={faTachometerAlt} /></a>
      </div>
    </div>
  );
};

export default SideNav;
