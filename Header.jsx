import { getRole } from "../auth/auth";

export default function Header({ title }) {
  const role = getRole();

  return (
    <header className="app-header">
      <h2>{title}</h2>
      <span style={{ fontSize: 13, color: "#64748b" }}>
        Role: {role}
      </span>
    </header>
  );
}
