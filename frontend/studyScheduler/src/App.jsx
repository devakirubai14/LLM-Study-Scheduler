import { useState, useEffect } from "react";
import "./App.css";

function App() {
  // Existing states
  const [subjects, setSubjects] = useState("");
  const [hours, setHours] = useState("");
  const [days, setDays] = useState("");
  const [planId, setPlanId] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [progress, setProgress] = useState({});
  const [loading, setLoading] = useState(false);

  // NEW MODAL STATES
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [newDays, setNewDays] = useState("");
  const [newHours, setNewHours] = useState("");

  const fetchTasks = async (id) => {
    try {
      const response = await fetch(`http://localhost:5000/api/plan/${id}/tasks`);
      if (!response.ok) throw new Error("Fetch tasks failed");
      const data = await response.json();
      setTasks(data);
    } catch (error) {
      console.error("Fetch tasks error:", error);
    }
  };

  const fetchProgress = async (id) => {
    try {
      const response = await fetch(`http://localhost:5000/api/plan/${id}/progress`);
      if (!response.ok) throw new Error("Fetch progress failed");
      const data = await response.json();
      setProgress(data);
    } catch (error) {
      console.error("Fetch progress error:", error);
    }
  };

  const createPlan = async () => {
    try {
      setLoading(true);
      const subjectList = subjects.split(",").map(s => s.trim()).filter(Boolean);

      if (subjectList.length === 0) {
        alert("Please enter at least one subject");
        return;
      }

      if (!hours || !days || Number(hours) <= 0 || Number(days) <= 0) {
        alert("Please enter valid hours and days");
        return;
      }

      const response = await fetch("http://localhost:5000/api/plan/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subjects: subjectList,
          hours_per_day: Number(hours),
          exam_days: Number(days)
        })
      });

      if (!response.ok) throw new Error("Create plan failed");

      const data = await response.json();
      if (data.plan_id) {
        setPlanId(data.plan_id);
      } else {
        alert("Plan creation failed");
      }
    } catch (error) {
      console.error("Create plan error:", error);
      alert("Failed to create plan. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const markComplete = async (taskId) => {
    try {
      const response = await fetch("http://localhost:5000/api/task/complete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_id: taskId })
      });

      if (!response.ok) throw new Error("Mark complete failed");

      fetchTasks(planId);
      fetchProgress(planId);
    } catch (error) {
      console.error("Mark complete error:", error);
    }
  };

  const markMissed = async (taskId) => {
    try {
      const response = await fetch("http://localhost:5000/api/task/miss", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_id: taskId })
      });

      if (!response.ok) throw new Error("Mark missed failed");

      fetchTasks(planId);
      fetchProgress(planId);
    } catch (error) {
      console.error("Mark missed error:", error);
    }
  };

  // ENHANCED RESCHEDULE WITH MODAL
  const rescheduleTasks = async () => {
    if (!progress.missed || progress.missed === 0) {
      alert("No missed tasks to reschedule");
      return;
    }
    setShowRescheduleModal(true); // SHOW MODAL FIRST
  };

  const handleSmartReschedule = async () => {
    try {
      if (!newDays || !newHours || Number(newDays) <= 0 || Number(newHours) <= 0) {
        alert("Please enter valid days and hours");
        return;
      }

      // Call reschedule API
      const response = await fetch(
        `http://localhost:5000/api/plan/${planId}/reschedule`,
        { method: "POST" }
      );

      if (!response.ok) throw new Error("Reschedule failed");

      // Refetch data
      fetchTasks(planId);
      fetchProgress(planId);
      
      // Reset modal
      setShowRescheduleModal(false);
      setNewDays("");
      setNewHours("");
      
      alert("✅ Tasks rescheduled successfully!");
    } catch (error) {
      console.error("Reschedule error:", error);
      alert("Reschedule failed. Please try again.");
    }
  };

  const resetPlan = () => {
    setPlanId(null);
    setTasks([]);
    setProgress({});
    setSubjects("");
    setHours("");
    setDays("");
    setShowRescheduleModal(false);
    setNewDays("");
    setNewHours("");
  };

  useEffect(() => {
    if (planId) {
      fetchTasks(planId);
      fetchProgress(planId);
    }
  }, [planId]);

  return (
    <div className="container">
      <h1>EduPlan-AI</h1>
      <p className="subtitle">Smart Study Dashboard</p>

      {/* PLAN CREATION */}
      {!planId && (
        <div className="card">
          <h3>Create Study Plan</h3>
          <input
            placeholder="Subjects (Math, Physics, Chemistry)"
            value={subjects}
            onChange={(e) => setSubjects(e.target.value)}
          />
          <div className="input-row">
            <input
              type="number"
              min="1"
              max="24"
              placeholder="Hours per day"
              value={hours}
              onChange={(e) => setHours(e.target.value)}
            />
            <input
              type="number"
              min="1"
              max="365"
              placeholder="Days until exam"
              value={days}
              onChange={(e) => setDays(e.target.value)}
            />
          </div>
          <button onClick={createPlan} disabled={loading}>
            {loading ? "Creating..." : "Create Plan"}
          </button>
        </div>
      )}

      {/* DASHBOARD */}
      {planId && (
        <>
          <div className="action-bar">
            <button onClick={resetPlan} className="secondary-btn">
              New Plan
            </button>
            <button 
              onClick={rescheduleTasks} 
              className="secondary-btn"
              disabled={!(progress.missed > 0)}
            >
              Reschedule ({progress.missed || 0})
            </button>
          </div>

          <div className="card">
            <h3>📊 Progress</h3>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress.completion_percent || 0}%` }}
              />
            </div>
            <p className="progress-text">
              {progress.completed || 0}/{progress.total_tasks || 0} completed 
              ({(progress.completion_percent || 0).toFixed(1)}%)
            </p>
            <div className="stats">
              <span>✅ {progress.completed || 0} Done</span>
              <span>⏳ {progress.pending || 0} Pending</span>
              <span>❌ {progress.missed || 0} Missed</span>
            </div>
          </div>

          <div className="card">
            <h3>📋 Your Tasks</h3>
            {tasks.length === 0 ? (
              <p>Loading tasks...</p>
            ) : (
              <div className="tasks-list">
                {tasks.map((task) => (
                  <div key={task._id} className={`task-item ${task.status || 'pending'}`}>
                    <div className="task-info">
                      <strong>Day {task.day}</strong>
                      <span className="task-subject">{task.subject}</span>
                      {task.duration_display && (
                        <span className="task-duration">⏱️ {task.duration_display}</span>
                      )}
                    </div>

                    <div className="task-actions">
                      {task.status === 'pending' && (
                        <>
                          <button 
                            onClick={() => markComplete(task._id)}
                            className="complete-btn"
                          >
                            ✅ Done
                          </button>
                          <button 
                            onClick={() => markMissed(task._id)}
                            className="miss-btn"
                          >
                            ❌ Missed
                          </button>
                        </>
                      )}
                      {task.status === 'completed' && (
                        <span className="status-tag completed-tag">✅ Completed</span>
                      )}
                      {task.status === 'missed' && (
                        <span className="status-tag missed-tag">❌ Missed</span>
                      )}
                      {task.status === 'rescheduled' && (
                        <span className="status-tag rescheduled-tag">🔄 Rescheduled</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* SMART RESCHEDULE MODAL */}
          {showRescheduleModal && (
            <div className="modal-overlay">
              <div className="modal">
                <h3>🔄 Smart Reschedule</h3>
                <p>{progress.missed} missed tasks. Update your timeline:</p>
                <div className="input-row">
                  <input
                    type="number"
                    min="1"
                    max="365"
                    placeholder="Days left to exam"
                    value={newDays}
                    onChange={(e) => setNewDays(e.target.value)}
                  />
                  <input
                    type="number"
                    min="1"
                    max="24"
                    placeholder="Hours per day"
                    value={newHours}
                    onChange={(e) => setNewHours(e.target.value)}
                  />
                </div>
                <div className="modal-actions">
                  <button 
                    onClick={() => setShowRescheduleModal(false)}
                    className="secondary-btn"
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={handleSmartReschedule}
                    disabled={!newDays || !newHours}
                    className="complete-btn"
                  >
                    Reschedule Now
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
