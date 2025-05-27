import React from "react";

function App() {
  const tasks = [
    {
      id: 1,
      location: "Germany",
      status: "Running",
      startTime: "2025-05-27 08:00",
      endTime: "",
      platform: "AWS",
      retries: 0
    },
    {
      id: 2,
      location: "USA",
      status: "Pending",
      startTime: "2025-05-27 09:00",
      endTime: "",
      platform: "On-prem",
      retries: 1
    },
    {
      id: 3,
      location: "UK",
      status: "Completed",
      startTime: "2025-05-27 10:00",
      endTime: "2025-05-27 10:30",
      platform: "Azure",
      retries: 0
    },
    {
      id: 4,
      location: "India",
      status: "Running",
      startTime: "2025-05-27 11:00",
      endTime: "",
      platform: "GCP",
      retries: 2
    },
    {
      id: 5,
      location: "Japan",
      status: "Failed",
      startTime: "2025-05-27 12:00",
      endTime: "2025-05-27 12:10",
      platform: "AWS",
      retries: 3
    }
  ];

  return (
    <div>
      <h2>Task Management System</h2>
      <table style={{ width: "100%" }} border="1">
        <thead>
          <tr>
            <th>Task ID</th>
            <th>Location</th>
            <th>Status</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Platform</th>
            <th>Retries</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map(task => (
            <tr key={task.id}>
              <td>{task.id}</td>
              <td>{task.location}</td>
              <td>{task.status}</td>
              <td>{task.startTime}</td>
              <td>{task.endTime}</td>
              <td>{task.platform}</td>
              <td>{task.retries}</td>
              <td>
                <button disabled={task.status === "Completed" || task.status === "Failed"}>
                  Cancel
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
