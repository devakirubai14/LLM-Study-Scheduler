import { useState } from "react";
import "./App.css";

function App() {
  const [subject, setSubject] = useState("");
  const [hours, setHours] = useState("");
  const [days, setDays] = useState("");
  const [result, setResult] = useState([]);

  const generatePlan = async () => {
    const response = await fetch("http://localhost:5000/generate-plan", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        subject: subject,
        hours_per_day: hours,
        exam_days: days
      })
    });

    const data = await response.json();
    setResult(data.study_plan || []);
  };

  return (
    <div className="container">
      <h1>EduPlan-AI</h1>
      <p className="subtitle">
        Personalized Study Planner for Education 4.0
      </p>

      <div className="input-group">
        <input
          placeholder="Subject (e.g., Math)"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        />
      </div>

      <div className="input-group">
        <input
          type="number"
          placeholder="Hours per day"
          value={hours}
          onChange={(e) => setHours(e.target.value)}
        />
      </div>

      <div className="input-group">
        <input
          type="number"
          placeholder="Days until exam"
          value={days}
          onChange={(e) => setDays(e.target.value)}
        />
      </div>

      <button onClick={generatePlan}>
        Generate Study Plan
      </button>

      {result.length > 0 && (
        <div className="result-box">
          <h3>Your Study Plan</h3>
          <ul>
            {result.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
