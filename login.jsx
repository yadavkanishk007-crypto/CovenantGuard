import { useState } from "react";
import api from "../api/client";
import { setAuth } from "../auth/auth";

export default function Login({ onSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/login", { username, password });
      setAuth(res.data.access_token, res.data.role);
      onSuccess();
    } catch {
      setError("Invalid username or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-layout">
      <div className="auth-panel">
        <div className="auth-header">
          <h1>CovenantGuard+</h1>
          <p>Institutional Covenant Risk Monitoring</p>
        </div>

        <div className="auth-form">
          <label>Username</label>
          <input
            placeholder="Enter username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <div className="auth-error">{error}</div>}

          <button onClick={submit} disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </div>

        <div className="auth-footer">
          <span>© CovenantGuard + </span>
        </div>
      </div>
    </div>
  );
}
