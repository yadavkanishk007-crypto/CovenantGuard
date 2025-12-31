export default function KPI({ title, value, tone }) {
  const colors = {
    green: "var(--green)",
    amber: "var(--amber)",
    red: "var(--red)"
  };

  return (
    <div className="card">
      <p className="muted">{title}</p>
      <h1 style={{ margin: "8px 0", color: colors[tone] }}>
        {value}
      </h1>
    </div>
  );
}
