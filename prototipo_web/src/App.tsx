import React from "react";
import "./App.css";
import INECapturePrototype from "./INECapturePrototype";

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Agente ID</h1>
      </header>

      <div className="card">
        <INECapturePrototype />
      </div>
    </div>
  );
}

export default App;
