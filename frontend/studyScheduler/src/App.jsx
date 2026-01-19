import { useState } from "react";

function App() {
  const [subject, setSubject] = useState("");
  const [hours, setHours] = useState("");
  const [days, setDays] = useState("");
  const [result, setResult] = useState("");

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
    setResult(data.study_plan);
  };

  return (
    <div style={{ padding: "40px" }}>
      <h2>EduPlan-AI – Study Scheduler</h2>

      <input
        placeholder="Subject"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
      /><br /><br />

      <input
        placeholder="Hours per day"
        value={hours}
        onChange={(e) => setHours(e.target.value)}
      /><br /><br />

      <input
        placeholder="Exam days"
        value={days}
        onChange={(e) => setDays(e.target.value)}
      /><br /><br />

      <button onClick={generatePlan}>
        Generate Study Plan
      </button>

      <h3>Result:</h3>
      <p>{result}</p>
    </div>
  );
}

export default App;
