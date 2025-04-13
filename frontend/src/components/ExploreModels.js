import React from "react";
import { useNavigate } from "react-router-dom";


const ExploreModels = ({ setActiveView }) => {
  const navigate = useNavigate();

  const handleNavigation = (view, route) => {
    setActiveView(view);
    navigate(route);
  }


    return (
      <div className="explore-models">
        <div class="row">
          <div class="col-sm-12 col-md-4 mb-30">
            <div
              class="card card-box"
              onClick={() => handleNavigation("sonata", "/explore/sonata")}
              style={{ cursor: "pointer" }}
            >
              <div>
                <img src="/robo3.png" height={"100px"} width={"100px"} />
              </div>
              <div class="card-body">
                <h5 class="card-title">SONATA BANK BOT</h5>
                <p class="card-text">
                  Here you can search for anything in your table for the mumbai
                  region.
                </p>
              </div>
            </div>
          </div>
          <div class="col-sm-12 col-md-4 mb-30">
            <div
              class="card card-box"
              onClick={() => handleNavigation("scrubdata", "/explore/scrubdata")}
              style={{ cursor: "pointer" }}
            >
              <div>
                <img src="/robo3.png" height={"100px"} width={"100px"} />
              </div>
              <div class="card-body">
                <h5 class="card-title">SCRUB DATA BOT DWSF GEO</h5>
                <p class="card-text">
                  Here you can search for anything in your table for scrub data
                  bot region.
                </p>
              </div>
            </div>
          </div>
          <div class="col-sm-12 col-md-4 mb-30">
            <div
              class="card card-box"
              onClick={() => handleNavigation("dswf", "/explore/dwsf")}
              style={{ cursor: "pointer" }}
            >
              <div>
                <img src="/robo3.png" height={"100px"} width={"100px"} />
              </div>
              {/* <h5 class="card-header weight-500">SBOT</h5> */}
              <div class="card-body">
                <h5 class="card-title">SCRUB DATA BOT DWSF GEO</h5>
                <p class="card-text">
                  Here you can search for anything in your table for day wise
                  data of Customer.
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-sm-12 col-md-4 mb-30">
            <div
              class="card card-box"
              onClick={() =>
                handleNavigation("scrubdataOther", "/explore/scrubdataOther")
              }
              style={{ cursor: "pointer" }}
            >
              <div>
                <img src="/robo3.png" height={"100px"} width={"100px"} />
              </div>
              <div class="card-body">
                <h5 class="card-title">PAYING TO OTHERS</h5>
                <p class="card-text">
                  Here you can search for customers paying to other banks but
                  not sonata.
                </p>
              </div>
            </div>
          </div>
          <div class="col-sm-12 col-md-4 mb-30">
            <div
              class="card card-box"
              onClick={() =>
                handleNavigation("scrubdataSonata", "/explore/scrubdataSonata")
              }
              style={{ cursor: "pointer" }}
            >
              <div>
                <img src="/robo3.png" height={"100px"} width={"100px"} />
              </div>
              <div class="card-body">
                <h5 class="card-title">PAYING TO SONATA</h5>
                <p class="card-text">
                  Here you can search for customers paying to sonata but not
                  other banks.
                </p>
              </div>
            </div>
          </div>
          {/* <div class="col-sm-12 col-md-4 mb-30">
            <div
              class="card card-box"
              onClick={() => setActiveView("scrubdataNeither")}
              style={{ cursor: "pointer" }}
            >
              <div class="card-body">
                <h5 class="card-title">NEITHER OF THE BANKS</h5>
                <p class="card-text">
                  Here you can search for customers who are paying to neither of
                  the banks.
                </p>
              </div>
            </div>
          </div> */}
          <div class="col-sm-12 col-md-4 mb-30">
            <div
              class="card card-box"
              onClick={() => handleNavigation("dwsf_websocket", "/explore/dwsf_websocket")}
              style={{ cursor: "pointer" }}
            >
              <div>
                <img src="/robo3.png" height={"100px"} width={"100px"} />
              </div>
              <div class="card-body">
                <h5 class="card-title">SCRUB DATA BOT DWSF -2</h5>
                <p class="card-text">
                  Here you can search for anything in your table for day wise
                  data of Customer.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="row"></div>
      </div>
    );
}

export default ExploreModels;