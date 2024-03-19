import React, { useState } from "react";
import "./App.css";
import "reactjs-popup/dist/index.css";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

function MyVerticallyCenteredModal(props) {
  return (
    <Modal
      {...props}
      size="lg"
      aria-labelledby="contained-modal-title-vcenter"
      centered
    >
      <Modal.Header closeButton>
        <Modal.Title id="contained-modal-titlevcenter">
          Thank you for using our service!
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p>We appreciate your trust in our Insurance Charges Prediction App.</p>
      </Modal.Body>
      <Modal.Footer>
        <Button onClick={props.onHide}>Close</Button>
      </Modal.Footer>
    </Modal>
  );
}

function App() {
  const [runLoading, setRunLoading] = useState(false);
  const [runMessage, setRunMessage] = useState("");

  const [enquiryLoading, setEnquiryLoading] = useState(false);
  const [enquiryMessage, setEnquiryMessage] = useState("");

  const [callLoading, setCallLoading] = useState(false);
  const [callMessage, setCallMessage] = useState("");

  const [modalShow, setModalShow] = useState(false);
  const [buttonsDisabled, setButtonsDisabled] = useState(false);

  const runPythonScript = async () => {
    try {
      console.log("Sending request to run Python script...");
      setButtonsDisabled(true);
      setRunLoading(true);
      setTimeout(() => {
        setRunMessage("Request sent successfully!");
      }, 10000);
      setRunMessage("Please wait...");

      const response = await fetch("http://localhost:5000/run-script", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
      console.log(response);
      if (response.ok) {
        console.log("Python script executed successfully");
        setModalShow(true);
      } else {
        setRunMessage("Failed to send request.");
      }
    } catch (error) {
      setRunMessage("Error connecting to the server.");
    } finally {
      setRunLoading(false);
      setButtonsDisabled(false);
    }
  };

  const runEnquiryScript = async () => {
    try {
      console.log("Sending request to run Python script...");
      setButtonsDisabled(true);
      setEnquiryLoading(true);
      setTimeout(() => {
        setEnquiryMessage("Request sent successfully!");
      }, 10000);
      setEnquiryMessage("Please wait...");

      const response = await fetch("http://localhost:5000/enquiry-script", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        console.log("Python script executed successfully");
        setModalShow(true);
      } else {
        setEnquiryMessage("Failed to send request.");
      }
    } catch (error) {
      setEnquiryMessage("Error connecting to the server.");
    } finally {
      setEnquiryLoading(false);
      setButtonsDisabled(false);
    }
  };

  const runCallScript = async () => {
    try {
      console.log("Sending request to run Python script...");
      setButtonsDisabled(true);
      setCallLoading(true);
      setTimeout(() => {
        setCallMessage("Request sent successfully!");
      }, 10000);
      setCallMessage("Please wait...");

      const response = await fetch("http://localhost:5000/call-script", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        console.log("Python script executed successfully");
        setModalShow(true);
      } else {
        setCallMessage("Failed to send request.");
      }
    } catch (error) {
      setCallMessage("Error connecting to the server.");
    } finally {
      setCallLoading(false);
      setButtonsDisabled(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Insurance Charges Prediction App</h1>
        <div className="button-container">
          <button
            className="run-button"
            onClick={runPythonScript}
            disabled={runLoading || buttonsDisabled}
          >
            {runLoading ? "Request Sent" : "I want to buy Health Insurance"}
          </button>
          {runLoading && <p className="message">{runMessage}</p>}

          <button
            className="enquiry-button"
            onClick={runEnquiryScript}
            disabled={enquiryLoading || buttonsDisabled}
          >
            {enquiryLoading ? "Request Sent" : "Enquiry"}
          </button>
          {enquiryLoading && <p className="message">{enquiryMessage}</p>}

          <button
            className="call-button"
            onClick={runCallScript}
            disabled={callLoading || buttonsDisabled}
          >
            {callLoading ? "Request Sent" : "Call User"}
          </button>
          {callLoading && <p className="message">{callMessage}</p>}
        </div>
        <MyVerticallyCenteredModal
          show={modalShow}
          onHide={() => setModalShow(false)}
        />
      </header>
    </div>
  );
}

export default App;
