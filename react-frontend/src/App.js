import React from "react";

function App() {
  const tasks = [
    { id: 1, location: "Germany", status: "Running" },
    { id: 2, location: "USA", status: "Pending" },
    { id: 3, location: "UK", status: "Completed" },
    { id: 4, location: "India", status: "Running" },
    { id: 5, location: "Japan", status: "Failed" }
  ];

  return (
    <div>
      <h2> Task Management System </h2>
      <table>
        <thead>
          <tr>
            <th>Task ID</th>
            <th>Location</th>
            <th>Status</th>
            <th>Cancel</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map(task => (
            <tr key={task.id}>
              <td>{task.id}</td>
              <td>{task.location}</td>
              <td>{task.status}</td>
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
