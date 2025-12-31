import { logout, getRole } from "../auth/auth";

export default function Sidebar({ current, setCurrent }) {
  const role = getRole();

  const items = [
    { key: "dashboard", label: "Dashboard" },
    { key: "new", label: "New Evaluation" },
    { key: "history", label: "History" }
  ];

  if (role === "admin") {
    items.push({ key: "admin", label: "Admin KPIs" });
  }

  return (
    <aside className="app-sidebar">
      <h2>CovenantGuard+</h2>

      {items.map(item => (
        <button
          key={item.key}
          className={`nav-button ${current === item.key ? "active" : ""}`}
          onClick={() => setCurrent(item.key)}
        >
          {item.label}
        </button>
      ))}

      <div style={{ flex: 1 }} />

      <button
        onClick={() => {
          logout();
          window.location.reload();
        }}
        style={{
          background: "#dc2626",
          color: "white",
          padding: "12px",
          borderRadius: 10
        }}
      >
        Logout
      </button>
    </aside>
  );
}
