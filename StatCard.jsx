export default function StatCard({ label, value, accent }) {
  return (
    <div className="card">
      <p style={{ fontSize: 12, marginBottom: 6 }}>{label}</p>
      <h1 style={{ color: accent || "#0f172a" }}>{value}</h1>
    </div>
  );
}
