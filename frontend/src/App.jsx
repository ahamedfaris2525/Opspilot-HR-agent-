import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [employeeId, setEmployeeId] = useState("");
  const [employee, setEmployee] = useState(null);
  const [error, setError] = useState("");

  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  const login = async () => {
    const id = employeeId.trim().toUpperCase();

    if (!id) {
      setError("Please enter your Employee ID");
      return;
    }

    try {
      const response = await axios.get(
        `${API_URL}/employee/${id}`
      );

      setEmployee(response.data);
      setError("");
    } catch (err) {
      setEmployee(null);
      setError(
        err.response?.data?.detail || "Employee not found"
      );
    }
  };

  const logout = () => {
    setEmployee(null);
    setEmployeeId("");
    setMessages([]);
    setMessage("");
  };

  const sendMessage = async () => {
    if (!message.trim()) return;

    const currentMessage = message.trim();

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: currentMessage,
      },
    ]);

    setMessage("");

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: currentMessage,
        employee_id: employee.employee_code,
      });

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: response.data.response,
        },
      ]);
    } catch (err) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: "Sorry, something went wrong.",
        },
      ]);
    }
  };

  // LOGIN SCREEN
  if (!employee) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="logo">✦</div>

          <h1>OpsPilot AI</h1>

          <p className="subtitle">
            AI-powered HR Operations Assistant
          </p>

          <label>Employee ID</label>

          <input
            type="text"
            placeholder="e.g. EMP001"
            value={employeeId}
            onChange={(e) =>
              setEmployeeId(e.target.value)
            }
            onKeyDown={(e) => {
              if (e.key === "Enter") login();
            }}
          />

          <button className="login-button" onClick={login}>
            Login
          </button>

          {error && <p className="error">{error}</p>}

          <p className="demo-text">
            Demo authentication · Employee ID only
          </p>
        </div>
      </div>
    );
  }

  // DASHBOARD
  return (
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">✦</div>

          <div>
            <h2>OpsPilot AI</h2>
            <span>HR Operations Assistant</span>
          </div>
        </div>

        <div className="user-area">
          <div className="user-info">
            <strong>{employee.name}</strong>
            <span>{employee.employee_code}</span>
          </div>

          <button className="logout" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard">
        <section className="welcome">
          <p className="eyebrow">EMPLOYEE PORTAL</p>

          <h1>
            Welcome back, {employee.name} 👋
          </h1>

          <p>
            Your AI assistant for HR questions and operations.
          </p>
        </section>

        <section className="employee-card">
          <div>
            <span className="label">EMPLOYEE</span>
            <h3>{employee.name}</h3>
          </div>

          <div>
            <span className="label">EMPLOYEE ID</span>
            <p>{employee.employee_code}</p>
          </div>

          <div>
            <span className="label">DEPARTMENT</span>
            <p>{employee.department || "N/A"}</p>
          </div>

          <div>
            <span className="label">EMAIL</span>
            <p>{employee.email}</p>
          </div>
        </section>

        <section className="chat-card">
          <div className="chat-title">
            <div className="ai-icon">✦</div>

            <div>
              <h2>Ask OpsPilot</h2>
              <p>
                Ask about company policies, leave, and HR.
              </p>
            </div>
          </div>

          <div className="messages">
            {messages.length === 0 ? (
              <div className="empty-state">
                <h3>How can I help you?</h3>

                <p>Try one of these questions:</p>

                <div className="suggestions">
                  <button
                    onClick={() =>
                      setMessage(
                        "How many leaves do I have?"
                      )
                    }
                  >
                    🗓️ How many leaves do I have?
                  </button>

                  <button
                    onClick={() =>
                      setMessage(
                        "What is the annual leave policy?"
                      )
                    }
                  >
                    📋 What is the annual leave policy?
                  </button>

                  <button
                    onClick={() =>
                      setMessage(
                        "Can I work from home during probation?"
                      )
                    }
                  >
                    🏠 Can I work from home?
                  </button>
                </div>
              </div>
            ) : (
              messages.map((item, index) => (
                <div
                  key={index}
                  className={`message ${item.role}`}
                >
                  <div className="message-name">
                    {item.role === "user"
                      ? "You"
                      : "OpsPilot AI"}
                  </div>

                  <div className="message-content">
                    {item.content}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="chat-input">
            <input
              type="text"
              placeholder="Ask OpsPilot something..."
              value={message}
              onChange={(e) =>
                setMessage(e.target.value)
              }
              onKeyDown={(e) => {
                if (e.key === "Enter") sendMessage();
              }}
            />

            <button onClick={sendMessage}>
              Send
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;